"""Shared pytest fixtures — available to every test file automatically."""

import pytest
from httpx import ASGITransport, AsyncClient


from app.main import app

@pytest.fixture
async def client():
     """An HTTP client that calls the app IN-PROCESS (no running server)."""
     transport = ASGITransport(app=app)          # route requests straight into the FastAPI app
     async with AsyncClient(transport=transport, base_url="http://test") as c:
          yield c                       # tests get `c`; teardown closes it after