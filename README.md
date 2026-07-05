# Cortex — AI Knowledge Assistant

A document Q&A backend: upload documents and chat with an AI that answers
from them, with citations. Built with FastAPI.

## Setup
    virtualenv .venv
    ./.venv/bin/pip install -r requirements.txt

## Run
    ./.venv/bin/uvicorn app.main:app --reload

Then open http://127.0.0.1:8000/docs
