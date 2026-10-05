from pathlib import Path

APP_PATH = Path(__file__).parents[2] / "src" / "cairnsearch" / "api" / "app.py"


def test_legacy_destructive_startup_is_removed() -> None:
    source = APP_PATH.read_text(encoding="utf-8")
    assert "def clear_all_data" not in source
    assert "shutil.rmtree" not in source
    assert "clear_all_data()" not in source
