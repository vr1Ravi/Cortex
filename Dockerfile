FROM python:3.14-slim

# Cleaner logs (unbuffered) and no .pyc clutter in the image.
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Build tools — needed only if a package lacks a prebuilt wheel for Python 3.14 on Linux.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

# 1. Deps FIRST (own cached layer — unchanged unless requirements.txt changes).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. THEN the code (edits here don't bust the deps layer above).
COPY . .

# 3. Start the API. host 0.0.0.0 = reachable from outside the container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
