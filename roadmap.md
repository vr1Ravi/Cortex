# 🚀 FastAPI → AI Software Engineer Roadmap

> **Goal:** Reach the depth of a 2–3 YOE **AI software engineer** — not surface-level CRUD.
> **Method:** Concept-first → build → review → "why?" check. One focused chunk per session.
> **Vehicle project:** **Cortex** — an AI Knowledge Assistant (document Q&A SaaS backend:
> users upload docs → chat with an AI that answers _from their docs_ with citations).

---

## ⏱️ Time budget & cadence

|                    |                                                          |
| ------------------ | -------------------------------------------------------- |
| Weekdays           | 2 hrs/day → **1 session/day**                            |
| Weekends           | 4 hrs/day → **2 sessions/day**                           |
| Weekly capacity    | **18 hrs ≈ 9 sessions/week**                             |
| Session length     | ~2 hrs (concept + build + review)                        |
| Total course       | **~42 sessions · ~84 focused hours**                     |
| Realistic calendar | **~8 weeks** (buffer for practice, debugging & revision) |

> A "session" = one 2-hr block. On weekends you'll do 2 per day. The timeline below
> already bakes in slack for real life — don't rush; depth > speed.

---

## 🗺️ The 7 phases at a glance

| Phase | Theme                                                 | Sessions | Hours  |
| ----- | ----------------------------------------------------- | :------: | :----: |
| 0     | Foundations (async, typing, tooling)                  |    3     |   6    |
| 1     | FastAPI core (Pydantic, DI, routers)                  |    6     |   12   |
| 2     | Data & persistence (async SQLAlchemy, Alembic)        |    6     |   12   |
| 2+    | (Phase 2 ran 7 sessions — relationships & perf split) |    +1    |   +2   |
| 3     | Advanced backend (auth, Celery, Redis, WebSockets)    |    8     |   16   |
| 4     | LLM integration (Claude API, streaming, tools)        |    5     |   10   |
| 5     | RAG + LangChain (embeddings, pgvector, agents)        |    8     |   16   |
| 6     | Ship it (testing, Docker, CI/CD, observability)       |    6     |   12   |
|       | **Total**                                             |  **42**  | **84** |

---

## 📚 Phase-by-phase sessions

### Phase 0 — Foundations · 3 sessions

- [x] **0.1** Async & the event loop — sync vs async, the blocking trap _(DONE)_
- [x] **0.2** Type hints deep + intro to **Pydantic v2** (validation from types) _(DONE)_
- [x] **0.3** Project structure, tooling (git, `.gitignore`, ruff, `requirements.txt`) _(DONE)_

### Phase 1 — FastAPI Core · 6 sessions

- [x] **1.1** Path / query / body params; request lifecycle _(DONE)_
- [x] **1.2** Pydantic models: `response_model`, validation, serialization, config _(DONE)_
- [x] **1.3** **Dependency Injection** — the heart of FastAPI (`Depends`, sub-deps, yield deps) _(DONE)_
- [x] **1.4** Routers & scalable project structure (`APIRouter`, versioning) _(DONE)_
- [x] **1.5** Error handling — exceptions, handlers, status codes, validation errors _(DONE)_
- [x] **1.6** OpenAPI/docs, tags, response models → **build the Cortex API skeleton** _(DONE)_

### Phase 2 — Data & Persistence · 6 sessions

- [x] **2.1** Async **SQLAlchemy 2.0** — engine, sessions, async setup with Postgres _(DONE)_
- [x] **2.2** Models — `Document` ORM model (typed columns, defaults, ARRAY) _(DONE)_; relationships next (with `User`)
- [x] **2.3** **Alembic** migrations — autogenerate, upgrade/downgrade, workflow _(DONE)_
- [x] **2.4** Repository pattern & CRUD wired into DI _(DONE)_
- [x] **2.5** Transactions, session lifecycle, unit-of-work _(DONE)_
- [x] **2.6** Relationships — `User` model, FK + one-to-many (`relationship`, `back_populates`) _(DONE)_
- [x] **2.7** Performance: N+1 problem, eager loading, indexing (Phase 2 finale) _(DONE)_

### Phase 3 — Advanced Backend · 8 sessions

