import os
import sys
from types import SimpleNamespace, ModuleType

import polars as pl
import pytest

from odata_to_staging.functions.download_parquet_odata import download_parquet_odata
from odata_to_staging.functions.engine_loaders import load_odata_client


class _Prop:
    def __init__(self, name: str):
        self.name = name


class _EntityType:
    def __init__(self, keys, props):
        self.key_proprties = [_Prop(k) for k in keys]
        self._props = [_Prop(p) for p in props]

    def proprties(self):
        return list(self._props)


class _Schema:
    def __init__(self, mapping):
        self._mapping = mapping

    def entity_set(self, name):
        et = self._mapping[name]
        return SimpleNamespace(entity_type=et)


class _Request:
    def __init__(self, pages_ref, count):
        # pages_ref is a list of pages; execute() will pop from it lazily
        self._pages_ref = pages_ref
        self._count = count
        self._next_url = None

    # Chainable no-ops for select/expand/filter
    def select(self, *_, **__):
        return self

    def expand(self, *_, **__):
        return self

    def filter(self, *_, **__):
        return self

    def skip(self, *_):
        return self

    def top(self, *_):
        return self

    def next_url(self, url):  # emulate API; we won't use in these tests
        self._next_url = url
        return self

    def count(self, inline=False):  # inline ignored here
        class _Count:
            def __init__(self, value):
                self._value = value

            def execute(self):
                return self._value

        return _Count(self._count)

    def execute(self):
        # Lazily consume the next available page when executing
        data = self._pages_ref.pop(0) if self._pages_ref else []
        return list(data)


class _EntitySetProxy:
    def __init__(self, name, pages, total):
        self._name = name
        self._pages = list(pages)
        self._total = total

    def get_entities(self):
        # Return a request bound to the shared pages list; it will consume on execute()
        return _Request(pages_ref=self._pages, count=self._total)


class _Client:
    def __init__(self, schema, entity_sets):
        self.schema = schema
        self.entity_sets = entity_sets


class _Cfg:
    """Minimal config stub: mapping section -> key -> value."""

    def __init__(self, mapping):
        self._mapping = mapping

    def has_option(self, section, option):  # ConfigParser-like API subset
        return option in self._mapping.get(section, {})

    def get(self, section, option, fallback=None):  # ConfigParser-like API subset
        return self._mapping.get(section, {}).get(option, fallback)


def _install_fake_pyodata(monkeypatch):
    captured = {}

    class _Client:
        def __init__(self, service_url, session, config=None):
            captured["service_url"] = service_url
            captured["session"] = session
            captured["config"] = config

    class _Config:
        def __init__(self, retain_null):
            self.retain_null = retain_null

    mod_pyodata = ModuleType("pyodata")
    mod_pyodata.__path__ = []
    mod_pyodata_v2 = ModuleType("pyodata.v2")
    mod_pyodata_v2.__path__ = []
    mod_pyodata_v2_model = ModuleType("pyodata.v2.model")
    setattr(mod_pyodata_v2_model, "Config", _Config)

    setattr(mod_pyodata, "Client", _Client)
    setattr(mod_pyodata, "v2", mod_pyodata_v2)
    setattr(mod_pyodata_v2, "model", mod_pyodata_v2_model)

    monkeypatch.setitem(sys.modules, "pyodata", mod_pyodata)
    monkeypatch.setitem(sys.modules, "pyodata.v2", mod_pyodata_v2)
    monkeypatch.setitem(sys.modules, "pyodata.v2.model", mod_pyodata_v2_model)

    return captured, _Client


def test_download_empty_entity_set(tmp_path):
    # Schema: Employees(ID key, Name prop)
    et = _EntityType(keys=["ID"], props=["Name"])
    schema = _Schema({"Employees": et})
    # No data pages
    es_proxy = SimpleNamespace(
        Employees=_EntitySetProxy("Employees", pages=[[]], total=0)
    )
    client = _Client(schema=schema, entity_sets=es_proxy)

    out_dir = tmp_path / "data"
    manifest = download_parquet_odata(
        client, entity_sets=["Employees"], output_dir=str(out_dir)
    )
    assert manifest is not None
    # Directory exists but contains only manifest
    files = os.listdir(out_dir)
    assert any(f.startswith(".ggmpilot_parquet_manifest_") for f in files)
    assert not any(f.endswith(".parquet") for f in files)


