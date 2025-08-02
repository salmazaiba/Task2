
import pytest
from app.main import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()

def test_health_check(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json["status"] == "ok"

def test_shorten_invalid_url(client):
    resp = client.post("/api/shorten", json={"url": "not-a-url"})
    assert resp.status_code == 400

def test_shorten_and_redirect(client):
    long_url = "https://example.com/long/url"
    resp = client.post("/api/shorten", json={"url": long_url})
    assert resp.status_code == 201
    short_code = resp.json["short_code"]

    redir = client.get(f"/{short_code}", follow_redirects=False)
    assert redir.status_code == 302
    assert redir.headers["Location"] == long_url

def test_stats_endpoint(client):
    long_url = "https://example.com/track"
    resp = client.post("/api/shorten", json={"url": long_url})
    short_code = resp.json["short_code"]

    for _ in range(3):
        client.get(f"/{short_code}", follow_redirects=False)

    stats = client.get(f"/api/stats/{short_code}")
    assert stats.status_code == 200
    assert stats.json["clicks"] == 3
    assert stats.json["url"] == long_url

def test_missing_short_code(client):
    stats = client.get("/api/stats/abcdef")
    assert stats.status_code == 404