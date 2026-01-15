"""HelloMe OAuth2 token management for Centric Dataplatform authentication.

This module provides a token manager that handles:
- Fetching bearer tokens from the HelloMe identity provider
- Caching tokens and tracking expiry
- Automatic re-authentication before token expires

Usage:
    manager = HelloMeTokenManager(
        token_endpoint="https://<tenant>.hellome.center/runtime/oauth2/token.idp",
        client_id="...",
        client_secret="...",
        username="...",
        password="...",
    )
    token = manager.get_token()  # Returns valid access token, refreshing if needed
"""

import logging
import threading
import time
from typing import Optional, Union

import requests

log = logging.getLogger("odata_to_staging.hellome_auth")


class HelloMeAuthError(Exception):
    """Raised when HelloMe authentication fails."""

    pass


class HelloMeTokenManager:
    """Manages OAuth2 token retrieval from HelloMe identity provider.

    Tokens are cached and automatically refreshed before expiry. Thread-safe.

    Attributes:
        token_endpoint: Full URL to HelloMe token endpoint
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        username: Resource owner username
        password: Resource owner password
        refresh_margin_seconds: Seconds before expiry to trigger refresh (default: 300)
        verify_ssl: Whether to verify SSL certificates (True), disable verification (False),
                    or path to a custom CA bundle (.pem file) for self-signed certificates
        request_timeout: HTTP request timeout in seconds (default: 30)
    """

    def __init__(
        self,
        token_endpoint: str,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
        refresh_margin_seconds: int = 300,
        verify_ssl: Union[bool, str] = True,
        request_timeout: float = 30.0,
    ) -> None:
        self.token_endpoint = token_endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.refresh_margin_seconds = refresh_margin_seconds
        self.verify_ssl = verify_ssl
        self.request_timeout = request_timeout

        # Cached token state (protected by lock)
        self._lock = threading.Lock()
        self._access_token: Optional[str] = None
        self._expires_at: float = 0.0  # Unix timestamp when token expires

    def get_token(self) -> str:
        """Get a valid access token, fetching a new one if necessary.

        Returns:
            A valid bearer access token string.

        Raises:
            HelloMeAuthError: If authentication fails.
        """
        with self._lock:
            now = time.time()
            # Check if we have a cached token that won't expire soon
            if self._access_token and now < (
                self._expires_at - self.refresh_margin_seconds
            ):
                return self._access_token

            # Need to fetch a new token
            log.info("Fetching new bearer token from HelloMe...")
            token_data = self._fetch_token()

            self._access_token = token_data["access_token"]
            # Calculate expiry time from expires_in (default 3600s = 1 hour)
            expires_in = token_data.get("expires_in", 3600)
            self._expires_at = now + expires_in

            log.info(
                "Obtained HelloMe token (expires in %d seconds, refresh margin %ds)",
                expires_in,
                self.refresh_margin_seconds,
            )
            return self._access_token

    def _fetch_token(self) -> dict:
        """POST to HelloMe token endpoint using resource owner password grant.

        Returns:
            Token response dict containing 'access_token', 'expires_in', etc.

        Raises:
            HelloMeAuthError: If the request fails or returns an error.
        """
        # Build form-urlencoded body per OAuth2 spec
        body = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password,
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        log.debug(
            "Requesting token from HelloMe endpoint: %s (username=%s, client_id=%s)",
            self.token_endpoint,
            self.username,
            self.client_id,
        )

        try:
            response = requests.post(
                self.token_endpoint,
                data=body,
                headers=headers,
                verify=self.verify_ssl,
                timeout=self.request_timeout,
            )
        except requests.ConnectionError as e:
            error_str = str(e)
            log.error(
                "Failed to connect to HelloMe token endpoint %s: %s",
                self.token_endpoint,
                e,
            )
            # Detect SSL certificate errors and provide specific guidance
            if "SSL" in error_str or "certificate" in error_str.lower():
                raise HelloMeAuthError(
                    f"SSL certificate verification failed for HelloMe token endpoint '{self.token_endpoint}': {e}. "
                    "Options to fix this:\n"
                    "  1. Set HELLOME_SSL_CA_CERT = /path/to/ca-bundle.pem in [hellome-auth] to use a custom CA certificate\n"
                    "  2. Set HELLOME_VERIFY_SSL = false in [hellome-auth] to disable verification (not recommended for production)"
                ) from e
            raise HelloMeAuthError(
                f"Failed to connect to HelloMe token endpoint '{self.token_endpoint}': {e}. "
                "Check network connectivity and verify HELLOME_TOKEN_ENDPOINT is correct."
            ) from e
        except requests.Timeout as e:
            log.error(
                "Timeout connecting to HelloMe token endpoint %s (timeout=%ss): %s",
                self.token_endpoint,
                self.request_timeout,
                e,
            )
            raise HelloMeAuthError(
                f"Timeout connecting to HelloMe token endpoint '{self.token_endpoint}' "
                f"after {self.request_timeout}s. The server may be slow or unreachable."
            ) from e
        except requests.RequestException as e:
            log.error("HelloMe token request failed: %s", e)
            raise HelloMeAuthError(f"HelloMe token request failed: {e}") from e

        log.debug("HelloMe response status: %d", response.status_code)

        # Check for HTTP errors with detailed OAuth2 error parsing
        if response.status_code == 401:
            # Try to extract error details from response body
            error_detail = self._parse_oauth_error(response)
            log.error(
                "HelloMe authentication failed (HTTP 401): %s",
                error_detail or "Invalid credentials",
            )
            raise HelloMeAuthError(
                f"HelloMe authentication failed (HTTP 401): {error_detail or 'Invalid credentials'}. "
                "Verify your HELLOME_CLIENT_ID, HELLOME_CLIENT_SECRET, HELLOME_USERNAME, and HELLOME_PASSWORD."
            )
        if response.status_code == 400:
            # OAuth2 error response - parse error and error_description
            error_detail = self._parse_oauth_error(response)
            log.error("HelloMe bad request (HTTP 400): %s", error_detail)
            raise HelloMeAuthError(
                f"HelloMe authentication failed (HTTP 400): {error_detail}. "
                "This typically indicates invalid grant_type, missing parameters, or incorrect credentials."
            )
        if response.status_code == 403:
            error_detail = self._parse_oauth_error(response)
            log.error("HelloMe access forbidden (HTTP 403): %s", error_detail)
            raise HelloMeAuthError(
                f"HelloMe access forbidden (HTTP 403): {error_detail}. "
                "The client may not be authorized to use the password grant type, or the user account may be disabled."
            )
        if response.status_code >= 500:
            log.error(
                "HelloMe server error (HTTP %d): %s",
                response.status_code,
                response.text[:300],
            )
            raise HelloMeAuthError(
                f"HelloMe server error (HTTP {response.status_code}): {response.text[:200]}. "
                "The HelloMe identity provider may be experiencing issues. Please try again later."
            )
        if not response.ok:
            error_detail = self._parse_oauth_error(response)
            log.error(
                "HelloMe token request failed (HTTP %d): %s",
                response.status_code,
                error_detail or response.text[:200],
            )
            raise HelloMeAuthError(
                f"HelloMe token request failed (HTTP {response.status_code}): "
                f"{error_detail or response.text[:200]}"
            )

        # Parse response
        try:
            token_data = response.json()
        except Exception as e:
            log.error(
                "HelloMe returned invalid JSON response: %s (body: %s)",
                e,
                response.text[:200],
            )
            raise HelloMeAuthError(
                f"HelloMe returned invalid JSON response: {e}. "
                f"Response body (truncated): {response.text[:200]}"
            ) from e

        if "access_token" not in token_data:
            log.error(
                "HelloMe response missing 'access_token' field; got keys: %s",
                list(token_data.keys()),
            )
            raise HelloMeAuthError(
                "HelloMe response missing 'access_token' field; "
                f"got keys: {list(token_data.keys())}. "
                "The token endpoint may not be a valid OAuth2 token endpoint."
            )

        return token_data

    def _parse_oauth_error(self, response: requests.Response) -> str:
        """Parse OAuth2 error response to extract error_description or error.

        OAuth2 error responses typically contain 'error' and 'error_description' fields.
        This method attempts to extract these for more informative error messages.

        Returns:
            Human-readable error string, or truncated response body as fallback.
        """
        try:
            error_data = response.json()
            error = error_data.get("error", "")
            error_desc = error_data.get("error_description", "")
            if error_desc:
                return f"{error}: {error_desc}" if error else error_desc
            if error:
                return error
        except Exception:
            pass
        # Fallback to raw response body
        return response.text[:200] if response.text else "No response body"

    def invalidate(self) -> None:
        """Invalidate the cached token, forcing a refresh on next get_token() call."""
        with self._lock:
            self._access_token = None
            self._expires_at = 0.0
            log.debug("HelloMe token cache invalidated")


__all__ = ["HelloMeTokenManager", "HelloMeAuthError"]
