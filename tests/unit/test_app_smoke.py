from cairnsearch.api.app import create_app


def test_create_app_smoke() -> None:
    app = create_app()
    assert app.title == "cairnsearch"