- [x] **3.1** Auth I — password hashing + user registration _(DONE)_ (JWT moved to 3.2)
- [x] **3.2** Auth II — JWT, OAuth2 login, `get_current_user` dependency _(DONE)_
- [x] **3.3** RBAC (roles) + document ownership (owner-only access, 403 vs 404) _(DONE)_
- [x] **3.4** Middleware deep-dive, CORS, request context _(DONE)_
- [x] **3.5** Background tasks vs **Celery** workers + Redis broker _(DONE)_
- [x] **3.6** **Redis** caching & rate limiting _(DONE)_
- [x] **3.7** **WebSockets** & **SSE** streaming responses _(DONE)_
- [x] **3.8** File uploads + config/secrets (`pydantic-settings`, `.env`) _(DONE)_ **← Phase 3 COMPLETE**

### Phase 4 — LLM Integration · 5 sessions

> **Provider: Google Gemini** (`google-genai` SDK) — chosen for its free tier. Same patterns as any LLM.

- [x] **4.1** Calling the **Gemini API** from the backend (`google-genai`, async, messages) _(DONE)_
- [x] **4.2** **Streaming** tokens to the client over SSE _(DONE)_
- [x] **4.3** Prompt design + **structured outputs** (system instruction, `response_schema`) _(DONE)_
- [x] **4.4** Production concerns: token/cost handling, retries, timeouts, error handling _(DONE)_
- [x] **4.5** Wire AI into Cortex — grounded document Q&A (RAG-lite) _(DONE)_ **← Phase 4 COMPLETE**

### Phase 5 — RAG + LangChain · 8 sessions

- [x] **5.1** Embeddings — what they are, how similarity search works _(DONE)_
- [x] **5.2** Chunking strategies (size, overlap, semantic) + trade-offs _(DONE)_
- [x] **5.3** Vector DB — **pgvector** setup, `document_chunks` table, ingestion pipeline _(DONE)_
- [x] **5.4** Retrieval — nearest-neighbor search (cosine, top-k, owner-scoped) _(DONE)_
- [x] **5.5** The full **RAG pipeline** end-to-end (retrieve → augment → generate + citations) _(DONE)_
- [ ] **5.6** **LangChain / LangGraph** — chains, orchestration
- [ ] **5.7** **RAG evaluation** — measuring answer quality, faithfulness
- [ ] **5.8** Building an **agent** with tools (function calling loop)

### Phase 6 — Ship It Like a Pro · 6 sessions

- [ ] **6.1** Testing I — pytest, async tests, `httpx` test client
- [ ] **6.2** Testing II — fixtures, DB test setup, **mocking the LLM**
- [ ] **6.3** **Docker** + docker-compose (app + Postgres + Redis)
- [ ] **6.4** CI/CD pipeline (lint, test, build on push)
- [ ] **6.5** Observability — logging, tracing LLM calls, metrics
- [ ] **6.6** Deployment + capstone polish → portfolio-ready

### Phase 7 — Performance, Scale & System Design · 3 sessions _(post-deploy capstone review)_

> A full pass back over the finished, deployed app with a **staff-engineer / system-design lens** — not building features, but auditing what we built: where it's slow, where it breaks under load, how it scales. This is the interview-defining phase.

- [ ] **7.1** **Performance audit** — profile the hot paths; N+1 & slow queries; DB indexes (incl. pgvector ANN/`ivfflat`/`hnsw`); cache hit-rates; sync-in-async smells (e.g. `extract_text` blocking the loop)
- [ ] **7.2** **Scalability & system design** — how each tier scales (stateless API replicas, Celery worker fleet, Postgres read-replicas/pooling, Redis, the queue as backpressure); find the bottleneck; back-of-envelope capacity (RPS, embeds/min ceiling, storage growth); draw the architecture diagram
- [ ] **7.3** **Resilience & hardening** — failure modes & graceful degradation (LLM/DB/Redis down), timeouts/retries/circuit-breakers, rate-limit & abuse protection everywhere, idempotency, cost controls; write a short **system-design doc** (interview-ready)

---

## 📅 8-week timeline (starting Fri, Jul 3, 2026)

