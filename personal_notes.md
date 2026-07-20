# I/O (Input/Output)

**Definition:** Any operation where the CPU communicates with a device _outside itself and RAM_ — sending data out or reading data in.

## Key idea

- The CPU's "home turf" = **CPU + RAM** (nanosecond-fast, direct).
- Anything beyond that = **I/O** (send a request → _wait_ for a separate device).
- The boundary is **RAM**, not the physical computer. A local SSD is still I/O.

## Types

- **Disk I/O** — files, reading/writing to SSD
- **Network I/O** — HTTP requests, calling APIs
- **Database I/O** — queries (network + disk underneath)
- **User I/O** — keyboard input, terminal output

## Speed (why I/O is "slow")

| Operation | Rough time |
| --------- | ---------- |
| CPU ↔ RAM | ~100 ns    |
| Read SSD  | ~100 µs    |
| Network   | ~1–100 ms  |

## Why it matters

- **I/O-bound** = limited by _waiting_ → **async helps** (`await` lets the CPU serve other requests while waiting).
- **CPU-bound** = limited by _computing_ → async doesn't help; need more cores.
- Most web work (DB calls, API calls) is **I/O-bound** → the reason FastAPI uses `async`.

> **Mental model:** I/O = CPU asks another device for data and waits. Computation = CPU works with what's already in RAM.

Request → [ API layer ] routes: receive request, return response
[ Service layer ] business logic: "what should happen"
[ Data layer ] models + DB access: "how it's stored"

What ruff is: a linter (finds bugs/bad patterns) and formatter (auto-styles code) in one, written in Rust so it's instant. It's the modern standard — replaces flake8 + isort + black.

- global is only needed when the = puts a new value on the name itself.
  If the = is on an index/attribute (thing[k] =, thing.attr =), you're mutating the object — no global.

* DI in one line: don't fetch what you need — declare it, and let FastAPI hand it to you.
* SQLAlchemy:- SQLAlchemy is a library for talking to SQL databases from Python
*     tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list) # Passing the callable means each row gets its own fresh empty list — the mutable-default trap you learned about, handled correctly.
* Analogy
  Image = a fresh install disc of a game, postgres etc (the program).
  Container = the game running on a console (you can play, and it has a temporary memory-card slot).
  Volume = an external memory card you plugged in → your saves persist even if you unplug the console (delete the container) and boot the game on a new one.
* A transaction is a group of database operations that all succeed or all fail — together. It's "all-or-nothing." In SQL:
* That "all-or-nothing" guarantee is Atomicity — the "A" in ACID (the four guarantees databases give: Atomicity, Consistency, Isolation, Durability). Atomicity is the one you'll reason about daily.
* func is SQLAlchemy's gateway to any SQL function? func.count() generates the SQL COUNT() aggregate, which counts rows.
* Encryption is two-way: encrypt → ciphertext → decrypt back to the original. Reversible (with the key).
* Hashing is one-way: hash("hunter2") → a fixed string, and there's no way to reverse it back to "hunter2".
* Passwords use hashing, precisely because it's irreversible — even you (the developer) can't recover a user's password. So how do you check a login? You hash the password they typed and compare it to the stored hash:
* You never un-hash anything. You only ever compare hashes.
* Redis is an in-memory key-value data store. Break that down:

Key-value — at its core, you store and fetch values by a key, like a giant dictionary:

SET user:5:name "Ravi"
GET user:5:name → "Ravi"
In-memory — it keeps all data in RAM, not on disk. This is the headline feature.
Data store / server — it runs as a separate server (your cortex-redis container) that apps talk to over the network.

- Redis = a blazing-fast, in-memory key-value store used for anything that needs speed and is transient/recomputable: caching, rate limiting, queues, sessions, real-time. Postgres holds the truth; Redis makes hot paths fast.

- Your API will hit Postgres constantly for the same data (e.g., a user's profile on every request). Caching hot data in Redis means fewer DB round-trips → faster responses + a lighter database. And rate limiting protects expensive endpoints (like the LLM calls coming in Phase 4 — you don't want one user hammering a pricey AI endpoint). Redis is the speed-and-control layer in front of your durable store.

- What Redis is used for (you've done one, about to do two)
  Message broker / task queue — ✅ you already did this (Celery broker/backend in 3.5). Its list structure holds the task queue.
  Caching — store expensive query/computation results with a TTL, serve repeats instantly. ← 3.6 next
  Rate limiting — fast counters (INCR + EXPIRE) to cap requests per user/window. ← 3.6 next
  Session storage — store login sessions (fast lookup per request).
  Pub/Sub & real-time — chat, live notifications, presence.
  Distributed locks — coordinate across multiple app servers.
  Leaderboards / rankings — sorted sets (game scores, trending).
  - db 1 — a single Redis server has 16 numbered "databases" (0–15). Celery uses 0; we use 1 so our cache keys don't mix with task queue data. Clean separation.
    decode_responses=True — makes Redis return str instead of raw bytes, so you get clean Python strings back.

* Big binary files → object storage (S3/MinIO); the database stores metadata and a pointer, not the bytes. Storing extracted text in the DB (like Cortex does) is fine — that's queryable data, not a blob.

* A BLOB (or BYTEA in Postgres) column stores raw bytes — a PDF, an image, an audio file — directly in a table cell, as opposed to text or numbers.

* Need the value? → make it a parameter (current_user: CurrentUser).
  Just need the gate, don't use the value? → put it in dependencies=[...]

* RAG = Retrieval-Augmented Generation.

* The RAG idea: Instead of stuffing everything in, you retrieve only the few most relevant pieces for a given question, and hand those to the LLM as context. The model then generates an answer grounded in your actual data.

* Why 768 and not 3072? gemini-embedding-001 defaults to 3072, but pgvector's ANN indexes only support up to 2000 dimensions. We'll ask Gemini for 768-dim vectors (it supports output_dimensionality) — smaller, faster, indexable, and plenty accurate. Cosine search (<=>) works fine without manual normalization.
