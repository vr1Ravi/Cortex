"""Cortex — AI Knowledge Assistant. Application entrypoint.

Run the dev server from the project root:
    ./.venv/bin/uvicorn app.main:app --reload
"""

import time

# import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, chat, demo, documents, rag, tasks, users
from app.core.exceptions import DocumentNotFoundError, EmailAlreadyExistsError, LLMError

app = FastAPI(
    title="Cortex",
    description="AI Knowledge Assistant — upload documents and chat with them.",
    version="0.1.0",
)

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s %(levelname)s %(name)s: %(message)s",
#     force=True,
# )

# --- CORS: allow your future frontend to call the API from the browser ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],   # the frontend origin(s) you'll allow
    allow_credentials=True,
    allow_methods=["*"],                        # GET, POST, PUT, DELETE, ...
    allow_headers=["*"],                        # including Authorization
)

# --- Custom middleware: time every request, expose it in a response header ---

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{elapsed:.4f}s"
    return response

app.include_router(documents.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(demo.router)
app.include_router(chat.router)
app.include_router(rag.router)




@app.exception_handler(DocumentNotFoundError)
async def document_not_found_handler(request: Request, exc: DocumentNotFoundError) -> JSONResponse:
    """Map the domain error -> a clean 404 response, app-wide"""
    return JSONResponse(status_code=404, content={"detail": str(exc), "doc_id": exc.doc_id})

@app.exception_handler(EmailAlreadyExistsError)
async def email_exists_handler(request: Request, exc: EmailAlreadyExistsError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})

@app.exception_handler(LLMError)
async def llm_error_handler(request: Request, exc: LLMError) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "detail": "The AI service is temporarily unavailable. Please try again."
        }
    )
# --- Endpoints ---
@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness check — confirms the API is up."""
    return {"status": "ok"}