| Week  | Dates (2026)    | Focus                                 | Milestone                                                 |
| :---: | --------------- | ------------------------------------- | --------------------------------------------------------- |
| **1** | Jul 3 – Jul 9   | Finish Phase 0 → Phase 1 (1.1–1.4)    | Async understood; Cortex routes take shape                |
| **2** | Jul 10 – Jul 16 | Phase 1 (1.5–1.6) → Phase 2 (2.1–2.3) | **API skeleton runs**; DB + migrations live               |
| **3** | Jul 17 – Jul 23 | Phase 2 (2.4–2.6) → Phase 3 (3.1–3.2) | Persistent users/docs; **login works**                    |
| **4** | Jul 24 – Jul 30 | Phase 3 (3.3–3.7)                     | RBAC, Redis, Celery, WebSockets in place                  |
| **5** | Jul 31 – Aug 6  | Phase 3 (3.8) → Phase 4 (4.1–4.4)     | Uploads working; **backend talks to Claude**              |
| **6** | Aug 7 – Aug 13  | Phase 4 (4.5) → Phase 5 (5.1–5.4)     | **AI chat in Cortex**; embeddings + retrieval             |
| **7** | Aug 14 – Aug 20 | Phase 5 (5.5–5.8)                     | **Full RAG + agent working end-to-end**                   |
| **8** | Aug 21 – Aug 27 | Phase 6 (6.1–6.6)                     | Tested, Dockerized, deployed → **portfolio-ready** 🎉\*\* |
| **9** | Aug 28 – Sep 3  | Phase 7 (7.1–7.3)                     | **System-design pass**: perf audited, scale + failure modes mapped, design doc written 🧭 |

> Buffer built in. If a topic needs an extra session, we take it — the calendar flexes.

---

## 🏆 Portfolio milestones (résumé bullets you'll earn)

1. **End of Phase 2** — Async FastAPI service with PostgreSQL, migrations, clean architecture.
2. **End of Phase 3** — Production-shaped API: JWT auth, RBAC, Redis, Celery, WebSockets.
3. **End of Phase 4** — LLM-powered backend with token streaming.
4. **End of Phase 5** — **Full RAG system** with vector search, citations, and an agent.
5. **End of Phase 6** — Tested, Dockerized, CI/CD, deployed — a complete AI SaaS backend.

---

## ✅ Progress log

| Date       | Session                      | Notes                                                                                                                                                                                                                                                                                                     |
| ---------- | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-07-03 | 0.1 Async & event loop       | Done. Saw the blocking trap live (`/fast` = 4.7s frozen vs 0.0015s free).                                                                                                                                                                                                                                 |
| 2026-07-04 | 0.2 Type hints & Pydantic    | Done. Type hints are enforced by Pydantic (coercion, constraints, nested models). Built a Cortex `Document` model. Learned: coercion (`"30"`→`30`), optional needs a default, constraints are opt-in.                                                                                                     |
| 2026-07-04 | 0.3 Structure & tooling      | Done. Layered `app/` package, ruff lint/format, pinned `requirements.txt`, `.gitignore`, git init + first commit. Cortex boots: `GET /health` → `{"status":"ok"}`, auto OpenAPI docs. **Phase 0 complete.**                                                                                               |
| 2026-07-04 | 1.1 Path/query/body params   | Done. Built first real endpoints (POST/GET documents, in-memory store). Learned the 3-door rule, required-vs-optional (default decides), auto-422. Side lessons: `global` (reassign vs mutate), dict comprehension.                                                                                       |
| 2026-07-06 | 1.2 Request/response schemas | Done. Split into `DocumentBase`/`DocumentCreate`/`DocumentResponse`; added `response_model` + `status_code=201`; list returns JSON array; 404 via HTTPException (taste of 1.5). Proved response_model filters out undeclared fields (password_hash demo).                                                 |
| 2026-07-06 | 1.3 Dependency Injection     | Done. Added `pagination_params` + `get_document_or_404` deps via `Annotated[T, Depends(fn)]`; refactored GET endpoints. Learned: deps are functions, their params resolved by three-door rule + hoisted to OpenAPI, can raise, sub-deps, testability via override.                                        |
| 2026-07-07 | 1.4 Routers & structure      | Done. Moved document endpoints + deps + store into `app/api/documents.py` (`APIRouter`, prefix `/documents`, tag); `main.py` now thin assembler w/ `include_router`. Hit real bug (`word_Count` typo) that lint missed → lesson: green lint ≠ working; test behavior.                                     |
| 2026-07-07 | 1.5 Error handling           | Done. Added `app/core/exceptions.py` (`CortexError`/`DocumentNotFoundError`), registered `@app.exception_handler` in main.py, dependency now raises domain error (HTTP-agnostic). Learned status codes (401 vs 403 etc.), custom exception classes (`self.x`/`super().__init__`), automatic 422.          |
| 2026-07-08 | 1.6 Complete CRUD (finale)   | Done. Added `DocumentUpdate` schema + `PUT`/`DELETE` endpoints reusing `get_document_or_404`; `model_copy(update=...)`, 204 for delete. Full CRUD lifecycle verified end-to-end. Wrong `response_model` (`DocumentUpdate`) silently stripped fields → reinforced 1.2 filter lesson. **Phase 1 COMPLETE.** |

