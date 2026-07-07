# 🚀 FastAPI → AI Software Engineer Roadmap

> **Goal:** Reach the depth of a 2–3 YOE **AI software engineer** — not surface-level CRUD.
> **Method:** Concept-first → build → review → "why?" check. One focused chunk per session.
> **Vehicle project:** **Cortex** — an AI Knowledge Assistant (document Q&A SaaS backend:
> users upload docs → chat with an AI that answers *from their docs* with citations).

---

## ⏱️ Time budget & cadence

| | |
|---|---|
| Weekdays | 2 hrs/day → **1 session/day** |
| Weekends | 4 hrs/day → **2 sessions/day** |
| Weekly capacity | **18 hrs ≈ 9 sessions/week** |
| Session length | ~2 hrs (concept + build + review) |
| Total course | **~42 sessions · ~84 focused hours** |
| Realistic calendar | **~8 weeks** (buffer for practice, debugging & revision) |

> A "session" = one 2-hr block. On weekends you'll do 2 per day. The timeline below
> already bakes in slack for real life — don't rush; depth > speed.

---

## 🗺️ The 7 phases at a glance

| Phase | Theme | Sessions | Hours |
|------|-------|:--------:|:-----:|
| 0 | Foundations (async, typing, tooling) | 3 | 6 |
| 1 | FastAPI core (Pydantic, DI, routers) | 6 | 12 |
| 2 | Data & persistence (async SQLAlchemy, Alembic) | 6 | 12 |
| 3 | Advanced backend (auth, Celery, Redis, WebSockets) | 8 | 16 |
| 4 | LLM integration (Claude API, streaming, tools) | 5 | 10 |
| 5 | RAG + LangChain (embeddings, pgvector, agents) | 8 | 16 |
| 6 | Ship it (testing, Docker, CI/CD, observability) | 6 | 12 |
| | **Total** | **42** | **84** |

---

## 📚 Phase-by-phase sessions

### Phase 0 — Foundations · 3 sessions
- [x] **0.1** Async & the event loop — sync vs async, the blocking trap *(DONE)*
- [x] **0.2** Type hints deep + intro to **Pydantic v2** (validation from types) *(DONE)*
- [x] **0.3** Project structure, tooling (git, `.gitignore`, ruff, `requirements.txt`) *(DONE)*

### Phase 1 — FastAPI Core · 6 sessions
- [x] **1.1** Path / query / body params; request lifecycle *(DONE)*
- [x] **1.2** Pydantic models: `response_model`, validation, serialization, config *(DONE)*
- [x] **1.3** **Dependency Injection** — the heart of FastAPI (`Depends`, sub-deps, yield deps) *(DONE)*
- [x] **1.4** Routers & scalable project structure (`APIRouter`, versioning) *(DONE)*
- [x] **1.5** Error handling — exceptions, handlers, status codes, validation errors *(DONE)*
- [ ] **1.6** OpenAPI/docs, tags, response models → **build the Cortex API skeleton**

### Phase 2 — Data & Persistence · 6 sessions
- [ ] **2.1** Async **SQLAlchemy 2.0** — engine, sessions, async setup with Postgres
- [ ] **2.2** Models & relationships (1-to-many, many-to-many)
- [ ] **2.3** **Alembic** migrations — autogenerate, upgrade/downgrade, workflow
- [ ] **2.4** Repository pattern & CRUD wired into DI
- [ ] **2.5** Transactions, session lifecycle, unit-of-work
- [ ] **2.6** Performance: N+1 problem, eager loading, indexing

### Phase 3 — Advanced Backend · 8 sessions
- [ ] **3.1** Auth I — password hashing, JWT creation/verification
- [ ] **3.2** Auth II — OAuth2 password flow, `get_current_user` dependency
- [ ] **3.3** Role-based access control (RBAC) & scopes
- [ ] **3.4** Middleware deep-dive, CORS, request context
- [ ] **3.5** Background tasks vs **Celery** workers + Redis broker
- [ ] **3.6** **Redis** caching & rate limiting
- [ ] **3.7** **WebSockets** & **SSE** streaming responses
- [ ] **3.8** File uploads → object storage, config/secrets (`pydantic-settings`), structured logging

### Phase 4 — LLM Integration · 5 sessions
- [ ] **4.1** Calling the **Claude API** from a backend (SDK, messages, params)
- [ ] **4.2** **Streaming** tokens to the client over SSE
- [ ] **4.3** Prompt design + **structured outputs / tool use**
- [ ] **4.4** Production concerns: token/cost handling, retries, timeouts, error handling
- [ ] **4.5** Wire real AI chat into Cortex

