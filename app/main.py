"""Cortex — AI Knowledge Assistant. Application entrypoint.

Run the dev server from the project root:
    ./.venv/bin/uvicorn app.main:app --reload
"""


from fastapi import FastAPI

from app.api import documents

app = FastAPI(
    title="Cortex",
    description="AI Knowledge Assistant — upload documents and chat with them.",
    version="0.1.0",
)

app.include_router(documents.router)


# --- Endpoints ---
@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness check — confirms the API is up."""
    return {"status": "ok"}
