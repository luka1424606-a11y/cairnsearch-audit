import pytest

from cairnsearch.platform.config import PlatformConfig


def test_config_requires_database_url(monkeypatch):
    monkeypatch.delenv("CAIRNSEARCH_DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError):
        PlatformConfig.from_env()


def test_config_reads_database_url_without_secrets_in_source(monkeypatch):
    monkeypatch.setenv("CAIRNSEARCH_DATABASE_URL", "postgresql://example.invalid/test")
    monkeypatch.setenv("CAIRNSEARCH_ENV", "test")
    cfg = PlatformConfig.from_env()
    assert cfg.database_url == "postgresql://example.invalid/test"
    assert cfg.app_env == "test"
