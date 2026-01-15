"""Tests for OData client certificate (mTLS/PKIO) configuration.

Verifies that ODATA_CLIENT_CERT and ODATA_CLIENT_KEY settings are
properly loaded and applied to the requests Session for mTLS authentication.
"""

import os
from unittest.mock import MagicMock, patch

import pytest


class _Cfg:
    """Minimal config parser mock for testing."""

    def __init__(self, mapping):
        self._mapping = mapping

    def has_option(self, section, option):
        return option in self._mapping.get(section, {})

    def get(self, section, option, fallback=None):
        return self._mapping.get(section, {}).get(option, fallback)


def _install_fake_pyodata(monkeypatch):
    """Install a fake pyodata module that doesn't make real HTTP requests."""
    fake_pyodata = MagicMock()
    fake_pyodata.Client = MagicMock(return_value=MagicMock())
    monkeypatch.setitem(__import__("sys").modules, "pyodata", fake_pyodata)
    return fake_pyodata


class TestClientCertificateConfiguration:
    """Tests for client certificate (mTLS/PKIO) configuration in load_odata_client."""

    def test_client_cert_and_key_applied_to_session(self, monkeypatch, tmp_path):
        """Client certificate and key are applied to session.cert when both are provided."""
        fake_pyodata = _install_fake_pyodata(monkeypatch)

        # Create temporary cert and key files
        cert_file = tmp_path / "client.pem"
        key_file = tmp_path / "client_key.pem"
        cert_file.write_text(
            "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        )
        key_file.write_text(
            "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----"
        )

        # Track what cert is set on the session
        captured_session = {}

        class MockSession:
            def __init__(self):
                self.verify = True
                self.headers = {}
                self.cert = None

            def request(self, method, url, **kwargs):
                return MagicMock()

        def capture_session():
            sess = MockSession()
            captured_session["session"] = sess
            return sess

        monkeypatch.setattr(
            "odata_to_staging.functions.engine_loaders.requests.Session",
            capture_session,
        )

        cfg = _Cfg(
            {
                "odata-connection": {
                    "ODATA_URL": "https://example.test/odata",
                    "ODATA_AUTH_MODE": "NONE",
                    "ODATA_CLIENT_CERT": str(cert_file),
                    "ODATA_CLIENT_KEY": str(key_file),
                },
            }
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        load_odata_client(cfg)

        # Verify session.cert was set to (cert_path, key_path) tuple
        sess = captured_session["session"]
        assert sess.cert == (str(cert_file), str(key_file))

    def test_client_cert_only_combined_file(self, monkeypatch, tmp_path):
        """When only ODATA_CLIENT_CERT is provided, assume combined cert+key file."""
        fake_pyodata = _install_fake_pyodata(monkeypatch)

        # Create temporary combined cert file
        cert_file = tmp_path / "client_combined.pem"
        cert_file.write_text(
            "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----\n"
            "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----"
        )

        captured_session = {}

        class MockSession:
            def __init__(self):
                self.verify = True
                self.headers = {}
                self.cert = None

            def request(self, method, url, **kwargs):
                return MagicMock()

        def capture_session():
            sess = MockSession()
            captured_session["session"] = sess
            return sess

        monkeypatch.setattr(
            "odata_to_staging.functions.engine_loaders.requests.Session",
            capture_session,
        )

        cfg = _Cfg(
            {
                "odata-connection": {
                    "ODATA_URL": "https://example.test/odata",
                    "ODATA_AUTH_MODE": "NONE",
                    "ODATA_CLIENT_CERT": str(cert_file),
                    # No ODATA_CLIENT_KEY - combined file
                },
            }
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        load_odata_client(cfg)

        # Verify session.cert was set to just the cert path (combined file)
        sess = captured_session["session"]
        assert sess.cert == str(cert_file)

    def test_no_client_cert_session_cert_is_none(self, monkeypatch, tmp_path):
        """When no client certificate is configured, session.cert remains None."""
        fake_pyodata = _install_fake_pyodata(monkeypatch)

        captured_session = {}

        class MockSession:
            def __init__(self):
                self.verify = True
                self.headers = {}
                self.cert = None

            def request(self, method, url, **kwargs):
                return MagicMock()

        def capture_session():
            sess = MockSession()
            captured_session["session"] = sess
            return sess

        monkeypatch.setattr(
            "odata_to_staging.functions.engine_loaders.requests.Session",
            capture_session,
        )

        cfg = _Cfg(
            {
                "odata-connection": {
                    "ODATA_URL": "https://example.test/odata",
                    "ODATA_AUTH_MODE": "NONE",
                    # No client cert settings
                },
            }
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        load_odata_client(cfg)

        # Verify session.cert was NOT set
        sess = captured_session["session"]
        assert sess.cert is None

    def test_client_cert_file_not_found_raises(self, monkeypatch, tmp_path):
        """Non-existent client certificate file raises ValueError."""
        _install_fake_pyodata(monkeypatch)

        cfg = _Cfg(
            {
                "odata-connection": {
                    "ODATA_URL": "https://example.test/odata",
                    "ODATA_AUTH_MODE": "NONE",
                    "ODATA_CLIENT_CERT": str(tmp_path / "nonexistent.pem"),
                },
            }
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        with pytest.raises(ValueError, match="ODATA_CLIENT_CERT.*does not exist"):
            load_odata_client(cfg)

    def test_client_key_file_not_found_raises(self, monkeypatch, tmp_path):
        """Non-existent client key file raises ValueError when cert exists."""
        _install_fake_pyodata(monkeypatch)

        # Create cert file but not key file
        cert_file = tmp_path / "client.pem"
        cert_file.write_text(
            "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        )

        cfg = _Cfg(
            {
                "odata-connection": {
                    "ODATA_URL": "https://example.test/odata",
                    "ODATA_AUTH_MODE": "NONE",
                    "ODATA_CLIENT_CERT": str(cert_file),
                    "ODATA_CLIENT_KEY": str(tmp_path / "nonexistent_key.pem"),
                },
            }
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        with pytest.raises(ValueError, match="ODATA_CLIENT_KEY.*does not exist"):
            load_odata_client(cfg)

    def test_client_cert_with_hellome_auth(self, monkeypatch, tmp_path):
        """Client certificate works together with HELLOME authentication mode."""
        fake_pyodata = _install_fake_pyodata(monkeypatch)

        # Create temporary cert files
        cert_file = tmp_path / "client.pem"
        key_file = tmp_path / "client_key.pem"
        cert_file.write_text(
            "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        )
        key_file.write_text(
            "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----"
        )

        captured_session = {}
        captured_hellome_kwargs = {}

        class MockSession:
            def __init__(self):
                self.verify = True
                self.headers = {}
                self.cert = None

            def request(self, method, url, **kwargs):
                return MagicMock()

        def capture_session():
            sess = MockSession()
            captured_session["session"] = sess
            return sess

        monkeypatch.setattr(
            "odata_to_staging.functions.engine_loaders.requests.Session",
            capture_session,
        )

        # Mock HelloMeTokenManager
        class MockTokenManager:
            def __init__(self, **kwargs):
                captured_hellome_kwargs.update(kwargs)

            def get_token(self):
                return "test_token"

        monkeypatch.setattr(
            "odata_to_staging.functions.hellome_auth.HelloMeTokenManager",
            MockTokenManager,
        )

        cfg = _Cfg(
            {
                "odata-connection": {
                    "ODATA_URL": "https://example.test/odata",
                    "ODATA_AUTH_MODE": "HELLOME",
                    "ODATA_CLIENT_CERT": str(cert_file),
                    "ODATA_CLIENT_KEY": str(key_file),
                },
                "hellome-auth": {
                    "HELLOME_TOKEN_ENDPOINT": "https://test.hellome.center/token",
                    "HELLOME_CLIENT_ID": "client_id",
                    "HELLOME_CLIENT_SECRET": "client_secret",
                    "HELLOME_USERNAME": "user",
                    "HELLOME_PASSWORD": "pass",
                },
            }
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        load_odata_client(cfg)

        # Verify both client cert AND HelloMe auth are configured
        sess = captured_session["session"]
        assert sess.cert == (str(cert_file), str(key_file))
        assert "token_endpoint" in captured_hellome_kwargs

    def test_client_key_password_warning_logged(self, monkeypatch, tmp_path, caplog):
        """Warning is logged when ODATA_CLIENT_KEY_PASSWORD is set."""
        import logging

        fake_pyodata = _install_fake_pyodata(monkeypatch)

        # Create temporary cert files
        cert_file = tmp_path / "client.pem"
        key_file = tmp_path / "client_key.pem"
        cert_file.write_text(
            "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        )
        key_file.write_text(
            "-----BEGIN ENCRYPTED PRIVATE KEY-----\ntest\n-----END ENCRYPTED PRIVATE KEY-----"
        )

        class MockSession:
            def __init__(self):
                self.verify = True
                self.headers = {}
                self.cert = None

            def request(self, method, url, **kwargs):
                return MagicMock()

        monkeypatch.setattr(
            "odata_to_staging.functions.engine_loaders.requests.Session",
            MockSession,
        )

        cfg = _Cfg(
            {
                "odata-connection": {
                    "ODATA_URL": "https://example.test/odata",
                    "ODATA_AUTH_MODE": "NONE",
                    "ODATA_CLIENT_CERT": str(cert_file),
                    "ODATA_CLIENT_KEY": str(key_file),
                    "ODATA_CLIENT_KEY_PASSWORD": "secret_password",
                },
            }
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        with caplog.at_level(logging.WARNING):
            load_odata_client(cfg)

        # Verify warning about encrypted keys was logged
        assert any(
            "ODATA_CLIENT_KEY_PASSWORD" in record.message
            and "encrypted" in record.message.lower()
            for record in caplog.records
        )

    def test_client_cert_from_legacy_odata_source_section(self, monkeypatch, tmp_path):
        """Client certificate settings are read from legacy [odata-source] section."""
        fake_pyodata = _install_fake_pyodata(monkeypatch)

        cert_file = tmp_path / "client.pem"
        key_file = tmp_path / "client_key.pem"
        cert_file.write_text(
            "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        )
        key_file.write_text(
            "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----"
        )

        captured_session = {}

        class MockSession:
            def __init__(self):
                self.verify = True
                self.headers = {}
                self.cert = None

            def request(self, method, url, **kwargs):
                return MagicMock()

        def capture_session():
            sess = MockSession()
            captured_session["session"] = sess
            return sess

        monkeypatch.setattr(
            "odata_to_staging.functions.engine_loaders.requests.Session",
            capture_session,
        )

        # Use legacy odata-source section
        cfg = _Cfg(
            {
                "odata-source": {
                    "ODATA_URL": "https://example.test/odata",
                    "ODATA_AUTH_MODE": "NONE",
                    "ODATA_CLIENT_CERT": str(cert_file),
                    "ODATA_CLIENT_KEY": str(key_file),
                },
            }
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        load_odata_client(cfg)

        sess = captured_session["session"]
        assert sess.cert == (str(cert_file), str(key_file))
