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

---

## 2.1 — Async SQLAlchemy setup

**Gotcha:** ORM = work with Python objects, SQLAlchemy translates to SQL. Three pieces:
**engine** (connection pool, created ONCE app-wide, connects lazily on first query),
**session** (unit-of-work, created fresh PER REQUEST, commit/rollback), **async driver**
(`asyncpg` + `create_async_engine`) so DB waits yield to the event loop (Phase 0). URL:
`postgresql+asyncpg://user:pass@host:port/db`. `async_sessionmaker(engine,
expire_on_commit=False)` (False so objects stay readable after commit → for responses).
`get_db` is a **yield dependency**: `async with session_maker() as s: yield s` → setup,
hand to endpoint, guaranteed close. `echo=True` logs generated SQL (great for learning).
`pip install` puts packages in `.venv`; must also add to `requirements.txt` or the venv
& source-of-truth drift. Module top-level code runs once at import; `def` body runs per call.

**❓ Q:** (1) Why `asyncpg` + async engine instead of a sync driver? (2) What's created
once app-wide vs fresh per request?

**A:** (1) A DB query is I/O (waiting); a sync driver blocks the event loop and freezes
the whole server (Phase 0). Async driver lets the wait yield so other requests flow.
(2) Engine + connection pool = once, app-wide; session = fresh per request (via `get_db`).

---

## 2.2 — ORM model (the Document table)

