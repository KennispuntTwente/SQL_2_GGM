import json
import logging
from typing import Any, Dict, Optional, Union, cast

import requests
from requests.adapters import HTTPAdapter

try:
    # urllib3 is a transitive dep of requests; Retry offers robust backoff
    from urllib3.util.retry import Retry  # type: ignore
except Exception:  # pragma: no cover - fallback if urllib3 API differs
    Retry = None  # type: ignore

from utils.config.get_config_value import get_config_value


log = logging.getLogger("odata_to_staging.engine_loaders")


def _require_non_empty_secret(
    value: Optional[str], setting: str, auth_mode: str
) -> str:
    """Ensure required auth inputs are present so we fail fast with a clear error."""
    if value is None:
        raise ValueError(f"{setting} must be set when ODATA_AUTH_MODE={auth_mode}")
    if isinstance(value, str) and value.strip() == "":
        raise ValueError(f"{setting} cannot be blank when ODATA_AUTH_MODE={auth_mode}")
    return value


def load_odata_client(cfg: Any):
    """Create and return a pyodata Client based on [odata-source] settings.

    Supports NONE, BASIC, BEARER auth modes; optional custom headers; SSL verify toggle.
    """
    try:
        import pyodata  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "pyodata is required for odata_to_staging; please install it in the environment"
        ) from e

    service_url_opt = cast(
        Optional[str],
        get_config_value(
            "ODATA_URL",
            section="odata-connection",
            cfg_parser=cfg,
            default=None,
            cast_type=str,
            allow_none_if_cast_fails=True,
        )
        or get_config_value(
            "ODATA_URL",
            section="odata-source",
            cfg_parser=cfg,
            default=None,
            cast_type=str,
            allow_none_if_cast_fails=True,
        ),
    )
    if not service_url_opt:
        raise ValueError(
            "ODATA_URL must be set in [odata-connection] (or legacy [odata-source])"
        )
    service_url = cast(str, service_url_opt)

    auth_mode = cast(
        str,
        get_config_value(
            "ODATA_AUTH_MODE",
            section="odata-connection",
            cfg_parser=cfg,
            default=None,
            cast_type=str,
            allow_none_if_cast_fails=True,
        )
        or get_config_value(
            "ODATA_AUTH_MODE",
            section="odata-source",
            cfg_parser=cfg,
            default="NONE",
            cast_type=str,
        ),
    ).upper()

    # Check ODATA_VERIFY_SSL from both sections - use explicit None check to handle False correctly
    verify_ssl_opt = cast(
        Optional[bool],
        get_config_value(
            "ODATA_VERIFY_SSL",
            section="odata-connection",
            cfg_parser=cfg,
            default=None,
            cast_type=bool,
            allow_none_if_cast_fails=True,
        ),
    )
    if verify_ssl_opt is None:
        verify_ssl_opt = cast(
            Optional[bool],
            get_config_value(
                "ODATA_VERIFY_SSL",
                section="odata-source",
                cfg_parser=cfg,
                default=None,
                cast_type=bool,
                allow_none_if_cast_fails=True,
            ),
        )
    verify_ssl_bool = True if verify_ssl_opt is None else verify_ssl_opt

    # Optional: custom CA certificate bundle for SSL verification
    # If set, this path is used instead of the default system CA bundle
    ssl_ca_cert_path = cast(
        Optional[str],
        get_config_value(
            "ODATA_SSL_CA_CERT",
            section="odata-connection",
            cfg_parser=cfg,
            default=None,
            cast_type=str,
            allow_none_if_cast_fails=True,
        )
        or get_config_value(
            "ODATA_SSL_CA_CERT",
            section="odata-source",
            cfg_parser=cfg,
            default=None,
            cast_type=str,
            allow_none_if_cast_fails=True,
        ),
    )

    # Determine verify_ssl: can be True, False, or a path to a CA bundle
    if ssl_ca_cert_path:
        import os

        if not os.path.isfile(ssl_ca_cert_path):
            raise ValueError(
                f"ODATA_SSL_CA_CERT path does not exist or is not a file: {ssl_ca_cert_path}"
            )
        verify_ssl: Union[bool, str] = ssl_ca_cert_path
        log.info(
            "Using custom CA certificate for SSL verification: %s", ssl_ca_cert_path
        )
    else:
        verify_ssl = verify_ssl_bool

    headers_raw = cast(
        Optional[str],
        get_config_value(
            "ODATA_HEADERS",
            section="odata-connection",
            cfg_parser=cfg,
            default=None,
            cast_type=str,
            allow_none_if_cast_fails=True,
        )
        or get_config_value(
            "ODATA_HEADERS",
            section="odata-source",
            cfg_parser=cfg,
            default=None,
            cast_type=str,
            allow_none_if_cast_fails=True,
        ),
    )
    headers: Dict[str, str] = {}
    if headers_raw:
        try:
            parsed = json.loads(headers_raw)
            if not isinstance(parsed, dict):
                raise ValueError("ODATA_HEADERS must be a JSON object")
            headers = {str(k): str(v) for k, v in parsed.items()}
        except Exception as e:
            raise ValueError(f"Failed to parse ODATA_HEADERS as JSON: {e}") from e

    sess = requests.Session()
    sess.verify = verify_ssl
    if headers:
        sess.headers.update(headers)

    if auth_mode == "BASIC":
        username_opt = cast(
            Optional[str],
            get_config_value(
                "ODATA_USERNAME",
                section="odata-connection",
                cfg_parser=cfg,
                default=None,
                cast_type=str,
                allow_none_if_cast_fails=True,
            )
            or get_config_value(
                "ODATA_USERNAME",
                section="odata-source",
                cfg_parser=cfg,
                default=None,
                cast_type=str,
                allow_none_if_cast_fails=True,
            ),
        )
        password_opt = cast(
            Optional[str],
            (
                get_config_value(
                    "ODATA_PASSWORD",
                    section="odata-connection",
                    cfg_parser=cfg,
                    print_value=False,
                    ask_in_command_line=get_config_value(
                        "ASK_PASSWORD_IN_CLI",
                        section="settings",
                        cfg_parser=cfg,
                        default=False,
                        cast_type=bool,
                    ),
                    default=None,
                    cast_type=str,
                    allow_none_if_cast_fails=True,
                )
                or get_config_value(
                    "ODATA_PASSWORD",
                    section="odata-source",
                    cfg_parser=cfg,
                    print_value=False,
                    ask_in_command_line=get_config_value(
                        "ASK_PASSWORD_IN_CLI",
                        section="settings",
                        cfg_parser=cfg,
                        default=False,
                        cast_type=bool,
                    ),
                    default=None,
                    cast_type=str,
                    allow_none_if_cast_fails=True,
                )
            ),
        )
        username = _require_non_empty_secret(username_opt, "ODATA_USERNAME", auth_mode)
        password = _require_non_empty_secret(password_opt, "ODATA_PASSWORD", auth_mode)
        sess.auth = (username, password)
    elif auth_mode == "BEARER":
        token_opt = cast(
            Optional[str],
            get_config_value(
                "ODATA_BEARER_TOKEN",
                section="odata-connection",
                cfg_parser=cfg,
                print_value=False,
                default=None,
                cast_type=str,
                allow_none_if_cast_fails=True,
            )
            or get_config_value(
                "ODATA_BEARER_TOKEN",
                section="odata-source",
                cfg_parser=cfg,
                print_value=False,
                default=None,
                cast_type=str,
                allow_none_if_cast_fails=True,
            ),
        )
        token = _require_non_empty_secret(token_opt, "ODATA_BEARER_TOKEN", auth_mode)
        sess.headers.setdefault("Authorization", f"Bearer {token}")
    elif auth_mode == "HELLOME":
        # Dynamic token retrieval from HelloMe identity provider
        from odata_to_staging.functions.hellome_auth import HelloMeTokenManager

        def _get_hellome_cfg(key: str, print_val: bool = True) -> Optional[str]:
            return cast(
                Optional[str],
                get_config_value(
                    key,
                    section="hellome-auth",
                    cfg_parser=cfg,
                    print_value=print_val,
                    default=None,
                    cast_type=str,
                    allow_none_if_cast_fails=True,
                ),
            )

        token_endpoint = _require_non_empty_secret(
            _get_hellome_cfg("HELLOME_TOKEN_ENDPOINT"),
            "HELLOME_TOKEN_ENDPOINT",
            auth_mode,
        )
        client_id = _require_non_empty_secret(
            _get_hellome_cfg("HELLOME_CLIENT_ID"),
            "HELLOME_CLIENT_ID",
            auth_mode,
        )
        client_secret = _require_non_empty_secret(
            _get_hellome_cfg("HELLOME_CLIENT_SECRET", print_val=False),
            "HELLOME_CLIENT_SECRET",
            auth_mode,
        )
        hm_username = _require_non_empty_secret(
            _get_hellome_cfg("HELLOME_USERNAME"),
            "HELLOME_USERNAME",
            auth_mode,
        )
        hm_password = _require_non_empty_secret(
            _get_hellome_cfg("HELLOME_PASSWORD", print_val=False),
            "HELLOME_PASSWORD",
            auth_mode,
        )
        refresh_margin = cast(
            int,
            get_config_value(
                "HELLOME_REFRESH_MARGIN_SECONDS",
                section="hellome-auth",
                cfg_parser=cfg,
                default=300,
                cast_type=int,
            ),
        )

        # HelloMe can have its own SSL CA cert, separate from OData
        hellome_ssl_ca_cert = cast(
            Optional[str],
            get_config_value(
                "HELLOME_SSL_CA_CERT",
                section="hellome-auth",
                cfg_parser=cfg,
                default=None,
                cast_type=str,
                allow_none_if_cast_fails=True,
            ),
        )

        # HelloMe can have its own SSL verify setting, separate from OData
        hellome_verify_ssl_opt = cast(
            Optional[bool],
            get_config_value(
                "HELLOME_VERIFY_SSL",
                section="hellome-auth",
                cfg_parser=cfg,
                default=None,
                cast_type=bool,
                allow_none_if_cast_fails=True,
            ),
        )

        # Determine verify_ssl for HelloMe:
        # 1. If HELLOME_SSL_CA_CERT is set, use the cert path
        # 2. Else if HELLOME_VERIFY_SSL is explicitly set, use that
        # 3. Else fall back to ODATA_SSL_CA_CERT / ODATA_VERIFY_SSL
        if hellome_ssl_ca_cert:
            import os

            if not os.path.isfile(hellome_ssl_ca_cert):
                raise ValueError(
                    f"HELLOME_SSL_CA_CERT path does not exist or is not a file: {hellome_ssl_ca_cert}"
                )
            hellome_verify_ssl: Union[bool, str] = hellome_ssl_ca_cert
            log.info(
                "Using custom CA certificate for HelloMe authentication: %s",
                hellome_ssl_ca_cert,
            )
        elif hellome_verify_ssl_opt is not None:
            hellome_verify_ssl = hellome_verify_ssl_opt
            if not hellome_verify_ssl:
                log.warning(
                    "SSL verification disabled for HelloMe endpoint (HELLOME_VERIFY_SSL=false)"
                )
        else:
            hellome_verify_ssl = verify_ssl

        token_manager = HelloMeTokenManager(
            token_endpoint=token_endpoint,
            client_id=client_id,
            client_secret=client_secret,
            username=hm_username,
            password=hm_password,
            refresh_margin_seconds=refresh_margin,
            verify_ssl=hellome_verify_ssl,
        )

        # Wrap session to inject fresh token on each request
        _orig_request = sess.request

        def _request_with_hellome_token(method, url, **kwargs):
            token = token_manager.get_token()
            headers = kwargs.get("headers", {})
            if headers is None:
                headers = {}
            headers["Authorization"] = f"Bearer {token}"
            kwargs["headers"] = headers
            return _orig_request(method, url, **kwargs)

        sess.request = _request_with_hellome_token  # type: ignore[method-assign]
        log.info(
            "Configured HelloMe dynamic token auth (endpoint=%s, refresh_margin=%ds)",
            token_endpoint,
            refresh_margin,
        )
    elif auth_mode == "NONE":
        pass
    else:
        raise ValueError(
            "ODATA_AUTH_MODE must be one of: NONE | BASIC | BEARER | HELLOME"
        )

    log.info("Initialized requests.Session for OData (verify_ssl=%s)", verify_ssl)

    # Optional: configure HTTP retries and a default timeout to avoid hangs
    # Prefer values from [settings], fallback to [odata-source] for backward compatibility
    def _cfg_with_fallback(key: str, default: Any, *, cast_type):
        val = get_config_value(
            key,
            section="settings",
            cfg_parser=cfg,
            default=None,
            cast_type=cast_type,
            allow_none_if_cast_fails=True,
        )
        if val is None:
            val = get_config_value(
                key,
                section="odata-source",
                cfg_parser=cfg,
                default=default,
                cast_type=cast_type,
            )
        return val

    timeout_seconds = cast(
        float,
        get_config_value(
            "ODATA_REQUEST_TIMEOUT_SECONDS",
            section="odata-network",
            cfg_parser=cfg,
            default=None,
            cast_type=float,
            allow_none_if_cast_fails=True,
        )
        or get_config_value(
            "ODATA_REQUEST_TIMEOUT_SECONDS",
            section="settings",
            cfg_parser=cfg,
            default=None,
            cast_type=float,
            allow_none_if_cast_fails=True,
        )
        or get_config_value(
            "ODATA_REQUEST_TIMEOUT_SECONDS",
            section="odata-source",
            cfg_parser=cfg,
            default=30.0,
            cast_type=float,
        ),
    )
    max_retries = cast(
        int,
        get_config_value(
            "ODATA_MAX_RETRIES",
            section="odata-network",
            cfg_parser=cfg,
            default=None,
            cast_type=int,
            allow_none_if_cast_fails=True,
        )
        or get_config_value(
            "ODATA_MAX_RETRIES",
            section="settings",
            cfg_parser=cfg,
            default=None,
            cast_type=int,
            allow_none_if_cast_fails=True,
        )
        or get_config_value(
            "ODATA_MAX_RETRIES",
            section="odata-source",
            cfg_parser=cfg,
            default=3,
            cast_type=int,
        ),
    )
    backoff = cast(
        float,
        get_config_value(
            "ODATA_RETRY_BACKOFF_SECONDS",
            section="odata-network",
            cfg_parser=cfg,
            default=None,
            cast_type=float,
            allow_none_if_cast_fails=True,
        )
        or get_config_value(
            "ODATA_RETRY_BACKOFF_SECONDS",
            section="settings",
            cfg_parser=cfg,
            default=None,
            cast_type=float,
            allow_none_if_cast_fails=True,
        )
        or get_config_value(
            "ODATA_RETRY_BACKOFF_SECONDS",
            section="odata-source",
            cfg_parser=cfg,
            default=1.0,
            cast_type=float,
        ),
    )
    status_forcelist_raw = cast(
        str,
        get_config_value(
            "ODATA_RETRY_STATUS_FORCELIST",
            section="odata-network",
            cfg_parser=cfg,
            default=None,
            cast_type=str,
            allow_none_if_cast_fails=True,
        )
        or get_config_value(
            "ODATA_RETRY_STATUS_FORCELIST",
            section="settings",
            cfg_parser=cfg,
            default=None,
            cast_type=str,
            allow_none_if_cast_fails=True,
        )
        or get_config_value(
            "ODATA_RETRY_STATUS_FORCELIST",
            section="odata-source",
            cfg_parser=cfg,
            default="429,500,502,503,504",
            cast_type=str,
        ),
    )
    try:
        status_forcelist = {
            int(s.strip()) for s in status_forcelist_raw.split(",") if s.strip()
        }
    except Exception:
        status_forcelist = {429, 500, 502, 503, 504}

    if Retry is not None and max_retries > 0:
        retry = Retry(
            total=max_retries,
            read=max_retries,
            connect=max_retries,
            status=max_retries,
            backoff_factor=backoff,
            status_forcelist=tuple(sorted(status_forcelist)),
            allowed_methods=(
                frozenset(
                    {
                        "GET",
                        "POST",
                        "PUT",
                        "PATCH",
                        "DELETE",
                        "HEAD",
                        "OPTIONS",
                    }
                )
            ),
            raise_on_status=False,
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry)
        if hasattr(sess, "mount"):
            try:
                sess.mount("http://", adapter)
                sess.mount("https://", adapter)
                log.info(
                    "Configured HTTP retries for OData (max_retries=%s, backoff=%s, status=%s)",
                    max_retries,
                    backoff,
                    sorted(status_forcelist),
                )
            except Exception:
                # Be defensive with custom session implementations/mocks
                log.info(
                    "Session does not support mounting adapters; skipping retries setup"
                )
        else:
            log.info("Session has no 'mount' attribute; skipping retries setup")
    else:
        log.info("HTTP retries not configured (urllib3 Retry unavailable or disabled)")

    # Ensure a default timeout is applied to all requests made by this session.
    # pyodata calls requests via this session without a timeout by default.
    if hasattr(sess, "request"):
        # Use a different variable name to avoid shadowing _orig_request from HELLOME wrapper
        _timeout_orig_request = sess.request  # type: ignore[attr-defined]

        def _request_with_timeout(method, url, **kwargs):  # type: ignore[no-redef]
            kwargs.setdefault("timeout", timeout_seconds)
            return _timeout_orig_request(method, url, **kwargs)

        try:
            sess.request = _request_with_timeout  # type: ignore[assignment]
            log.info(
                "Set default request timeout for OData session: %ss", timeout_seconds
            )
        except Exception:
            log.info("Session is not assignable; skipping default-timeout wrapper")
    else:
        log.info("Session has no 'request' attribute; skipping default-timeout wrapper")

    # Retain nulls to distinguish between missing values and default values
    retain_null = cast(
        bool,
        get_config_value(
            "ODATA_RETAIN_NULL",
            section="odata-export",
            cfg_parser=cfg,
            default=None,
            cast_type=bool,
            allow_none_if_cast_fails=True,
        )
        or get_config_value(
            "ODATA_RETAIN_NULL",
            section="odata-source",
            cfg_parser=cfg,
            default=True,
            cast_type=bool,
        ),
    )

    client_config = None
    if retain_null:
        try:
            # pyodata.v2 is the most common, using it as a default.
            # The import is here to avoid breaking if pyodata is not installed
            import pyodata.v2.model

            client_config = pyodata.v2.model.Config(retain_null=True)
            log.info("OData client configured with retain_null=True.")
        except (AttributeError, ImportError):
            log.warning(
                "Could not find pyodata.v2.model.Config, proceeding without it. "
                "This might be expected for OData V4 services."
            )

    if client_config:
        return pyodata.Client(service_url, sess, config=client_config)
    return pyodata.Client(service_url, sess)


__all__ = ["load_odata_client"]
