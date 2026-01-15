"""Tests for HelloMe OAuth2 token management.

Uses mocked HTTP responses to verify token fetching, caching, and auto-refresh behavior.
"""

import threading
import time
from unittest.mock import MagicMock, patch

import pytest
import requests

from odata_to_staging.functions.hellome_auth import (
    HelloMeAuthError,
    HelloMeTokenManager,
)


class TestHelloMeTokenManager:
    """Tests for HelloMeTokenManager class."""

    @pytest.fixture
    def token_manager(self):
        """Create a token manager with test credentials."""
        return HelloMeTokenManager(
            token_endpoint="https://test.hellome.center/runtime/oauth2/token.idp",
            client_id="test_client_id",
            client_secret="test_client_secret",
            username="test_user",
            password="test_password",
            refresh_margin_seconds=60,
            verify_ssl=True,
            request_timeout=10.0,
        )

    def test_fetch_token_success(self, token_manager):
        """Successful token fetch returns access_token."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token_abc123",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

        with patch("requests.post", return_value=mock_response) as mock_post:
            token = token_manager.get_token()

            assert token == "test_token_abc123"
            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args
            assert call_kwargs.kwargs["data"]["grant_type"] == "password"
            assert call_kwargs.kwargs["data"]["client_id"] == "test_client_id"
            assert call_kwargs.kwargs["data"]["username"] == "test_user"

    def test_fetch_token_invalid_credentials_401(self, token_manager):
        """401 response raises clear error about invalid credentials."""
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.text = ""
        # Mock JSON parsing to raise exception (simulate non-JSON response)
        mock_response.json.side_effect = ValueError("No JSON")

        with patch("requests.post", return_value=mock_response):
            with pytest.raises(HelloMeAuthError) as exc_info:
                token_manager.get_token()

            assert "HTTP 401" in str(exc_info.value)
            assert "HELLOME_CLIENT_ID" in str(exc_info.value)

    def test_fetch_token_bad_request_400(self, token_manager):
        """400 response includes error description from OAuth response."""
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "invalid_grant",
            "error_description": "The username or password is incorrect",
        }

        with patch("requests.post", return_value=mock_response):
            with pytest.raises(HelloMeAuthError) as exc_info:
                token_manager.get_token()

            assert "username or password is incorrect" in str(exc_info.value)

    def test_fetch_token_server_error_500(self, token_manager):
        """500 response raises error with status code."""
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch("requests.post", return_value=mock_response):
            with pytest.raises(HelloMeAuthError) as exc_info:
                token_manager.get_token()

            assert "HTTP 500" in str(exc_info.value)

    def test_fetch_token_network_error(self, token_manager):
        """Network errors are wrapped in HelloMeAuthError."""
        with patch(
            "requests.post", side_effect=requests.ConnectionError("Connection refused")
        ):
            with pytest.raises(HelloMeAuthError) as exc_info:
                token_manager.get_token()

            assert "Failed to connect" in str(exc_info.value)
            assert "HELLOME_TOKEN_ENDPOINT" in str(exc_info.value)

    def test_fetch_token_ssl_certificate_error(self, token_manager):
        """SSL certificate errors provide specific guidance about HELLOME_SSL_CA_CERT."""
        ssl_error = requests.ConnectionError(
            "HTTPSConnectionPool(host='test.hellome.center', port=443): "
            "Max retries exceeded (Caused by SSLError(SSLCertVerificationError(1, "
            "'[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate')))"
        )
        with patch("requests.post", side_effect=ssl_error):
            with pytest.raises(HelloMeAuthError) as exc_info:
                token_manager.get_token()

            assert "SSL" in str(exc_info.value)
            assert "HELLOME_SSL_CA_CERT" in str(exc_info.value)
            assert "HELLOME_VERIFY_SSL" in str(exc_info.value)

    def test_fetch_token_timeout_error(self, token_manager):
        """Timeout errors are wrapped with clear message."""
        with patch(
            "requests.post", side_effect=requests.Timeout("Connection timed out")
        ):
            with pytest.raises(HelloMeAuthError) as exc_info:
                token_manager.get_token()

            assert "Timeout" in str(exc_info.value)
            assert "10" in str(exc_info.value)  # timeout value from fixture

    def test_fetch_token_forbidden_403(self, token_manager):
        """403 response raises clear error about authorization."""
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_response.json.side_effect = ValueError("No JSON")

        with patch("requests.post", return_value=mock_response):
            with pytest.raises(HelloMeAuthError) as exc_info:
                token_manager.get_token()

            assert "HTTP 403" in str(exc_info.value)
            assert "forbidden" in str(exc_info.value).lower()

    def test_fetch_token_missing_access_token(self, token_manager):
        """Response without access_token field raises error."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token_type": "Bearer"
        }  # Missing access_token

        with patch("requests.post", return_value=mock_response):
            with pytest.raises(HelloMeAuthError) as exc_info:
                token_manager.get_token()

            assert "missing 'access_token'" in str(exc_info.value)

    def test_fetch_token_invalid_json(self, token_manager):
        """Invalid JSON response raises error."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")

        with patch("requests.post", return_value=mock_response):
            with pytest.raises(HelloMeAuthError) as exc_info:
                token_manager.get_token()

            assert "invalid JSON" in str(exc_info.value)

    def test_token_caching(self, token_manager):
        """Token is cached and reused within expiry window."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "cached_token",
            "expires_in": 3600,
        }

        with patch("requests.post", return_value=mock_response) as mock_post:
            # First call fetches token
            token1 = token_manager.get_token()
            # Second call should use cache
            token2 = token_manager.get_token()
            # Third call should still use cache
            token3 = token_manager.get_token()

            assert token1 == token2 == token3 == "cached_token"
            # Only one HTTP request should have been made
            assert mock_post.call_count == 1

    def test_token_refresh_before_expiry(self, token_manager):
        """Token is refreshed when within refresh margin of expiry."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "token_v1",
            "expires_in": 3600,
        }

        with patch("requests.post", return_value=mock_response) as mock_post:
            # First call fetches token
            token1 = token_manager.get_token()
            assert token1 == "token_v1"
            assert mock_post.call_count == 1

            # Simulate time passing to within refresh margin
            # Token expires in 3600s, refresh margin is 60s, so at 3550s it should refresh
            token_manager._expires_at = (
                time.time() + 30
            )  # 30s until expiry (< 60s margin)

            # Update mock to return new token
            mock_response.json.return_value = {
                "access_token": "token_v2",
                "expires_in": 3600,
            }

            token2 = token_manager.get_token()
            assert token2 == "token_v2"
            assert mock_post.call_count == 2

    def test_token_not_refreshed_outside_margin(self, token_manager):
        """Token is NOT refreshed when outside refresh margin."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "stable_token",
            "expires_in": 3600,
        }

        with patch("requests.post", return_value=mock_response) as mock_post:
            token1 = token_manager.get_token()

            # Set expiry far in the future (well outside refresh margin)
            token_manager._expires_at = time.time() + 3600

            # This should NOT trigger a refresh
            token2 = token_manager.get_token()

            assert token1 == token2 == "stable_token"
            assert mock_post.call_count == 1

    def test_invalidate_clears_cache(self, token_manager):
        """invalidate() forces next get_token() to fetch fresh token."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "original_token",
            "expires_in": 3600,
        }

        with patch("requests.post", return_value=mock_response) as mock_post:
            token1 = token_manager.get_token()
            assert mock_post.call_count == 1

            token_manager.invalidate()

            # Update mock to return new token
            mock_response.json.return_value = {
                "access_token": "new_token",
                "expires_in": 3600,
            }

            token2 = token_manager.get_token()
            assert token2 == "new_token"
            assert mock_post.call_count == 2

    def test_thread_safety(self, token_manager):
        """Concurrent get_token() calls don't cause race conditions."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "thread_safe_token",
            "expires_in": 3600,
        }

        results = []
        errors = []

        def get_token_thread():
            try:
                token = token_manager.get_token()
                results.append(token)
            except Exception as e:
                errors.append(e)

        with patch("requests.post", return_value=mock_response) as mock_post:
            threads = [threading.Thread(target=get_token_thread) for _ in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

        assert len(errors) == 0
        assert all(t == "thread_safe_token" for t in results)
        # Due to locking, only one request should be made (others wait and use cached)
        assert mock_post.call_count == 1

    def test_default_expires_in(self, token_manager):
        """If expires_in is missing, defaults to 3600 seconds."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "no_expiry_token",
            # No expires_in field
        }

        with patch("requests.post", return_value=mock_response):
            with patch("time.time", return_value=1000.0):
                token_manager.get_token()
                # Should default to 3600s expiry
                assert token_manager._expires_at == 1000.0 + 3600


class TestHelloMeEngineLoaderIntegration:
    """Tests for HelloMe integration in engine_loaders.py."""

    def test_load_odata_client_hellome_missing_endpoint(self, monkeypatch):
        """HELLOME mode requires HELLOME_TOKEN_ENDPOINT."""
        from odata_to_staging.tests.test_odata_to_staging_fast import (
            _install_fake_pyodata,
        )

        _install_fake_pyodata(monkeypatch)

        class _Cfg:
            def __init__(self, mapping):
                self._mapping = mapping

            def has_option(self, section, option):
                return option in self._mapping.get(section, {})

            def get(self, section, option, fallback=None):
                return self._mapping.get(section, {}).get(option, fallback)

        cfg = _Cfg(
            {
                "odata-connection": {
                    "ODATA_URL": "https://example.test/odata",
                    "ODATA_AUTH_MODE": "HELLOME",
                },
                "hellome-auth": {
                    # Missing HELLOME_TOKEN_ENDPOINT
                    "HELLOME_CLIENT_ID": "client",
                    "HELLOME_CLIENT_SECRET": "secret",
                    "HELLOME_USERNAME": "user",
                    "HELLOME_PASSWORD": "pass",
                },
            }
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        with pytest.raises(ValueError, match="HELLOME_TOKEN_ENDPOINT.*HELLOME"):
            load_odata_client(cfg)

    def test_load_odata_client_hellome_missing_client_id(self, monkeypatch):
        """HELLOME mode requires HELLOME_CLIENT_ID."""
        from odata_to_staging.tests.test_odata_to_staging_fast import (
            _install_fake_pyodata,
        )

        _install_fake_pyodata(monkeypatch)

        class _Cfg:
            def __init__(self, mapping):
                self._mapping = mapping

            def has_option(self, section, option):
                return option in self._mapping.get(section, {})

            def get(self, section, option, fallback=None):
                return self._mapping.get(section, {}).get(option, fallback)

        cfg = _Cfg(
            {
                "odata-connection": {
                    "ODATA_URL": "https://example.test/odata",
                    "ODATA_AUTH_MODE": "HELLOME",
                },
                "hellome-auth": {
                    "HELLOME_TOKEN_ENDPOINT": "https://test.hellome.center/token",
                    # Missing HELLOME_CLIENT_ID
                    "HELLOME_CLIENT_SECRET": "secret",
                    "HELLOME_USERNAME": "user",
                    "HELLOME_PASSWORD": "pass",
                },
            }
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        with pytest.raises(ValueError, match="HELLOME_CLIENT_ID.*HELLOME"):
            load_odata_client(cfg)

    def test_load_odata_client_hellome_session_wrapping(self, monkeypatch):
        """HELLOME mode wraps session to inject bearer token."""
        from odata_to_staging.tests.test_odata_to_staging_fast import (
            _install_fake_pyodata,
        )

        _install_fake_pyodata(monkeypatch)

        # Track calls to the underlying request method
        request_calls = []

        def _track_request(method, url, **kwargs):
            request_calls.append({"method": method, "url": url, "kwargs": kwargs})
            return MagicMock()

        class _Session:
            def __init__(self):
                self.verify = True
                self.headers = {}
                # Use a bound method that we control
                self._underlying_request = _track_request

            def request(self, method, url, **kwargs):
                # This is the "original" that will be wrapped
                return self._underlying_request(method, url, **kwargs)

        mock_session = _Session()
        monkeypatch.setattr(
            "odata_to_staging.functions.engine_loaders.requests.Session",
            lambda: mock_session,
        )

        # Mock the token manager to return a known token
        mock_token_manager = MagicMock()
        mock_token_manager.get_token.return_value = "dynamic_test_token"
        monkeypatch.setattr(
            "odata_to_staging.functions.hellome_auth.HelloMeTokenManager",
            lambda **kwargs: mock_token_manager,
        )

        class _Cfg:
            def __init__(self, mapping):
                self._mapping = mapping

            def has_option(self, section, option):
                return option in self._mapping.get(section, {})

            def get(self, section, option, fallback=None):
                return self._mapping.get(section, {}).get(option, fallback)

        cfg = _Cfg(
            {
                "odata-connection": {
                    "ODATA_URL": "https://example.test/odata",
                    "ODATA_AUTH_MODE": "HELLOME",
                },
                "hellome-auth": {
                    "HELLOME_TOKEN_ENDPOINT": "https://test.hellome.center/token",
                    "HELLOME_CLIENT_ID": "client",
                    "HELLOME_CLIENT_SECRET": "secret",
                    "HELLOME_USERNAME": "user",
                    "HELLOME_PASSWORD": "pass",
                },
            }
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        load_odata_client(cfg)

        # After load_odata_client, mock_session.request has been wrapped
        # Call the wrapped version
        mock_session.request("GET", "https://example.test/odata/Employees")

        # Token manager should have been called
        mock_token_manager.get_token.assert_called()

        # The tracking function should have been called with Authorization header
        assert len(request_calls) == 1
        assert request_calls[0]["method"] == "GET"
        assert request_calls[0]["url"] == "https://example.test/odata/Employees"
        assert (
            request_calls[0]["kwargs"]["headers"]["Authorization"]
            == "Bearer dynamic_test_token"
        )


class TestHelloMeSSLConfiguration:
    """Tests for HelloMe-specific SSL configuration options."""

    def _install_fake_pyodata(self, monkeypatch):
        """Install fake pyodata module for testing."""
        from odata_to_staging.tests.test_odata_to_staging_fast import (
            _install_fake_pyodata,
        )

        return _install_fake_pyodata(monkeypatch)

    def _make_cfg(self, odata_connection=None, hellome_auth=None):
        """Create a config object with given sections."""

        class _Cfg:
            def __init__(self, mapping):
                self._mapping = mapping

            def has_option(self, section, option):
                return option in self._mapping.get(section, {})

            def get(self, section, option, fallback=None):
                return self._mapping.get(section, {}).get(option, fallback)

        base_odata = {
            "ODATA_URL": "https://example.test/odata",
            "ODATA_AUTH_MODE": "HELLOME",
        }
        base_hellome = {
            "HELLOME_TOKEN_ENDPOINT": "https://test.hellome.center/token",
            "HELLOME_CLIENT_ID": "client",
            "HELLOME_CLIENT_SECRET": "secret",
            "HELLOME_USERNAME": "user",
            "HELLOME_PASSWORD": "pass",
        }
        if odata_connection:
            base_odata.update(odata_connection)
        if hellome_auth:
            base_hellome.update(hellome_auth)

        return _Cfg(
            {
                "odata-connection": base_odata,
                "hellome-auth": base_hellome,
            }
        )

    def test_hellome_verify_ssl_false_disables_verification(
        self, monkeypatch, tmp_path
    ):
        """HELLOME_VERIFY_SSL=false should disable SSL verification for HelloMe."""
        self._install_fake_pyodata(monkeypatch)

        # Track what verify_ssl value is passed to HelloMeTokenManager
        captured_kwargs = {}

        class MockTokenManager:
            def __init__(self, **kwargs):
                captured_kwargs.update(kwargs)

            def get_token(self):
                return "test_token"

        # Patch in the hellome_auth module where it's imported from
        monkeypatch.setattr(
            "odata_to_staging.functions.hellome_auth.HelloMeTokenManager",
            MockTokenManager,
        )

        class _Session:
            def __init__(self):
                self.verify = True
                self.headers = {}

            def request(self, method, url, **kwargs):
                return MagicMock()

        monkeypatch.setattr(
            "odata_to_staging.functions.engine_loaders.requests.Session",
            lambda: _Session(),
        )

        cfg = self._make_cfg(
            odata_connection={"ODATA_VERIFY_SSL": "true"},  # OData has SSL enabled
            hellome_auth={"HELLOME_VERIFY_SSL": "false"},  # But HelloMe disables it
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        load_odata_client(cfg)

        # HelloMe should have verify_ssl=False
        assert captured_kwargs.get("verify_ssl") is False

    def test_hellome_verify_ssl_true_enables_verification(self, monkeypatch):
        """HELLOME_VERIFY_SSL=true should enable SSL verification for HelloMe."""
        self._install_fake_pyodata(monkeypatch)

        captured_kwargs = {}

        class MockTokenManager:
            def __init__(self, **kwargs):
                captured_kwargs.update(kwargs)

            def get_token(self):
                return "test_token"

        monkeypatch.setattr(
            "odata_to_staging.functions.hellome_auth.HelloMeTokenManager",
            MockTokenManager,
        )

        class _Session:
            def __init__(self):
                self.verify = True
                self.headers = {}

            def request(self, method, url, **kwargs):
                return MagicMock()

        monkeypatch.setattr(
            "odata_to_staging.functions.engine_loaders.requests.Session",
            lambda: _Session(),
        )

        cfg = self._make_cfg(
            odata_connection={"ODATA_VERIFY_SSL": "false"},  # OData has SSL disabled
            hellome_auth={"HELLOME_VERIFY_SSL": "true"},  # But HelloMe enables it
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        load_odata_client(cfg)

        # HelloMe should have verify_ssl=True
        assert captured_kwargs.get("verify_ssl") is True

    def test_hellome_ssl_ca_cert_used_when_set(self, monkeypatch, tmp_path):
        """HELLOME_SSL_CA_CERT should be used for HelloMe SSL verification."""
        self._install_fake_pyodata(monkeypatch)

        # Create a temporary cert file
        cert_file = tmp_path / "hellome_ca.pem"
        cert_file.write_text(
            "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        )

        captured_kwargs = {}

        class MockTokenManager:
            def __init__(self, **kwargs):
                captured_kwargs.update(kwargs)

            def get_token(self):
                return "test_token"

        monkeypatch.setattr(
            "odata_to_staging.functions.hellome_auth.HelloMeTokenManager",
            MockTokenManager,
        )

        class _Session:
            def __init__(self):
                self.verify = True
                self.headers = {}

            def request(self, method, url, **kwargs):
                return MagicMock()

        monkeypatch.setattr(
            "odata_to_staging.functions.engine_loaders.requests.Session",
            lambda: _Session(),
        )

        cfg = self._make_cfg(
            hellome_auth={"HELLOME_SSL_CA_CERT": str(cert_file)},
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        load_odata_client(cfg)

        # HelloMe should have verify_ssl set to the cert path
        assert captured_kwargs.get("verify_ssl") == str(cert_file)

    def test_hellome_ssl_ca_cert_takes_priority_over_verify_ssl(
        self, monkeypatch, tmp_path
    ):
        """HELLOME_SSL_CA_CERT should take priority over HELLOME_VERIFY_SSL."""
        self._install_fake_pyodata(monkeypatch)

        # Create a temporary cert file
        cert_file = tmp_path / "hellome_ca.pem"
        cert_file.write_text(
            "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        )

        captured_kwargs = {}

        class MockTokenManager:
            def __init__(self, **kwargs):
                captured_kwargs.update(kwargs)

            def get_token(self):
                return "test_token"

        monkeypatch.setattr(
            "odata_to_staging.functions.hellome_auth.HelloMeTokenManager",
            MockTokenManager,
        )

        class _Session:
            def __init__(self):
                self.verify = True
                self.headers = {}

            def request(self, method, url, **kwargs):
                return MagicMock()

        monkeypatch.setattr(
            "odata_to_staging.functions.engine_loaders.requests.Session",
            lambda: _Session(),
        )

        cfg = self._make_cfg(
            hellome_auth={
                "HELLOME_VERIFY_SSL": "false",  # This should be ignored
                "HELLOME_SSL_CA_CERT": str(cert_file),  # This takes priority
            },
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        load_odata_client(cfg)

        # HelloMe should have verify_ssl set to the cert path, not False
        assert captured_kwargs.get("verify_ssl") == str(cert_file)

    def test_hellome_falls_back_to_odata_ssl_settings(self, monkeypatch, tmp_path):
        """Without HELLOME SSL settings, should fall back to ODATA settings."""
        self._install_fake_pyodata(monkeypatch)

        # Create a temporary cert file for OData
        cert_file = tmp_path / "odata_ca.pem"
        cert_file.write_text(
            "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        )

        captured_kwargs = {}

        class MockTokenManager:
            def __init__(self, **kwargs):
                captured_kwargs.update(kwargs)

            def get_token(self):
                return "test_token"

        monkeypatch.setattr(
            "odata_to_staging.functions.hellome_auth.HelloMeTokenManager",
            MockTokenManager,
        )

        class _Session:
            def __init__(self):
                self.verify = True
                self.headers = {}

            def request(self, method, url, **kwargs):
                return MagicMock()

        monkeypatch.setattr(
            "odata_to_staging.functions.engine_loaders.requests.Session",
            lambda: _Session(),
        )

        cfg = self._make_cfg(
            odata_connection={"ODATA_SSL_CA_CERT": str(cert_file)},
            # No HELLOME SSL settings - should fall back to ODATA
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        load_odata_client(cfg)

        # HelloMe should have verify_ssl set to the ODATA cert path
        assert captured_kwargs.get("verify_ssl") == str(cert_file)

    def test_hellome_falls_back_to_odata_verify_ssl_false(self, monkeypatch):
        """Without HELLOME SSL settings, should fall back to ODATA_VERIFY_SSL=false."""
        self._install_fake_pyodata(monkeypatch)

        captured_kwargs = {}

        class MockTokenManager:
            def __init__(self, **kwargs):
                captured_kwargs.update(kwargs)

            def get_token(self):
                return "test_token"

        monkeypatch.setattr(
            "odata_to_staging.functions.hellome_auth.HelloMeTokenManager",
            MockTokenManager,
        )

        class _Session:
            def __init__(self):
                self.verify = True
                self.headers = {}

            def request(self, method, url, **kwargs):
                return MagicMock()

        monkeypatch.setattr(
            "odata_to_staging.functions.engine_loaders.requests.Session",
            lambda: _Session(),
        )

        cfg = self._make_cfg(
            odata_connection={"ODATA_VERIFY_SSL": "false"},
            # No HELLOME SSL settings - should fall back to ODATA
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        load_odata_client(cfg)

        # HelloMe should have verify_ssl=False (from ODATA)
        assert captured_kwargs.get("verify_ssl") is False

    def test_hellome_ssl_ca_cert_nonexistent_file_raises(self, monkeypatch):
        """HELLOME_SSL_CA_CERT with nonexistent file should raise ValueError."""
        self._install_fake_pyodata(monkeypatch)

        class _Session:
            def __init__(self):
                self.verify = True
                self.headers = {}

        monkeypatch.setattr(
            "odata_to_staging.functions.engine_loaders.requests.Session",
            lambda: _Session(),
        )

        cfg = self._make_cfg(
            hellome_auth={"HELLOME_SSL_CA_CERT": "/nonexistent/path/to/cert.pem"},
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        with pytest.raises(ValueError, match="HELLOME_SSL_CA_CERT.*does not exist"):
            load_odata_client(cfg)
