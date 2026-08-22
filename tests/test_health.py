"""Tests for the health endpoint."""


async def test_health_returns_ok(client):
    resp = await client.get("/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


    
async def test_unknown_route_returns_404(client):
    resp = await client.get("/does-not-exist")
    assert resp.status_code == 404
