"""
Тесты для новой системы конфигурации (YAML + env-подстановка + Pydantic).
"""
import os
import textwrap
from pathlib import Path

import pytest

from app.config import (
    _load_dotenv,
    _substitute_env,
    load_settings,
    Settings,
    ServerConfig,
    DatabaseConfig,
    JwtConfig,
    StaticFileConfig,
)


# ─── Тесты _substitute_env ────────────────────────────────────────────────────

class TestSubstituteEnv:
    def test_replaces_with_env_var(self, monkeypatch):
        monkeypatch.setenv("MY_VAR", "hello")
        result = _substitute_env('value: {{ env("MY_VAR", "default") }}')
        assert result == "value: hello"

    def test_uses_default_when_var_missing(self, monkeypatch):
        monkeypatch.delenv("MISSING_VAR", raising=False)
        result = _substitute_env('value: {{ env("MISSING_VAR", "fallback") }}')
        assert result == "value: fallback"

    def test_env_overrides_default(self, monkeypatch):
        monkeypatch.setenv("OVERRIDE_VAR", "from_env")
        result = _substitute_env('value: {{ env("OVERRIDE_VAR", "default_val") }}')
        assert result == "value: from_env"

    def test_no_default_returns_empty_string(self, monkeypatch):
        monkeypatch.delenv("NO_DEFAULT_VAR", raising=False)
        result = _substitute_env('value: {{ env("NO_DEFAULT_VAR") }}')
        assert result == "value: "

    def test_multiple_substitutions(self, monkeypatch):
        monkeypatch.setenv("HOST", "myhost")
        monkeypatch.setenv("PORT", "9090")
        raw = 'host: {{ env("HOST", "localhost") }}\nport: {{ env("PORT", "8080") }}'
        result = _substitute_env(raw)
        assert result == "host: myhost\nport: 9090"

    def test_no_placeholders_unchanged(self):
        raw = "host: localhost\nport: 8080"
        assert _substitute_env(raw) == raw


# ─── Тесты _load_dotenv ───────────────────────────────────────────────────────

class TestLoadDotenv:
    def test_loads_vars_from_file(self, tmp_path, monkeypatch):
        dotenv = tmp_path / ".env"
        dotenv.write_text('TEST_LOAD_KEY=loaded_value\n', encoding="utf-8")
        monkeypatch.delenv("TEST_LOAD_KEY", raising=False)
        _load_dotenv(dotenv)
        assert os.environ.get("TEST_LOAD_KEY") == "loaded_value"

    def test_does_not_overwrite_existing_env(self, tmp_path, monkeypatch):
        dotenv = tmp_path / ".env"
        dotenv.write_text('EXISTING_KEY=from_dotenv\n', encoding="utf-8")
        monkeypatch.setenv("EXISTING_KEY", "from_system")
        _load_dotenv(dotenv)
        assert os.environ["EXISTING_KEY"] == "from_system"

    def test_handles_missing_file(self, tmp_path):
        # Не должно вызывать исключений
        _load_dotenv(tmp_path / "nonexistent.env")

    def test_skips_comments_and_empty_lines(self, tmp_path, monkeypatch):
        dotenv = tmp_path / ".env"
        dotenv.write_text(
            '# comment\n\nVALID_KEY=valid_value\n',
            encoding="utf-8"
        )
        monkeypatch.delenv("VALID_KEY", raising=False)
        _load_dotenv(dotenv)
        assert os.environ.get("VALID_KEY") == "valid_value"

    def test_strips_quotes_from_values(self, tmp_path, monkeypatch):
        dotenv = tmp_path / ".env"
        dotenv.write_text('QUOTED_KEY="quoted_value"\n', encoding="utf-8")
        monkeypatch.delenv("QUOTED_KEY", raising=False)
        _load_dotenv(dotenv)
        assert os.environ.get("QUOTED_KEY") == "quoted_value"


# ─── Тесты load_settings ─────────────────────────────────────────────────────

