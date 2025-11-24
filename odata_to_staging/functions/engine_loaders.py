import json
import logging
from typing import Any, Dict, Optional, cast

import requests
from requests.adapters import HTTPAdapter

try:
    # urllib3 is a transitive dep of requests; Retry offers robust backoff
    from urllib3.util.retry import Retry  # type: ignore
except Exception:  # pragma: no cover - fallback if urllib3 API differs
    Retry = None  # type: ignore

from utils.config.get_config_value import get_config_value


log = logging.getLogger("odata_to_staging.engine_loaders")


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

    verify_ssl_opt = cast(
        Optional[bool],
        get_config_value(
            "ODATA_VERIFY_SSL",
            section="odata-connection",
            cfg_parser=cfg,
            default=None,
            cast_type=bool,
            allow_none_if_cast_fails=True,
        )
        or get_config_value(
            "ODATA_VERIFY_SSL",
            section="odata-source",
            cfg_parser=cfg,
            default=None,
            cast_type=bool,
            allow_none_if_cast_fails=True,
        ),
    )
    verify_ssl = True if verify_ssl_opt is None else verify_ssl_opt

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
        username = cast(
            str,
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
        password = cast(
            str,
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
        sess.auth = (username, password)
    elif auth_mode == "BEARER":
        token = cast(
            str,
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
        sess.headers.setdefault("Authorization", f"Bearer {token}")
    elif auth_mode == "NONE":
        pass
    else:
        raise ValueError("ODATA_AUTH_MODE must be one of: NONE | BASIC | BEARER")

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
        _orig_request = sess.request  # type: ignore[attr-defined]

        def _request_with_timeout(method, url, **kwargs):  # type: ignore[no-redef]
            kwargs.setdefault("timeout", timeout_seconds)
            return _orig_request(method, url, **kwargs)

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


def load_destination_engine(cfg: Any):
    """Delegate to existing destination engine loader to avoid duplication."""
    from sql_to_staging.functions.engine_loaders import (
        load_destination_engine as _load_dst,
    )

    return _load_dst(cfg)
