"""Split text into overlapping chunks for embedding."""

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """Split `text` into fixed-size character chunks that overlap by `overlap` chars.

    ~800 chars ≈ 200 tokens — a focused-but-contextful chunk.
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_szie must be greater than overlap")
    
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:                         # skip empty/whitespace-only pieces
            chunks.append(chunk)
        start += chunk_size - overlap     # advance by (size − overlap) → the overlap
    return chunks