| 2026-07-08 | 2.1 Async SQLAlchemy setup | Done. Postgres 16 via Docker (`docker-compose.yml`), installed `sqlalchemy[asyncio]`+`asyncpg` (added to requirements.txt). Wrote `app/core/database.py` (engine, `async_sessionmaker`, `Base`, `get_db` yield dep). Verified live async connection (`SELECT version()`). Learned engine-vs-session lifecycle, import-time vs call-time. |

| 2026-07-08 | 2.2 ORM model (Document) | Done. Wrote `app/models/document.py` (`Document` model: `Mapped`/`mapped_column`, `String(200)`/`Text`/`ARRAY(String)`, `default` vs `server_default`, `DateTime(timezone=True)`, SERIAL PK). Printed generated `CREATE TABLE` DDL; confirmed no tables in DB yet (Alembic next). Learned `Mapped` nullability, defaults distinction, psql inspection. |

| 2026-07-08 | 2.3 Alembic migrations | Done. Installed alembic, `alembic init -t async`, wired `env.py` (Base.metadata, import models, DATABASE_URL). Autogenerated + `upgrade head` → `documents` table created in Postgres (verified via psql `\d documents`). Learned two-phase revision-vs-upgrade, revision chain, model-import gotcha, `alembic_version`, SERIAL/nextval. |

| 2026-07-11 | 2.4 Repository + wire to DB | Done. Created `app/repositories/document.py` (add/commit/refresh/get/select/delete), rewrote `app/api/documents.py` to use `get_db` + repo (deleted `_documents` dict & `_next_id`), added `ConfigDict(from_attributes=True)`. Full CRUD now persists to Postgres (verified row in psql). Learned session API, unit-of-work update, per-request session caching (shared session for sub-deps). Bugs found: `async_session_maker` missing `()`; `is_publsihed` typo in response schema (always returns false until fixed). |

| 2026-07-11 | 2.5 Transactions & unit-of-work | Done. Concept-heavy: transactions/atomicity/ACID, commit vs rollback, provisional-until-commit (flush at commit), session=unit-of-work (new/dirty/deleted), per-request transaction boundary in `get_db`. Proved atomicity with `scratch_tx.py` (error before commit → not persisted; two adds → one batched INSERT + commit). |

| 2026-07-11 | 2.6 Relationships (one-to-many) | Done. Added `app/models/user.py` (User: email unique+index, hashed_password); added `owner_id` nullable FK + `owner`/`documents` relationships (`back_populates`); `app/models/__init__.py` registers both; env.py imports package. Migration `d7eba3eb9aa5` → `users` table + FK + indexes (verified psql). Deep-dived: FK vs relationship, circular imports + `TYPE_CHECKING`, runtime vs static/compile time, indexing trade-offs. |

| 2026-07-11 | 2.7 N+1 & eager loading | Done. Demoed N+1 with seeded users/docs + query counter: naive lazy loading scales with distinct related rows, `selectinload(Document.owner)` = flat 2 queries (`... WHERE id IN (owner_ids)`). Learned lazy vs eager, `selectinload` (to-many) vs `joinedload` (to-one), identity map (naive was 1+3=4 not 10), async forbids implicit lazy load (`MissingGreenlet`). **PHASE 2 COMPLETE.** |