**Gotcha:** A model class = a DB table (`__tablename__`), each attr = a column. SQLAlchemy
2.0 style: `name: Mapped[type] = mapped_column(...)`. `Mapped[X]` marks it as a column,
carries the Python type (autocomplete/type-check) AND nullability (`Mapped[str]`=NOT NULL,
`Mapped[str | None]`=nullable). Simple types (int/bool/str) are inferred; a **list needs an
explicit type** → `ARRAY(String)` (Postgres-only). Always use `DateTime(timezone=True)` for
timestamps (else timezone-naive). `func.X()` = call SQL function X (general, not just dates).
**`default=` (Python-side, SQLAlchemy fills before INSERT, NOT in table DDL) vs
`server_default=` (DB-side, becomes `DEFAULT ...` in the table, DB fills it).** `primary_key=True`
on an int → Postgres `SERIAL` auto-increments (replaces the `_next_id` hack). Inspect DB:
`docker exec -it cortex-postgres psql -U cortex -d cortex` then `\dt`, `\d documents`.
Defining a model ≠ creating the table (that's Alembic, 2.3).

**❓ Q:** Both `word_count` (`default=0`) and `created_at` (`server_default=func.now()`)
have a default, but only one appears as `DEFAULT ...` in `CREATE TABLE`. Which, and why?

**A:** Only `created_at`. `server_default` is a DB-side default baked into the table DDL
(Postgres applies it). `default=0` is Python-side — SQLAlchemy fills it before the INSERT,
so it never reaches the table definition. Matters when a non-app writer inserts rows:
`server_default` still applies, `default` doesn't. Use `server_default` for DB-owned values
(timestamps); `default` for plain app values.

---

## 2.3 — Alembic migrations

**Gotcha:** Migrations = version control for the DB schema (like git commits for tables).
Two-phase: **`alembic revision --autogenerate -m "..."`** WRITES a migration file (compares
models vs DB, generates the diff — DB untouched) → review it → **`alembic upgrade head`**
EXECUTES pending migrations against the DB (runs `upgrade()`, actually creates/alters).
Each migration has `upgrade()`/`downgrade()` + a revision chain (`down_revision`). Setup:
`alembic init -t async alembic` (async template!), then in `env.py`: import `Base`,
**import your models** (side effect: registers them on `Base.metadata`), `target_metadata =
Base.metadata`, `config.set_main_option("sqlalchemy.url", DATABASE_URL)`. `alembic_version`
table tracks the applied revision. `SERIAL`/`nextval(seq)` = the auto-increment PK. Inspect
with psql `\dt` / `\d documents`. Autogenerate needs DB at head before making a new revision.

**❓ Q:** (1) `alembic revision --autogenerate` vs `alembic upgrade head`? (2) Why import
models in `env.py`?

**A:** (1) `revision --autogenerate` writes the migration FILE (the diff/plan; DB unchanged);
`upgrade head` RUNS the file(s) against the DB (creates/alters tables). (2) Models attach to
`Base.metadata` only when imported; without the import, `target_metadata` is empty and
autogenerate silently produces an empty migration (thinks no tables are needed).

---

## 2.4 — Repository pattern & wiring endpoints to the DB

**Gotcha:** Session API: `session.add(obj)` (stage insert) → `await session.commit()` (write)
→ `await session.refresh(obj)` (reload → get DB-generated `id`/`created_at`; commit also
expires attrs). `await session.get(Model, pk)` (fetch by PK or None); `select(Model)` +
`session.execute(...)` + `.scalars().all()` (query); `session.delete(obj)`. **Update = mutate
the attached ORM object's attrs then `commit()`** (no `add` — unit-of-work tracks changes).
**Repository pattern**: all DB access in `app/repositories/`, endpoints just orchestrate.
`ConfigDict(from_attributes=True)` on the response schema lets Pydantic read ORM object
attributes (else it only reads dicts → conversion breaks). Session injected by FastAPI via
`Annotated[AsyncSession, Depends(get_db)]`; **cached once per request** so `get_document_or_404`
and the endpoint share ONE session (needed for PUT/DELETE to commit the fetched object).
PUT = full replace → must send full body (partial = PATCH w/ `exclude_unset=True`).

**❓ Q:** (1) Why `session.refresh(doc)` after `commit()` in `create()`? (2) What breaks
without `from_attributes=True` on `DocumentResponse`?

**A:** (1) `id` (SERIAL) and `created_at` (server_default) are generated by Postgres during
INSERT; the Python object doesn't know them until reloaded. `refresh()` re-fetches them
(commit also expires attrs). (2) Pydantic can only read dicts by default; without
`from_attributes` it can't extract fields from an ORM object → returning the ORM object errors.

---

## 2.5 — Transactions, sessions & unit-of-work

**Gotcha:** A **transaction** = a group of DB ops that all succeed or all fail (**atomicity**,
the "A" in ACID: Atomicity/Consistency/Isolation/Durability). `commit()` = make permanent &
visible; `rollback()` = discard everything since BEGIN. Changes are **provisional until commit**
— the `INSERT`/`UPDATE` SQL is only emitted at commit (the *flush*), so an error before commit
means the DB never even saw it. The **session = unit of work**: tracks New (`add`→INSERT),
Dirty (mutated attached objs→UPDATE), Deleted (`delete`→DELETE) and flushes them together in
one transaction. That's why `update()` needs no `add()` — mutating a tracked object marks it
dirty. `get_db`'s `async with ... session` defines the per-request transaction boundary:
success→your commit persists; error before commit→session closes→rolled back (no partial writes).
`session.scalar(select(...))` returns one value. `func.count()` → SQL `COUNT()`.

**❓ Q:** (1) In `update()`, no `session.add()` — how does SQLAlchemy know to emit an UPDATE?
(2) Exception after `add()` but before `commit()` — is the row in the DB? Why?

**A:** (1) Mutating an *attached* object marks it **dirty**; the unit-of-work sees the dirty
object at `commit()` and emits the UPDATE. (2) No — every session runs in a transaction;
without `commit()` the changes are provisional and roll back when the session closes on error
(the INSERT is never even flushed).

---

## 2.6 — Relationships (one-to-many)

**Gotcha:** One-to-many needs two pieces: **FK column** (`owner_id: Mapped[int|None] =
mapped_column(ForeignKey("users.id"), index=True)`) — the *stored* link, enforced by the DB —
and **`relationship()`** — Python-only navigation, NOT a stored column. `owner` (on Document,
the "many" side) fetches the one User at access time via owner_id; `documents` (on User, the
"one" side) is the list of that user's docs. `back_populates="..."` on both ends keeps them in
sync. **The FK lives on the "many" side.** Only `owner_id` is stored; `owner` is derived (this
is what causes N+1 — next session). Made `owner_id` **nullable** because existing doc rows have
no owner → a NOT NULL column would fail the migration (tighten in Phase 3 w/ auth).
Cross-file relationships → circular import: guard the type-only import with `if TYPE_CHECKING:`
(False at runtime, so skipped) + string annotation `Mapped["User"]` (SQLAlchemy resolves later
from its registry). Register BOTH models in `app/models/__init__.py` so the registry + Alembic
see them. Runtime vs static: Python runs `import`/`class` line-by-line AT RUNTIME; type hints
are for static checkers only (ignored at runtime), so a TYPE_CHECKING import never executes.
`email` unique+index (login lookups); index only columns you query by (indexes cost write speed+storage).

**❓ Q:** (1) `owner_id` column vs the `owner`/`documents` relationship attributes? (2) Why is
`owner_id` nullable for now?

**A:** (1) `owner_id` = stored FK column (integer → users.id, enforced by DB). `owner`/`documents`
are `relationship()` attributes — not stored; navigable in Python, fetched at query time. `owner`
(on Document) → the one User; `documents` (on User) → many Documents. FK lives on the many side.
(2) Existing document rows have no owner_id; adding a NOT NULL column fails on that existing data
→ nullable now, NOT NULL in Phase 3 once auth sets the owner.

**Doubts cleared this session:**

- **Runtime vs compile/static time (Python):** Python has only a tiny compile step (syntax →
  bytecode; no name/type checks). `import`, `def`, `class` are **executable statements that run
  at RUNTIME**, top-to-bottom. Type hints are ignored at runtime — they exist only for **static
  checkers** (mypy/IDE), a separate optional step *before* running. Three moments: bytecode-compile
  (syntax only) → static type-check (reads hints, optional) → runtime (imports run, hints ignored).

- **Why circular imports crash (single-threaded!):** nothing loads "in parallel." Imports run
  sequentially, but Python caches a **half-initialized** module in `sys.modules` the moment it
  starts loading. If A (mid-load) imports B, and B imports A, Python returns the *half-done* A —
  the class isn't defined yet → `ImportError`. It's re-entrancy, not threads.

- **How `if TYPE_CHECKING:` fixes it:** `TYPE_CHECKING` is `False` at runtime, so the block is
  skipped like `if False:` — the import **never executes**, so no jump to the other file, no
  circle. The annotation is a **string** (`Mapped["User"]`), so runtime never needs the import;
  SQLAlchemy resolves the name later from its registry. Escape hatches for circular imports:
  (1) `TYPE_CHECKING` for type-only imports, (2) import inside a function, (3) move shared code
  to a 3rd module.

- **Indexes — why only some columns:** an index speeds up reads on that column but **slows writes**
  (every insert/update maintains it) and **costs storage**. So index only columns you search/join
  by: `id` (PK, auto), `email` (login lookups), `owner_id` (FK, "docs for this user"). Not
  `title`/`content` (never looked up by them). Composite indexes (multi-column) exist too.

- **Do we store both `owner` and `owner_id`? NO.** Only `owner_id` is a real DB column. `owner`
  is a `relationship()` — not stored; accessing `doc.owner` runs a query (`SELECT user WHERE
  id=owner_id`) at that moment. `owner` is *derived* from `owner_id`. (This lazy "query on access"
  is what causes N+1.)

- **"many side" vs attribute direction (comment clarification):** two different labels — the
  MODEL: `User`=one side, `Document`=many side (**FK lives on the many side**); the ATTRIBUTE:
  `owner` points to the ONE user (to-one), `documents` points to MANY docs (to-many). Both true,
  different levels.

---

## 2.7 — N+1 problem & eager loading (Phase 2 finale)

**Gotcha:** **N+1** = 1 query for the list + **N** extra queries (one per item) to lazily load
each item's related object (`d.owner` in a loop). Scales with the number of **distinct** related
rows → melts the DB at scale. **Lazy** loading = fetch related on access (one-at-a-time). **Eager**
loading = fetch related up front in bulk. Fix: `select(Document).options(selectinload(Document.owner))`
→ 2 queries flat: (1) `SELECT documents`, (2) `SELECT users WHERE id IN (<owner_ids>)`. The
`owner_id`s ride along free as a column on the loaded docs; selectinload reads them from memory,
dedupes, fires ONE `IN` query, matches owners back. **`joinedload` for to-one (single JOIN),
`selectinload` for to-many (second IN query)** — rule of thumb. Async bonus: touching an
un-loaded relationship raises `MissingGreenlet` (no implicit lazy IO) → forces explicit eager
loading. **Identity map**: session caches loaded objects by PK, so repeated lookups of the same
id within a session don't re-query (why the demo was 1+3=4, not 1+9). FK index makes the `IN`/join fast.

**❓ Q:** (1) What is N+1 in one sentence? (2) How does `selectinload(Document.owner)` cut it to
2 queries — what's the 2nd query? (3) Why did the naive demo fire 4 queries, not 10?

**A:** (1) 1 query for the list + N extra queries (one per item) to load each item's related
object. (2) It eager-loads: after `SELECT documents`, it reads the owner_ids from the loaded docs
and fires ONE `SELECT * FROM users WHERE id IN (...)`, matching owners back in memory → 2 total.
(3) The session **identity map** cached each User by PK; 9 docs had only 3 distinct owners, so
only 3 owner-queries ran (1 + 3 = 4).

---

## 3.1 — Password hashing & registration

**Gotcha:** NEVER store plaintext passwords. Store a **hash** (one-way, irreversible) — unlike
encryption (two-way). Login = hash the entered password and compare to stored hash; you never
un-hash. Plain fast hashes (SHA-256) are brute-forceable + rainbow-tableable, so use: **salt**
(random per-password value, kills rainbow tables + makes identical passwords hash differently;
stored alongside the hash) + a **slow/memory-hard algorithm** (**Argon2**/bcrypt — ~0.1s, makes
mass brute force impractical). `pwdlib` (`PasswordHash.recommended()` = Argon2) does salt+algo
automatically and packs `$argon2id$...$salt$hash` into one self-describing string.
**`verify()` doesn't re-hash & string-compare** — it extracts the salt FROM the stored hash,
re-hashes the input with that same salt, and compares (that's why same-password hashes look
different yet verify True). Registration: `UserCreate` (email `EmailStr`, password) → repo hashes
before storing → `UserResponse` has NO password field (response_model allow-list = hash can't
leak). Duplicate email → `EmailAlreadyExistsError` → 409. `scalar_one_or_none()` for at-most-one.
No migration needed (only app code, User table already existed).

**❓ Q:** (1) Same password hashed twice → 2 different strings; how does `verify()` still return
True? (2) Why a *slow* algorithm for passwords? (3) Why can't the hash leak in the response?

**A:** (1) `verify()` reads the salt embedded in the stored hash, re-hashes the input with THAT
salt (not a fresh one), and compares → same password reproduces the stored hash. (2) Slow +
memory-hard makes brute-forcing stolen hashes impractical (thousands/sec, not billions); ~0.1s is
invisible to real users. (3) `response_model=UserResponse` is an allow-list — FastAPI serializes
through it, and it doesn't declare `hashed_password`, so that field is dropped on output.

**Why plain hashing (e.g. SHA-256) fails — 2 problems, 2 fixes:**

- **Problem 1: too fast + rainbow tables.** Fast hashes (SHA-256) can be computed billions/sec on
  a GPU → brute force is cheap. Also **rainbow tables** (huge precomputed hash→password lookups)
  crack unsalted hashes instantly.
  → **Fix A — slow, memory-hard algorithm** (Argon2/bcrypt): deliberately ~0.1s + RAM-hungry, so
  an attacker gets thousands of guesses/sec instead of billions; rainbow tables can't be
  precomputed against it. Invisible to a real user logging in once.

- **Problem 2: identical passwords → identical hashes.** With plain hashing, two users who pick
  `"password123"` get the *same* hash → a leak reveals who shares passwords, and cracking one
  cracks all of them.
  → **Fix B — salt**: a random value generated *per password*, mixed in before hashing. Now the
  same password hashes *differently* for every user → kills rainbow tables (can't precompute for
  every possible salt) and hides shared passwords. The salt isn't secret — it's stored right in
  the hash string; its only job is to be **unique per password**.

Argon2 (via pwdlib) applies BOTH fixes automatically: generates a random salt + runs the slow
memory-hard algorithm, packing algo+params+salt+hash into one self-describing string.

---

## 3.2 — JWT & login

**Gotcha:** HTTP is stateless → after login, prove identity each request with a **token**. **JWT**
= `header.payload.signature` (dot-separated base64). **Signed, NOT encrypted** — anyone can
base64-decode & READ the payload (never put secrets in it); the signature only proves it's
authentic + untampered. **SECRET_KEY** (server-only, never in token) signs & verifies the
**SIGNATURE** (in the token, public). Reading needs no key (base64 = encoding, not encryption);
**forging** needs the secret → that's the real protection (threat = forgery/impersonation, not
reading). Flow: `POST /auth/login` (form data via `OAuth2PasswordRequestForm`; field is `username`
but holds email) → `verify_password` → `create_access_token` (sub=user id, exp) → returns
`{access_token, token_type}`. Same 401 for "no user" and "wrong password" (no email-enumeration
leak). `get_current_user` dependency: `OAuth2PasswordBearer` extracts Bearer token → `jwt.decode`
(verifies sig+expiry) → load user; any failure → 401. `CurrentUser = Annotated[User,
Depends(get_current_user)]` → add to any endpoint to require login. `tokenUrl` is ONLY a Swagger
hint (where its Authorize button posts) — not used in real verification. `response_model` (Pydantic
shape) ≠ `response_class` (Response type like JSONResponse). Not-a-JWT tokens: `eyJ...` = JWT;
`U2FsdGVkX18` (=`Salted__`) = AES-encrypted (JWE/custom), unreadable without key.

