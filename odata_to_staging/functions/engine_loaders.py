import json
import logging
from typing import Any, Dict, Optional, cast

import requests

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

    service_url = cast(
        str, get_config_value("ODATA_URL", section="odata-source", cfg_parser=cfg)
    )

    auth_mode = cast(
        str,
        get_config_value(
            "ODATA_AUTH_MODE", section="odata-source", cfg_parser=cfg, default="NONE"
        ),
    ).upper()

    verify_ssl = cast(
        bool,
        get_config_value(
            "ODATA_VERIFY_SSL",
            section="odata-source",
            cfg_parser=cfg,
            default=True,
            cast_type=bool,
        ),
    )

    headers_raw = cast(
        Optional[str],
        get_config_value(
            "ODATA_HEADERS",
            section="odata-source",
            cfg_parser=cfg,
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
                section="odata-source",
                cfg_parser=cfg,
                cast_type=str,
            ),
        )
        password = cast(
            str,
            get_config_value(
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
                cast_type=str,
            ),
        )
        sess.auth = (username, password)
    elif auth_mode == "BEARER":
        token = cast(
            str,
            get_config_value(
                "ODATA_BEARER_TOKEN",
                section="odata-source",
                cfg_parser=cfg,
                print_value=False,
                cast_type=str,
            ),
        )
        sess.headers.setdefault("Authorization", f"Bearer {token}")
    elif auth_mode == "NONE":
        pass
    else:
        raise ValueError("ODATA_AUTH_MODE must be one of: NONE | BASIC | BEARER")

    log.info("Initialized requests.Session for OData (verify_ssl=%s)", verify_ssl)

    # Retain nulls to distinguish between missing values and default values
    retain_null = cast(
        bool,
        get_config_value(
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
    from source_to_staging.functions.engine_loaders import (
        load_destination_engine as _load_dst,
    )

    return _load_dst(cfg)
