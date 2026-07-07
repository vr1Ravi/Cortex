# 📓 FastAPI Learning Notes

> Lean revision notes: just the **gotcha/trap** and a **recall question**.
> On revision, answer the question from memory *before* reading the answer.
> Answers are filled in only after your attempt has been checked.

---

## 0.1 — Async & the event loop

**Gotcha:** `await` only helps while *waiting* on I/O — never during CPU work.
`time.sleep(5)` (or a heavy computation) inside `async def` freezes the whole
server; `await asyncio.sleep(5)` does not.

**❓ Q:** Why can't `await` speed up a 3-second pure-CPU image resize, and what do
you do instead?

**A:** CPU work keeps the single thread busy the whole time — there's no idle
moment to switch on, and nothing awaitable. Move it off the loop: threadpool
(light work) or a separate process / Celery (heavy work).

---

## 0.2 — Type hints & Pydantic

**Gotcha:** Python ignores type hints at runtime — Pydantic reads and *enforces*
them. Also: a field is optional only if it has a **default**, NOT because its type
is `x | None`. `subtitle: str | None` is still REQUIRED; `subtitle: str | None = None`
is optional.

**❓ Q:** Given `age="30"` (a string) passed to a Pydantic model with `age: int`,
what does Pydantic do, and why is that behaviour useful for a web API?

**A:** It **coerces** it — converts `"30"` → `30`. Pydantic tries to convert first
and errors only when conversion is impossible (e.g. `"not-a-number"`). Useful because
web input (JSON, query params, forms) often arrives as strings, so you get real
Python types automatically without manual casting. Caveat: coercion is lenient by
default; use `Field(strict=True)` when you need the exact type.

---

## 0.3 — Project structure & tooling

**Gotcha:** Never commit `.venv/` or `.env` (secrets) — that's what `.gitignore` is
for; run `git status` before committing to confirm. Pin exact dependency versions
(`==`) so builds are reproducible. Keep code in layers (api / services / models)
instead of one giant `main.py`.

**❓ Q:** In FastAPI projects we keep "schemas" and "models" separate. What does each
represent, and why not just use a single class for both?

**A:** **Schema** (Pydantic) = the API shape — data going in/out over HTTP.
**Model** (SQLAlchemy) = the DB table shape. Kept separate because the three shapes
differ: (1) input omits server-generated fields like `id`/`created_at`; (2) output
must not leak columns like `password_hash`; (3) one DB model often maps to several
schemas (`Create`, `Update`, `Response`). One class can't safely serve all three roles.

---

## 1.1 — Path, query & body params

**Gotcha:** FastAPI decides each function param's "door" by rule, not config:
(1) name matches a `{placeholder}` in the path → **path** param; (2) type is a Pydantic
`BaseModel` → **request body**; (3) anything else (plain `int`/`str`/…) → **query**
param. A param with a default is optional, without a default is required (path params
are always required). Wrong type → automatic `422`, no validation code needed.
Also: `global` is only for *reassigning* a module var inside a function; *mutating*
an object (`dict[k]=v`) needs no `global`, and you never write `global` at module level.

**❓ Q:** For `@app.get("/documents/{doc_id}")` with the function
`async def get(doc_id: int, tag: str | None = None, limit: int = 10)`, classify each of
the three params as path / query / body, and say which are required vs optional and why.

**A:** `doc_id` = **path**, **required** (no default; also path params are always
required — they're part of the URL). `tag` = **query**, **optional** (the `= None`
default makes it optional — NOT the `| None`). `limit` = **query**, **optional**
(defaults to `10`). Rule: required-ness comes from having a default, not the type.

---

## 1.2 — Request & response schemas