### Phase 5 — RAG + LangChain · 8 sessions
- [ ] **5.1** Embeddings — what they are, how similarity search works
- [ ] **5.2** Chunking strategies (size, overlap, semantic) + trade-offs
- [ ] **5.3** Vector DBs — **pgvector** setup & queries (+ Chroma overview)
- [ ] **5.4** Retrieval — top-k, filtering, hybrid search, reranking
- [ ] **5.5** The full **RAG pipeline** end-to-end (ingest → retrieve → generate + citations)
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

---

## 📅 8-week timeline (starting Fri, Jul 3, 2026)

| Week | Dates (2026) | Focus | Milestone |
|:----:|--------------|-------|-----------|
| **1** | Jul 3 – Jul 9 | Finish Phase 0 → Phase 1 (1.1–1.4) | Async understood; Cortex routes take shape |
| **2** | Jul 10 – Jul 16 | Phase 1 (1.5–1.6) → Phase 2 (2.1–2.3) | **API skeleton runs**; DB + migrations live |
| **3** | Jul 17 – Jul 23 | Phase 2 (2.4–2.6) → Phase 3 (3.1–3.2) | Persistent users/docs; **login works** |
| **4** | Jul 24 – Jul 30 | Phase 3 (3.3–3.7) | RBAC, Redis, Celery, WebSockets in place |
| **5** | Jul 31 – Aug 6 | Phase 3 (3.8) → Phase 4 (4.1–4.4) | Uploads working; **backend talks to Claude** |
| **6** | Aug 7 – Aug 13 | Phase 4 (4.5) → Phase 5 (5.1–5.4) | **AI chat in Cortex**; embeddings + retrieval |
| **7** | Aug 14 – Aug 20 | Phase 5 (5.5–5.8) | **Full RAG + agent working end-to-end** |
| **8** | Aug 21 – Aug 27 | Phase 6 (6.1–6.6) | Tested, Dockerized, deployed → **portfolio-ready** 🎉** |

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

| Date | Session | Notes |
|------|---------|-------|
| 2026-07-03 | 0.1 Async & event loop | Done. Saw the blocking trap live (`/fast` = 4.7s frozen vs 0.0015s free). |
| 2026-07-04 | 0.2 Type hints & Pydantic | Done. Type hints are enforced by Pydantic (coercion, constraints, nested models). Built a Cortex `Document` model. Learned: coercion (`"30"`→`30`), optional needs a default, constraints are opt-in. |
| 2026-07-04 | 0.3 Structure & tooling | Done. Layered `app/` package, ruff lint/format, pinned `requirements.txt`, `.gitignore`, git init + first commit. Cortex boots: `GET /health` → `{"status":"ok"}`, auto OpenAPI docs. **Phase 0 complete.** |
| 2026-07-04 | 1.1 Path/query/body params | Done. Built first real endpoints (POST/GET documents, in-memory store). Learned the 3-door rule, required-vs-optional (default decides), auto-422. Side lessons: `global` (reassign vs mutate), dict comprehension. |
| 2026-07-06 | 1.2 Request/response schemas | Done. Split into `DocumentBase`/`DocumentCreate`/`DocumentResponse`; added `response_model` + `status_code=201`; list returns JSON array; 404 via HTTPException (taste of 1.5). Proved response_model filters out undeclared fields (password_hash demo). |
| 2026-07-06 | 1.3 Dependency Injection | Done. Added `pagination_params` + `get_document_or_404` deps via `Annotated[T, Depends(fn)]`; refactored GET endpoints. Learned: deps are functions, their params resolved by three-door rule + hoisted to OpenAPI, can raise, sub-deps, testability via override. |
| 2026-07-07 | 1.4 Routers & structure | Done. Moved document endpoints + deps + store into `app/api/documents.py` (`APIRouter`, prefix `/documents`, tag); `main.py` now thin assembler w/ `include_router`. Hit real bug (`word_Count` typo) that lint missed → lesson: green lint ≠ working; test behavior. |
| 2026-07-07 | 1.5 Error handling | Done. Added `app/core/exceptions.py` (`CortexError`/`DocumentNotFoundError`), registered `@app.exception_handler` in main.py, dependency now raises domain error (HTTP-agnostic). Learned status codes (401 vs 403 etc.), custom exception classes (`self.x`/`super().__init__`), automatic 422. |

*(We'll tick boxes above and add rows here as we go.)*
