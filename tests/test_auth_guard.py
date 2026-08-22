"""Protected endpoints must reject requests with no credentials."""


async def test_list_documents_requires_auth(client):
    resp = await client.get("/documents")          # no Authorization header
    assert resp.status_code in (401, 403)           # unauthorized / forbidden — not allowed in