**❓ Q:** (1) Why can Cortex be stateless yet know who you are each request? (2) Three failure
cases in `get_current_user` that all → 401? (3) Why does it being a dependency make protecting
any endpoint trivial?

**A:** (1) The token travels with each request; server verifies its signature + reads the user id
from it → nothing stored server-side. (2) i. `decode` raises (bad/expired/tampered/malformed sig),
ii. token decodes but has no `sub`, iii. token valid but user not in DB (deleted). All → vague 401.
(3) It's a dependency, so protecting an endpoint = adding one param (`current_user: CurrentUser`);
auth logic written once, reused everywhere, composable (e.g. `require_admin` builds on it),
overridable in tests — and it also hands you the authenticated user.

**Doubts cleared this session:**

- **How can I read a JWT payload with no secret?** Because reading = **base64 *decoding*, not decryption.**
  base64 is just a reversible text encoding (for safe transport), no key involved. The JWT payload
  is plain base64-encoded JSON — never hidden. Only the *signature* involves the secret.

- **SECRET_KEY vs SIGNATURE:** SECRET_KEY = secret string, **server-only, never in the token**, used
  to create & verify signatures. SIGNATURE = 3rd part of the JWT, **in the token, public**, computed
  as `HMAC(header+payload, SECRET_KEY)`. You can *see* the signature but can't *reproduce* it without
  the secret.

