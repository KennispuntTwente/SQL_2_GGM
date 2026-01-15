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


class TestPfxCertificateSupport:
    """Tests for .pfx/.p12 (PKCS#12) certificate support."""

    def _create_test_pfx(self, tmp_path, password: bytes = b"testpass"):
        """Create a minimal test .pfx file with self-signed cert and key."""
        try:
            from cryptography import x509
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives.serialization.pkcs12 import (
                serialize_key_and_certificates,
            )
            from cryptography.x509.oid import NameOID
            import datetime
        except ImportError:
            pytest.skip("cryptography library not installed")

        # Generate a private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # Create a self-signed certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "Test Certificate"),
        ])
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=1))
            .sign(private_key, hashes.SHA256())
        )

        # Serialize to PKCS#12
        pfx_data = serialize_key_and_certificates(
            name=b"test",
            key=private_key,
            cert=cert,
            cas=None,
            encryption_algorithm=serialization.BestAvailableEncryption(password),
        )

        pfx_path = tmp_path / "test_client.pfx"
        pfx_path.write_bytes(pfx_data)
        return pfx_path

    def test_pfx_extracts_cert_and_key(self, tmp_path):
        """_extract_pem_from_pfx extracts certificate and key to temp files."""
        pfx_path = self._create_test_pfx(tmp_path, password=b"secret123")

        from odata_to_staging.functions.engine_loaders import _extract_pem_from_pfx

        cert_path, key_path = _extract_pem_from_pfx(str(pfx_path), password="secret123")

        try:
            # Verify files were created
            assert os.path.exists(cert_path)
            assert os.path.exists(key_path)

            # Verify they contain PEM data
            with open(cert_path, "r") as f:
                cert_content = f.read()
            assert "-----BEGIN CERTIFICATE-----" in cert_content

            with open(key_path, "r") as f:
                key_content = f.read()
            assert "-----BEGIN" in key_content and "PRIVATE KEY-----" in key_content
        finally:
            # Clean up temp files
            for path in [cert_path, key_path]:
                try:
                    os.unlink(path)
                except Exception:
                    pass

    def test_pfx_wrong_password_raises(self, tmp_path):
        """_extract_pem_from_pfx raises clear error for wrong password."""
        pfx_path = self._create_test_pfx(tmp_path, password=b"correct_password")

        from odata_to_staging.functions.engine_loaders import _extract_pem_from_pfx

        with pytest.raises(ValueError, match="incorrect password"):
            _extract_pem_from_pfx(str(pfx_path), password="wrong_password")

    def test_pfx_file_not_found_raises(self, tmp_path, monkeypatch):
        """Non-existent .pfx file raises ValueError."""
        _install_fake_pyodata(monkeypatch)

        cfg = _Cfg(
            {
                "odata-connection": {
                    "ODATA_URL": "https://example.test/odata",
                    "ODATA_AUTH_MODE": "NONE",
                    "ODATA_CLIENT_PFX": str(tmp_path / "nonexistent.pfx"),
                },
            }
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        with pytest.raises(ValueError, match="ODATA_CLIENT_PFX.*does not exist"):
            load_odata_client(cfg)

    def test_pfx_applied_to_session(self, monkeypatch, tmp_path):
        """ODATA_CLIENT_PFX extracts cert/key and applies to session.cert."""
        _install_fake_pyodata(monkeypatch)
        pfx_path = self._create_test_pfx(tmp_path, password=b"pfxpass")

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
                    "ODATA_CLIENT_PFX": str(pfx_path),
                    "ODATA_CLIENT_KEY_PASSWORD": "pfxpass",
                },
            }
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        load_odata_client(cfg)

        # Verify session.cert was set to a tuple of temp file paths
        sess = captured_session["session"]
        assert sess.cert is not None
        assert isinstance(sess.cert, tuple)
        assert len(sess.cert) == 2
        # Temp files should exist (at least for this test's duration)
        cert_path, key_path = sess.cert
        assert os.path.exists(cert_path)
        assert os.path.exists(key_path)

    def test_pfx_takes_precedence_over_pem(self, monkeypatch, tmp_path, caplog):
        """When both ODATA_CLIENT_PFX and ODATA_CLIENT_CERT are set, .pfx is used."""
        import logging

        _install_fake_pyodata(monkeypatch)
        pfx_path = self._create_test_pfx(tmp_path, password=b"pfxpass")

        # Also create PEM files
        cert_file = tmp_path / "client.pem"
        key_file = tmp_path / "client_key.pem"
        cert_file.write_text("-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----")
        key_file.write_text("-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----")

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
                    "ODATA_CLIENT_PFX": str(pfx_path),
                    "ODATA_CLIENT_CERT": str(cert_file),
                    "ODATA_CLIENT_KEY": str(key_file),
                    "ODATA_CLIENT_KEY_PASSWORD": "pfxpass",
                },
            }
        )

        from odata_to_staging.functions.engine_loaders import load_odata_client

        with caplog.at_level(logging.WARNING):
            load_odata_client(cfg)

        # Verify warning was logged about using .pfx over .pem
        assert any(
            "ODATA_CLIENT_PFX" in record.message and "ignoring" in record.message.lower()
            for record in caplog.records
        )

        # Verify the .pfx-extracted files are used, not the .pem files
        sess = captured_session["session"]
        assert sess.cert is not None
        cert_path, key_path = sess.cert
        # The temp files should NOT be the original .pem files
        assert cert_path != str(cert_file)
        assert key_path != str(key_file)

    def test_pfx_with_hellome_auth(self, monkeypatch, tmp_path):
        """ODATA_CLIENT_PFX works together with HELLOME authentication mode."""
        _install_fake_pyodata(monkeypatch)
        pfx_path = self._create_test_pfx(tmp_path, password=b"pfxpass")

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
                    "ODATA_CLIENT_PFX": str(pfx_path),
                    "ODATA_CLIENT_KEY_PASSWORD": "pfxpass",
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

        # Verify both .pfx cert AND HelloMe auth are configured
        sess = captured_session["session"]
        assert sess.cert is not None
        assert len(sess.cert) == 2
        assert "token_endpoint" in captured_hellome_kwargs