| 2026-07-11 | 3.1 Password hashing + registration | Done. Installed `pwdlib[argon2]` + `pydantic[email]`. `app/core/security.py` (`hash_password`/`verify_password`, Argon2). `app/schemas/user.py` (`UserCreate` EmailStr+password, `UserResponse` no password). `app/repositories/user.py` (`get_by_email`, `create` hashes before store). `EmailAlreadyExistsError`→409 handler. `POST /users` register endpoint. Verified: 201, no hash leak, 409 dup, 422 validation. Learned hashing vs encryption, salt, slow algo, verify() reuses embedded salt. |

| 2026-07-12 | 3.2 JWT & login | Done. Installed `pyjwt`. JWT funcs in security.py (`create_access_token`/`decode_access_token`, HS256, 30min). `Token` schema, `app/api/auth.py` `POST /auth/login` (`OAuth2PasswordRequestForm`, verify_password, same 401 for both fail cases). `app/api/deps.py` (`oauth2_scheme`, `get_current_user`, `CurrentUser`), `user_repo.get_by_id`, protected `GET /users/me`. Full flow verified via curl. Deep dives: signed-not-encrypted, SECRET_KEY vs SIGNATURE, encoding vs encryption, real AES token (`Salted__`). Bugs: `response_class`→`response_model`, `tokenUrl="auth/logi"` typo (Swagger-only). |

| 2026-07-12 | 3.3 RBAC & ownership | Done. Added `role` to User (server_default "user") + migration. `require_admin`/`AdminUser` (composes get_current_user) + admin-only `GET /users` (`user_repo.list_all`). Documents scoped to owner: `owner_id=current_user.id` on create, list filters by owner, `get_owned_document_or_404` (404 missing / 403 not-yours); all doc routes require auth. Bootstrapped admin via SQL. Truncated all data (RESTART IDENTITY CASCADE). Verified full authz matrix (401/403/404, cross-user isolation) via curl. |

| 2026-07-13 | 3.4 Middleware & CORS | Done. Custom `@app.middleware("http")` timing middleware (X-Process-Time header on every response) + `CORSMiddleware` (allow localhost:3000). Learned middleware vs dependency, call_next pre/post, CORS is browser-enforced (curl never triggers it). Debug lesson: `curl -s` hides connection-refused (exit 7) — server was just down, code was fine. |

| 2026-07-16 | 3.5 Celery + Redis | Done. Added `redis:7` to docker-compose; installed `celery[redis]`. `app/worker.py` (Celery app, redis broker+backend, `process_document` task with time.sleep to simulate heavy work). `app/api/tasks.py` (`POST /tasks/process-document` → `.delay()` → 202 + task_id; `GET /tasks/{id}` → AsyncResult status/result). Ran worker `--pool=solo`; verified full flow PENDING→SUCCESS, API returns instantly. Learned broker/backend/worker arch, `.delay()` serialization (pass ids/primitives not sessions/ORM objects), 202 Accepted. |

| 2026-07-16 | 3.6 Redis caching & rate limiting | Done. `app/core/redis_client.py` (async `redis.asyncio` client, db 1, decode_responses). Caching: `GET /demo/expensive/{n}` cache-aside (get→miss→compute→set ex=30); verified 2s miss vs 0.02s hit (~85×). Rate limiting: `rate_limit` dep (INCR+EXPIRE fixed window, 429), applied via `dependencies=[Depends(...)]`; verified 5×200 then 429. Bug: `decode_response`→`decode_responses` typo (root cause hidden under misleading `IndexError: pop from empty list` — lesson: read chained tracebacks to the BOTTOM). |

| 2026-07-16 | 3.7 WebSockets & SSE | Done. `@router.websocket("/demo/ws/echo")` (accept + receive/send loop + WebSocketDisconnect) — verified echo via TestClient. SSE: `GET /demo/stream` async generator `yield f"data: {word}\n\n"` + `StreamingResponse(media_type="text/event-stream")` — verified words drip ~0.3s apart via `curl -N`. Learned WS (persistent, two-way) vs SSE (one-way server→client stream); this is the exact Phase 4 LLM token-streaming skeleton. |