- **If anyone can decode a JWT, what's the point of the secret?** The point isn't secrecy — it's
  **unforgeability.** Threat = someone sending `sub:1` to impersonate the admin, NOT someone reading
  their own `sub:4`. Without a signature, anyone could fabricate `{"sub":"1"}` and the server couldn't
  tell. The signature (made with the secret) lets the server verify "did I actually issue this exact
  token, unchanged?" Change the payload → signature no longer matches → rejected. Hide the secret
  because if it leaks, attackers can mint valid tokens for any user. **JWT = unforgeable ID badge,
  not secret message** (like a banknote: readable, but you can't print your own).

- **Why couldn't I decode a real token from another site?** It started with `U2FsdGVkX18` (= `Salted__`)
  → it's **AES-encrypted** (CryptoJS/OpenSSL), not a JWT. A JWT starts with `eyJ` (= `{"`) and has 2
  dots (`header.payload.signature`). That site *encrypted* its token (contents hidden, needs key),
  vs a signed JWT (readable). Sign = integrity only; encrypt (JWE/AES) = also confidential. Not every
  "token" is a JWT.

---

## 3.3 — Roles (RBAC) & document ownership

**Gotcha:** Authentication (who are you → 401) vs Authorization (allowed? → 403). Two authz kinds:
**RBAC** (role gate) + **ownership** (own-your-resource). Added `role` to User
(`String(20), default="user", server_default="user"` — server_default backfills existing rows so
the NOT NULL migration doesn't fail). **Dependency composition**: `require_admin` depends on
`get_current_user` → runs authenticate FIRST (401), then role check (403); reuses all token logic.
`AdminUser`/`CurrentUser` aliases → gate any route with one param. Ownership: stamp
`owner_id=current_user.id` on create; `list` filters to `owner_id==current_user.id`;
`get_owned_document_or_404` = **404 if missing, 403 if exists-but-not-yours** (composes get_current_user
too). Bootstrapping the first admin: do it via direct SQL (`UPDATE users SET role='admin'...`) — a
public promote endpoint = privilege escalation; admin-granting must be admin-only → chicken-and-egg
for the first one. `TRUNCATE t1, t2 RESTART IDENTITY CASCADE` wipes data + resets id sequences (CASCADE
needed for FK; leave alembic_version alone).

**❓ Q:** (1) Advantage of `require_admin` composing `get_current_user`, and the 401-then-403 order?
(2) Why 404 in one case and 403 in another in `get_owned_document_or_404`? (3) Why grant admin via
SQL, not an endpoint?

**A:** (1) Token logic is written once in `get_current_user` and reused (no rewriting/re-handling
errors); the chain runs authenticate first → 401 if that fails, then the role check → 403. (2) 404 =
document doesn't exist; 403 = it exists but you don't own it (different questions, different codes).
(3) A public make-admin endpoint lets anyone self-promote; admin-granting must be admin-only, which
can't grant the FIRST admin (chicken-and-egg) → bootstrap directly in the DB.

---

## 3.4 — Middleware, CORS & request context

**Gotcha:** **Middleware** wraps EVERY request/response (runs before routing/deps and after the
endpoint). For cross-cutting concerns: logging, timing, headers, CORS, compression. Custom:
`@app.middleware("http")` async fn `(request, call_next)` → code before `call_next` = pre-processing,
`response = await call_next(request)` runs the rest of the chain (deps + endpoint), code after =
post-processing, then `return response`. **Middleware vs dependency**: middleware = every request,
wraps the cycle, can't inject values → use for global infra; dependency = selective, **returns a
value into the endpoint** (session, current_user) → use for auth/DB/validation. **CORS** = browser
same-origin policy blocks JS on origin A from calling API on origin B unless the API returns
`Access-Control-Allow-Origin`. `CORSMiddleware(allow_origins=[...], allow_credentials, allow_methods,
allow_headers)`. **CORS is enforced by the BROWSER, not the server** → curl/Postman never trigger it
(that's why our curl tests never hit CORS). Non-simple requests → browser sends a preflight `OPTIONS`.
Debug tip: with `curl -s`, connection-refused and "header missing" both print nothing → drop `-s` to
see `curl: (7) Failed to connect` vs a real response.

**❓ Q:** (1) Why is timing a good fit for middleware but auth better as a dependency? (2) What does
`await call_next(request)` do, and what runs before vs after? (3) Why did curl tests never hit CORS?

**A:** (1) Timing applies to every request → middleware; auth is selective AND must return the user
object into the endpoint → dependency (middleware can't inject values). (2) It passes the request to
the next middleware/eventually the route handler and returns the Response; before = pre-processing
(on the way in), after = post-processing (on the way out). (3) CORS is enforced by the browser, not
the server; curl isn't a browser, so it ignores CORS entirely.