**Gotcha:** Use a *family* of schemas, not one class: `Base` (shared) → `Create`
(what client sends, no server fields) → `Response` (what API returns, +id/timestamps).
Server-generated fields (`id`, `word_count`, `created_at`) go in `Response` only, so
clients can't set them. `response_model=` does 3 things: documents the output shape,
serializes it, and **filters** — returns ONLY declared fields, silently dropping
anything extra (security: a `password_hash` not in the response model CAN'T leak).
Import order (ruff `I`): stdlib group first, then third-party, blank line between.
Line-too-long inside a docstring/string is a manual fix (ruff won't reword strings).

**❓ Q:** (1) Why is `word_count` in `DocumentResponse` but not `DocumentCreate`?
(2) If a function returns an object with a field NOT declared in its `response_model`,
what does the client receive, and what guarantee does that give you?

**A:** (1) `word_count` is server-computed/derived — the client can't be trusted to
send it accurately, so it's not in `Create`. (2) The client receives ONLY the fields
declared in `response_model`; extras are silently dropped. Guarantee: the API can
never leak a field it hasn't declared (allow-list on output).

---

## 1.3 — Dependency Injection

**Gotcha:** A dependency is just a function; wire it with `Annotated[Type, Depends(fn)]`
(modern syntax). Don't fetch what you need — declare it, FastAPI provides it. A
dependency's OWN params are resolved by the same three-door rule against the route
(so `get_document_or_404(doc_id: int)` gets `doc_id` from the path), and its params
get hoisted onto the endpoint's OpenAPI. Dependencies can do logic and raise
(`HTTPException`), and can depend on other dependencies (sub-deps → whole tree
resolved). Benefits: reuse (DRY), cleaner endpoints, and **testability** (override a
dependency in tests to swap real DB for a fake). `yield` deps do setup/teardown (Phase 2 DB sessions).

**❓ Q:** (1) A dependency `get_document_or_404(doc_id: int)` gets `doc_id` filled
automatically — where from, and how does FastAPI decide? (2) Name one concrete benefit
of moving fetch-or-404 into a dependency vs inline.

**A:** (1) From the URL **path** — FastAPI pools the dependency's params with the
endpoint's and applies the three-door rule; `doc_id` matches the `{doc_id}` placeholder
in the route, so it's a path param. (2) Reusability (also: cleaner endpoints; testable
via dependency override).

---

## 1.4 — Routers & scalable structure

**Gotcha:** `APIRouter(prefix="/documents", tags=["documents"])` groups related routes
in their own file; write paths relative to the prefix (`""` → `/documents`, use `""`
not `"/"` to avoid a trailing-slash redirect). Mount with `app.include_router(...)` so
`main.py` stays a thin assembler. Big lesson: **green lint ≠ working code** — ruff
passed while a `word_Count` vs `word_count` typo broke the app, because the linter
checks syntax/style, not logic. Only *running* the code (or a test) catches wiring bugs.
(Also: debug by testing behavior — does the endpoint respond? — not internal attributes.)

**❓ Q:** (1) What does a router `prefix` save you, and why does splitting into routers
help as the app grows? (2) Why did `ruff check` pass while the app was still broken,
and what catches that class of bug?

**A:** (1) You write the base path once instead of on every decorator (change it in one
place); routers keep each domain in its own file with `main.py` as a thin assembler →
modular, no merge conflicts. (2) `word_Count` is valid Python, so the linter (syntax/
style only) had nothing to flag; only running the code / an automated test that
exercises the endpoint catches logic & wiring bugs.

---

## 1.5 — Error handling

**Gotcha:** Prefer **custom domain exceptions + a central handler** over raw
`HTTPException` in your logic: business code raises a pure concept
(`DocumentNotFoundError`), and one `@app.exception_handler(...)` maps it → HTTP
response app-wide. Keeps business logic HTTP-agnostic (works in jobs/tests too) and
makes errors consistent. Status codes: 400 bad request, **401 = don't know who you are
(authn)**, **403 = know you but not allowed (authz)**, 404 not found, 409 conflict,
422 validation (FastAPI does this automatically, reports ALL errors with loc/type/msg/
input). Exception classes are just classes: `self.x = x` stores data for the handler;
`super().__init__(msg)` sets the message so `str(exc)` works.

**❓ Q:** (1) Difference between 401 and 403? (2) Architectural benefit of moving the
404 from a raw `HTTPException` in the dependency to a domain exception + handler?

**A:** (1) 401 = not authenticated (server doesn't know who you are); 403 = authenticated
but not authorized (known, but access restricted). (2) Separation of concerns — business
logic raises a pure domain error and stays HTTP-agnostic (reusable in jobs/tests); the
HTTP mapping lives once in the web layer → consistent, reusable error handling.

---

## 1.6 — Completing CRUD (Phase 1 finale)

**Gotcha:** Set `status_code` only when it differs from the default `200`: POST→201,
DELETE→**204 No Content** (empty body), PUT→200 (default, returns updated resource).
PUT = full replace; PATCH = partial (`model_dump(exclude_unset=True)`). Reuse
`get_document_or_404` as a dependency in GET/PUT/DELETE → existence guarantee + consistent
404, no duplication. `existing.model_copy(update={...})` copies an object changing only
some fields (keeps id/created_at, swaps title/content/tags, recomputes word_count).
Pointing `response_model` at the wrong schema (e.g. `DocumentUpdate`) silently strips
fields with no error — same filter mechanism as 1.2. `summary=` sets the /docs label;
the docstring becomes the description.

**❓ Q:** (1) What two things does reusing `get_document_or_404` in PUT/DELETE give you?
(2) Why does DELETE return 204 while PUT returns 200?

**A:** (1) A guarantee the document exists (fetch) + consistent 404 handling, with zero
duplication (DRY). (2) DELETE has nothing to return (resource gone) → 204 empty body;
PUT succeeds AND returns the updated resource → 200.