| 2026-07-17 | 3.8 Config + file uploads | Done. `pydantic-settings`: `app/core/config.py` `Settings(BaseSettings)` + `.env` (gitignored); refactored database.py/security.py/redis_client.py/worker.py/alembic env.py to use `settings` (secrets out of code). File uploads: `POST /documents/upload` (`UploadFile`, validate size 413/encoding+empty 400, decode → DocumentCreate → owned doc). Verified app boots + JWT round-trip via settings + upload 201. Bugs: `model_string`→`model_config`, get_settings indented inside class. **PHASE 3 COMPLETE (3.1–3.8, 8 sessions).** |

| 2026-07-18 | 4.1 Calling the LLM (Gemini) | Done. Chose **Google Gemini** (free tier) as the provider — `google-genai` SDK. `app/core/llm.py` async client, `app/schemas/chat.py`, `app/services/chat.py` (`generate_reply` → `await gemini.aio.models.generate_content`), `app/api/chat.py` `POST /chat` (auth + rate_limit). Working end-to-end — Cortex gets real LLM replies. Gotcha: `gemini-2.0-flash` had 0 free quota on the day-old account (429 `limit:0`); `gemini-flash-latest` works. Lesson: LLM is a swappable component behind the service layer. |

| 2026-07-18 | 4.2 Streaming LLM over SSE | Done. `chat.py` service `stream_reply` async generator (`async for chunk in await gemini.aio...generate_content_stream`, `yield chunk.text`); `POST /chat/stream` endpoint `event_generator` → `data: {json.dumps(token)}\n\n` + `[DONE]` via `StreamingResponse`. Verified drip via `curl -N` (server relays 2 streams: `async for` in ← Gemini, `yield` out → client). Deep-dived chunked transfer encoding / ASGI more_body / buffering. Gotcha: looked "all at once" in `/docs` (Swagger can't render SSE) — use `curl -N`. |

| 2026-07-18 | 4.3 Prompt design + structured output | Done. Added `system_instruction` (Cortex persona) via `types.GenerateContentConfig`. Structured output: `app/schemas/analysis.py` `DocumentAnalysis`, `app/services/analysis.py` (`response_schema=DocumentAnalysis` → `response.parsed`), `POST /documents/{id}/analyze` (composes owned-doc dep + rate_limit + service). Verified: analyzed a real doc → clean validated JSON {summary, tags[], key_points[]}. Learned system vs user message, why schema-enforced output beats prompt-and-parse. |

| 2026-07-19 | 4.4 Production concerns | Done. `chat.py` `_generate` wrapper: `asyncio.timeout(30)` + retry loop (transient 429/500/503, exponential backoff `2**attempt`, break on 4xx) → `LLMError` on failure; `generate_reply` logs `usage_metadata`. `LLMError` domain exception + 503 handler. `logging.basicConfig(level=INFO, force=True)` in main.py. Verified: token log shows (total>prompt+output due to thinking tokens). Learned retry control-flow (return/break/loop-end), backoff, provider-error decoupling. |

| 2026-07-19 | 4.5 Grounded doc Q&A (finale) | Done. `app/schemas/qa.py` (AskRequest/AskResponse), `app/services/qa.py` (`answer_from_document` — stuffs doc + grounding system instruction), `POST /documents/{id}/ask` (owned-doc + rate_limit). Verified: grounded answer from a real doc; refuses out-of-doc questions. **Refactored** robust `generate()` wrapper into `app/core/llm.py` — chat/analyze/qa all share it (DRY, user's own catch). Learned grounding/trustworthiness + the stuffing limitation → Phase 5 RAG. **PHASE 4 COMPLETE (4.1–4.5).** Minor: consistent typos `analyze_document`/`answer_from_document` (run fine; optional rename). |

| 2026-07-19 | 5.1 Embeddings | Done. Concept lab (`scratch_embeddings.py`, deleted): embedded sentences via `gemini.aio.models.embed_content(model="gemini-embedding-001")` (3072-dim), computed cosine → related pairs 0.80/0.74 vs unrelated ~0.57. User grokked it deeply: embedding = coordinates of text as a point in N-dim meaning space; similar meaning = nearby points; cosine = angle; retrieval = nearest-neighbor. Key lesson: scores uncalibrated (unrelated≈0.57) → use top-K ranking, not a fixed threshold. |

| 2026-07-20 | 5.2 Chunking | Done. `app/services/chunking.py` `chunk_text(text, chunk_size=800, overlap=150)` (fixed-size char chunks, `start += chunk_size - overlap`). Verified via scratch (deleted): 288 chars → 4 chunks with visible overlap. Learned why chunk (blurry-average whole-doc vector, input limits, stuff-only-relevant), size trade-off, overlap purpose, and that char-based cuts mid-word → boundary-aware/recursive splitting is the upgrade (5.6). |

| 2026-07-20 | 5.3 pgvector + ingestion | Done. Swapped Docker image → `pgvector/pgvector:pg16`; installed `pgvector`; `app/models/chunk.py` `DocumentChunk` (Vector(768), owner-cascade FK); migration (manual `CREATE EXTENSION vector` + `Vector` import fix). Embeddings settings (gemini-embedding-001, dim 768). `embed_texts` (task_type RETRIEVAL_DOCUMENT) + `ingest_document` (chunk→embed→store, idempotent delete-first) + `POST /documents/{id}/ingest`. Ingested doc 3 → **62 chunks, 62 vectors, 768-dim** in pgvector. Refactored (user's catch) `_resilient` generic wrapper for both generate + embed. Hit real 429 (embed 100/min free limit — 62 chunks/ingest × retries) → lesson: throttle + Celery for ingestion. Bugs: FK `document`→`documents`, migration Vector import. |

| 2026-07-21 | 5.4 Retrieval | Done. `app/services/retrieval.py` `retrieve_chunks(session, query, owner_id, k)` — embed query (RETRIEVAL_QUERY) → `select(DocumentChunk, cosine_distance.label('distance')).join(Document).where(owner_id).order_by(distance).limit(k)`. `app/schemas/search.py` (SearchRequest/SearchResult), `POST /documents/search`. Verified: "fix N+1?" → N+1 chunks ranked by distance (0.255/0.283/0.287) — semantic match, not keywords. Learned cosine_distance builds SQL (not Python), lower=more similar, owner-scope = multi-tenant safety. Bugs: `{}` vs `()` around stmt; SearchRequest vs SearchResult in response_model. |

| 2026-07-23 | 5.5 Full RAG pipeline | Done. `app/services/rag.py` `answer_with_rag` (RETRIEVE top-k → relevance floor MAX_DISTANCE=0.45 → AUGMENT: stuff chunks w/ `[source doc:chunk]` labels + grounding system instruction → GENERATE via `generate()`) → returns (answer, chunks). `app/schemas/rag.py` (RagRequest/Citation/RagResponse), `app/api/rag.py` `POST /rag/ask`. Verified: relevant Q → grounded cited answer across docs; off-topic → "not found" + no citations (+ no LLM call). **Core RAG loop complete.** User caught "retrieved ≠ used" (phantom citations) → added relevance floor + short-circuit. Noted gold-standard: LLM reports used sources via structured output. |

| 2026-07-23 | 5.5b Auto-ingest + Celery-ify + PDF | Done (consolidation; ties 3.5+5.3). Real Celery task `ingest_document_task(doc_id)` in `app/worker.py`: sync task runs async work via `asyncio.run(_ingest_async(doc_id))` — opens its OWN `async_session_maker` session (no `get_db`), fetches doc, calls `insert_document`, `await engine.dispose()` in finally (connections bound to the event loop; fresh loop each task). Passes **doc_id (reference), not content** — don't put big payloads on the broker. Wired fire-and-forget `ingest_document_task.delay(id)` into create/upload/update; `/ingest` now a 202 re-ingest trigger (poll via `/tasks/{id}`). PDF support: `pip install pypdf`; `app/services/extraction.py` `extract_text(filename, bytes)` (PdfReader from BytesIO, `.pdf`→extract else UTF-8; empty→400 "no text"; = a hand-built "document loader"). Fixed latent bug `status.HTTP_413`→`HTTP_413_REQUEST_ENTITY_TOO_LARGE`. Verified: create/upload → 201 instant, worker chunks+embeds in bg; PDF ingests. Run: `celery -A app.worker.celery_app worker --loglevel=info` alongside uvicorn. Recall (correct): response returns in ms because embedding is offloaded to Celery — `.delay()` just enqueues to Redis. |

_(We'll tick boxes above and add rows here as we go.)_
