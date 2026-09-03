from fastapi.testclient import TestClient

# M7.1's own acceptance criterion ("write one trivial test hitting /health").
# Small, but it's the test that proves the harness itself works: the second
# one below only passes if the get_db override actually reached the route and
# handed it the fixture's SQLite session — a real query, against the test
# database, through the full middleware/routing stack.


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_db_uses_the_overridden_test_session(client: TestClient) -> None:
    # /health/db runs SELECT 1 through Depends(get_db). Without the override
    # this would hit the configured Postgres (or fail outright); passing here
    # means the fixture's session is genuinely the one being injected.
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
