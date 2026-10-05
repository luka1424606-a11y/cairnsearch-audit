from pathlib import Path


ROOT = Path(__file__).parents[2] / "src" / "cairnsearch"


def test_target_platform_has_no_sqlite_dependency():
    db_source = (ROOT / "platform" / "db.py").read_text(encoding="utf-8")
    assert "sqlite3" not in db_source


def test_agent_package_does_not_exist_as_implemented_agent_yet():
    agents = ROOT / "agents"
    if agents.exists():
        assert not any(
            p.name.endswith(".py") and p.name != "__init__.py"
            for p in agents.iterdir()
        )