class TestLoadSettings:
    def _write_config(self, tmp_path: Path, content: str) -> Path:
        cfg = tmp_path / "config.yaml"
        cfg.write_text(textwrap.dedent(content), encoding="utf-8")
        return cfg

    def test_minimal_config_with_db_uri(self, tmp_path, monkeypatch):
        cfg = self._write_config(tmp_path, """
            database:
              uri: sqlite+aiosqlite:///test.db
        """)
        monkeypatch.setenv("STATAPI_CONFIG", str(cfg))
        s = load_settings()
        assert str(s.database.uri) == "sqlite+aiosqlite:///test.db"

    def test_env_var_substitution_in_yaml(self, tmp_path, monkeypatch):
        monkeypatch.setenv("STATAPI_DB_URL", "sqlite+aiosqlite:///env_test.db")
        cfg = self._write_config(tmp_path, """
            database:
              uri: '{{ env("STATAPI_DB_URL") }}'
        """)
        monkeypatch.setenv("STATAPI_CONFIG", str(cfg))
        s = load_settings()
        assert "env_test.db" in str(s.database.uri)

    def test_default_values_without_env_vars(self, tmp_path, monkeypatch):
        cfg = self._write_config(tmp_path, """
            database:
              uri: sqlite+aiosqlite:///app.db
        """)
        monkeypatch.setenv("STATAPI_CONFIG", str(cfg))
        s = load_settings()
        assert s.server.host == "localhost"
        assert s.server.port == 8080
        assert s.jwt.access.secret == "example1"
        assert s.jwt.access.expiration == 900
        assert s.jwt.refresh.secret == "example2"
        assert s.jwt.refresh.expiration == 2592000
        assert s.jwt.refresh.cookie_name == "refresh_token"

    def test_server_section_overrides(self, tmp_path, monkeypatch):
        cfg = self._write_config(tmp_path, """
            server:
              host: 0.0.0.0
              port: 9000
            database:
              uri: sqlite+aiosqlite:///app.db
        """)
        monkeypatch.setenv("STATAPI_CONFIG", str(cfg))
        s = load_settings()
        assert s.server.host == "0.0.0.0"
        assert s.server.port == 9000

    def test_port_coerced_to_int_from_string_via_env(self, tmp_path, monkeypatch):
        monkeypatch.setenv("STATAPI_PORT", "5000")
        cfg = self._write_config(tmp_path, """
            server:
              port: '{{ env("STATAPI_PORT", "8080") }}'
            database:
              uri: sqlite+aiosqlite:///app.db
        """)
        monkeypatch.setenv("STATAPI_CONFIG", str(cfg))
        s = load_settings()
        assert s.server.port == 5000
        assert isinstance(s.server.port, int)

    def test_missing_config_file_raises(self, monkeypatch):
        monkeypatch.setenv("STATAPI_CONFIG", "/nonexistent/path/config.yaml")
        with pytest.raises(FileNotFoundError):
            load_settings()

    def test_missing_database_uri_raises_system_exit(self, tmp_path, monkeypatch):
        cfg = self._write_config(tmp_path, """
            server:
              host: localhost
        """)
        monkeypatch.setenv("STATAPI_CONFIG", str(cfg))
        with pytest.raises(SystemExit):
            load_settings()

    def test_jwt_section_overrides(self, tmp_path, monkeypatch):
        cfg = self._write_config(tmp_path, """
            database:
              uri: sqlite+aiosqlite:///app.db
            jwt:
              access:
                secret: my_access_secret
                expiration: 300
              refresh:
                secret: my_refresh_secret
                expiration: 86400
                cookie_name: my_refresh
        """)
        monkeypatch.setenv("STATAPI_CONFIG", str(cfg))
        s = load_settings()
        assert s.jwt.access.secret == "my_access_secret"
        assert s.jwt.access.expiration == 300
        assert s.jwt.refresh.secret == "my_refresh_secret"
        assert s.jwt.refresh.expiration == 86400
        assert s.jwt.refresh.cookie_name == "my_refresh"

    def test_cors_section(self, tmp_path, monkeypatch):
        cfg = self._write_config(tmp_path, """
            server:
              cors:
                allowed_hosts:
                  - http://localhost:3000
                allowed_methods:
                  - GET
                  - POST
                allowed_headers:
                  - Authorization
            database:
              uri: sqlite+aiosqlite:///app.db
        """)
        monkeypatch.setenv("STATAPI_CONFIG", str(cfg))
        s = load_settings()
        assert s.server.cors is not None
        assert "http://localhost:3000" in s.server.cors.allowed_hosts
        assert "GET" in s.server.cors.allowed_methods

    def test_static_section(self, tmp_path, monkeypatch):
        cfg = self._write_config(tmp_path, """
            server:
              static:
                base_path: /srv/static
                files:
                  - path: dist
                    name: frontend
                    fallback: true
                    fallback_to: index.html
            database:
              uri: sqlite+aiosqlite:///app.db
        """)
        monkeypatch.setenv("STATAPI_CONFIG", str(cfg))
        s = load_settings()
        assert s.server.static is not None
        assert s.server.static.base_path == "/srv/static"
        assert len(s.server.static.files) == 1
        assert s.server.static.files[0].fallback is True
        assert s.server.static.files[0].fallback_to == "index.html"

    def test_missing_sections_use_defaults(self, tmp_path, monkeypatch):
        cfg = self._write_config(tmp_path, """
            database:
              uri: sqlite+aiosqlite:///app.db
        """)
        monkeypatch.setenv("STATAPI_CONFIG", str(cfg))
        s = load_settings()
        assert s.server.cors is None
        assert s.server.static is None
        assert s.server.compression is None

    def test_custom_config_path_via_statapi_config(self, tmp_path, monkeypatch):
        custom = tmp_path / "custom.yaml"
        custom.write_text(
            "database:\n  uri: sqlite+aiosqlite:///custom.db\n",
            encoding="utf-8"
        )
        monkeypatch.setenv("STATAPI_CONFIG", str(custom))
        s = load_settings()
        assert "custom.db" in str(s.database.uri)

    def test_env_priority_system_over_dotenv(self, tmp_path, monkeypatch):
        """Системные переменные имеют приоритет над .env"""
        dotenv = tmp_path / ".env"
        dotenv.write_text('STATAPI_DB_URL=sqlite+aiosqlite:///from_dotenv.db\n', encoding="utf-8")
        monkeypatch.setenv("STATAPI_DB_URL", "sqlite+aiosqlite:///from_system.db")
        cfg = self._write_config(tmp_path, """
            database:
              uri: '{{ env("STATAPI_DB_URL", "sqlite+aiosqlite:///default.db") }}'
        """)
        monkeypatch.setenv("STATAPI_CONFIG", str(cfg))
        # Системная переменная уже задана через monkeypatch, dotenv не должен её перезаписать
        _load_dotenv(dotenv)
        s = load_settings()
        assert "from_system.db" in str(s.database.uri)