def test_download_simple_two_rows(tmp_path):
    et = _EntityType(keys=["ID"], props=["Name"])
    schema = _Schema({"Employees": et})

    class E:
        def __init__(self, ID, Name):
            self.ID = ID
            self.Name = Name

    page1 = [E(1, "Alice"), E(2, "Bob")]
    es_proxy = SimpleNamespace(
        Employees=_EntitySetProxy("Employees", pages=[page1], total=2)
    )
    client = _Client(schema=schema, entity_sets=es_proxy)

    out_dir = tmp_path / "data"
    manifest = download_parquet_odata(
        client,
        entity_sets=["Employees"],
        output_dir=str(out_dir),
        page_size=10,
        log_row_count=True,
    )

    assert manifest is not None
    files = sorted([f for f in os.listdir(out_dir) if f.endswith(".parquet")])
    assert files == ["Employees_part0000.parquet"]
    # Basic sanity: file is a valid parquet we can read
    df = pl.read_parquet(out_dir / files[0])
    assert set(df.columns) == {"ID", "Name"}
    assert len(df) == 2


def test_load_odata_client_basic_auth(monkeypatch):
    """load_odata_client wires BASIC auth and retain_null config."""

    captured, client_cls = _install_fake_pyodata(monkeypatch)

    class _Session:
        def __init__(self):
            self.verify = True
            self.headers = {}
            self.auth = None

    monkeypatch.setattr(
        "odata_to_staging.functions.engine_loaders.requests.Session", _Session
    )

    cfg = _Cfg(
        {
            "odata-source": {
                "ODATA_URL": "https://example.test/odata",
                "ODATA_AUTH_MODE": "BASIC",
                "ODATA_USERNAME": "user1",
                "ODATA_PASSWORD": "secret",
                "ODATA_RETAIN_NULL": "True",
            },
            "settings": {"ASK_PASSWORD_IN_CLI": "False"},
        }
    )

    client = load_odata_client(cfg)
    assert isinstance(client, client_cls)
    assert captured["service_url"] == "https://example.test/odata"
    sess = captured["session"]
    assert isinstance(sess, _Session)
    # BASIC auth set on session
    assert sess.auth == ("user1", "secret")
    # retain_null=True propagated into pyodata config
    assert captured["config"].retain_null is True


def test_load_odata_client_basic_auth_missing_username(monkeypatch):
    _install_fake_pyodata(monkeypatch)
    cfg = _Cfg(
        {
            "odata-source": {
                "ODATA_URL": "https://example.test/odata",
                "ODATA_AUTH_MODE": "BASIC",
                "ODATA_PASSWORD": "secret",
            },
            "settings": {"ASK_PASSWORD_IN_CLI": "False"},
        }
    )

    with pytest.raises(ValueError, match="ODATA_USERNAME.*BASIC"):
        load_odata_client(cfg)


def test_load_odata_client_basic_auth_missing_password(monkeypatch):
    _install_fake_pyodata(monkeypatch)
    cfg = _Cfg(
        {
            "odata-source": {
                "ODATA_URL": "https://example.test/odata",
                "ODATA_AUTH_MODE": "BASIC",
                "ODATA_USERNAME": "user1",
            },
            "settings": {"ASK_PASSWORD_IN_CLI": "False"},
        }
    )

    with pytest.raises(ValueError, match="ODATA_PASSWORD.*BASIC"):
        load_odata_client(cfg)


def test_load_odata_client_bearer_missing_token(monkeypatch):
    _install_fake_pyodata(monkeypatch)
    cfg = _Cfg(
        {
            "odata-source": {
                "ODATA_URL": "https://example.test/odata",
                "ODATA_AUTH_MODE": "BEARER",
            }
        }
    )

    with pytest.raises(ValueError, match="ODATA_BEARER_TOKEN.*BEARER"):
        load_odata_client(cfg)
