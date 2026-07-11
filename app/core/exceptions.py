"""Domain exceptions — business errors that know nothing about HTTP.

The web layer (main.py) maps these to HTTP responses via exception handlers.
"""


class CortexError(Exception):
    """Base class for all Cortex domain errors"""


class DocumentNotFoundError(CortexError):
    """Raised when a document id doesn't exist."""

    def __init__(self, doc_id: int) -> None:
        self.doc_id = doc_id
        super().__init__(f"Document {doc_id} not found")