# ─── Тесты StaticFileConfig валидации ────────────────────────────────────────

class TestStaticFileConfig:
    def test_valid_without_fallback(self):
        cfg = StaticFileConfig(path="dist", name="frontend")
        assert cfg.fallback is False
        assert cfg.fallback_to is None

    def test_valid_with_fallback(self):
        cfg = StaticFileConfig(path="dist", name="frontend", fallback=True, fallback_to="index.html")
        assert cfg.fallback is True
        assert cfg.fallback_to == "index.html"

    def test_fallback_true_without_fallback_to_raises(self):
        with pytest.raises(Exception, match="fallback_to"):
            StaticFileConfig(path="dist", name="frontend", fallback=True)

    def test_fallback_to_without_fallback_raises(self):
        with pytest.raises(Exception, match="fallback_to"):
            StaticFileConfig(path="dist", name="frontend", fallback_to="index.html")


# ─── Тесты backward-compatible свойств ───────────────────────────────────────

class TestBackwardCompatProperties:
    def _make_settings(self, tmp_path, monkeypatch, extra_yaml: str = "") -> Settings:
        content = textwrap.dedent(f"""
            server:
              cors:
                allowed_hosts:
                  - http://example.com
                allowed_methods:
                  - GET
                allowed_headers:
                  - Authorization
              static:
                base_path: /srv/static
            database:
              uri: sqlite+aiosqlite:///compat.db
            jwt:
              access:
                secret: acc_secret
                expiration: 600
              refresh:
                secret: ref_secret
                expiration: 1800
            {extra_yaml}
        """)
        cfg = tmp_path / "config.yaml"
        cfg.write_text(content, encoding="utf-8")
        monkeypatch.setenv("STATAPI_CONFIG", str(cfg))
        return load_settings()

    def test_sqlalchemy_database_url(self, tmp_path, monkeypatch):
        s = self._make_settings(tmp_path, monkeypatch)
        assert "compat.db" in str(s.sqlalchemy_database_url)

    def test_static_files(self, tmp_path, monkeypatch):
        s = self._make_settings(tmp_path, monkeypatch)
        assert s.static_files == "/srv/static"

    def test_static_files_default_without_section(self, tmp_path, monkeypatch):
        cfg = tmp_path / "config.yaml"
        cfg.write_text("database:\n  uri: sqlite+aiosqlite:///app.db\n", encoding="utf-8")
        monkeypatch.setenv("STATAPI_CONFIG", str(cfg))
        s = load_settings()
        assert s.static_files == "./static"

    def test_allowed_hosts(self, tmp_path, monkeypatch):
        s = self._make_settings(tmp_path, monkeypatch)
        assert "http://example.com" in s.allowed_hosts

    def test_allowed_methods(self, tmp_path, monkeypatch):
        s = self._make_settings(tmp_path, monkeypatch)
        assert "GET" in s.allowed_methods

    def test_allowed_headers(self, tmp_path, monkeypatch):
        s = self._make_settings(tmp_path, monkeypatch)
        assert "Authorization" in s.allowed_headers

    def test_access_secret(self, tmp_path, monkeypatch):
        s = self._make_settings(tmp_path, monkeypatch)
        assert s.access_secret == "acc_secret"

    def test_refresh_secret(self, tmp_path, monkeypatch):
        s = self._make_settings(tmp_path, monkeypatch)
        assert s.refresh_secret == "ref_secret"

    def test_access_duration(self, tmp_path, monkeypatch):
        s = self._make_settings(tmp_path, monkeypatch)
        assert s.access_duration == 600

    def test_refresh_duration(self, tmp_path, monkeypatch):
        s = self._make_settings(tmp_path, monkeypatch)
        assert s.refresh_duration == 1800
