"""Cortex — AI Knowledge Assistant. Application entrypoint.

Run the dev server from the project root:
    ./.venv/bin/uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import documents, users
from app.core.exceptions import DocumentNotFoundError, EmailAlreadyExistsError

app = FastAPI(
    title="Cortex",
    description="AI Knowledge Assistant — upload documents and chat with them.",
    version="0.1.0",
)

app.include_router(documents.router)
app.include_router(users.router)


@app.exception_handler(DocumentNotFoundError)
async def document_not_found_handler(request: Request, exc: DocumentNotFoundError) -> JSONResponse:
    """Map the domain error -> a clean 404 response, app-wide"""
    return JSONResponse(status_code=404, content={"detail": str(exc), "doc_id": exc.doc_id})

@app.exception_handler(EmailAlreadyExistsError)
async def email_exists_handler(request: Request, exc: EmailAlreadyExistsError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


# --- Endpoints ---
@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness check — confirms the API is up."""
    return {"status": "ok"}
