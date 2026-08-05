# 📓 FastAPI Learning Notes

> Lean revision notes: just the **gotcha/trap** and a **recall question**.
> On revision, answer the question from memory _before_ reading the answer.
> Answers are filled in only after your attempt has been checked.

---

## 0.1 — Async & the event loop

**Gotcha:** `await` only helps while _waiting_ on I/O — never during CPU work.
`time.sleep(5)` (or a heavy computation) inside `async def` freezes the whole
server; `await asyncio.sleep(5)` does not.

**❓ Q:** Why can't `await` speed up a 3-second pure-CPU image resize, and what do
you do instead?

**A:** CPU work keeps the single thread busy the whole time — there's no idle
moment to switch on, and nothing awaitable. Move it off the loop: threadpool
(light work) or a separate process / Celery (heavy work).

---

## 0.2 — Type hints & Pydantic

**Gotcha:** Python ignores type hints at runtime — Pydantic reads and _enforces_
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
Also: `global` is only for _reassigning_ a module var inside a function; _mutating_
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

**Gotcha:** Use a _family_ of schemas, not one class: `Base` (shared) → `Create`
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
checks syntax/style, not logic. Only _running_ the code (or a test) catches wiring bugs.
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
— the `INSERT`/`UPDATE` SQL is only emitted at commit (the _flush_), so an error before commit
means the DB never even saw it. The **session = unit of work**: tracks New (`add`→INSERT),
Dirty (mutated attached objs→UPDATE), Deleted (`delete`→DELETE) and flushes them together in
one transaction. That's why `update()` needs no `add()` — mutating a tracked object marks it
dirty. `get_db`'s `async with ... session` defines the per-request transaction boundary:
success→your commit persists; error before commit→session closes→rolled back (no partial writes).
`session.scalar(select(...))` returns one value. `func.count()` → SQL `COUNT()`.

**❓ Q:** (1) In `update()`, no `session.add()` — how does SQLAlchemy know to emit an UPDATE?
(2) Exception after `add()` but before `commit()` — is the row in the DB? Why?

**A:** (1) Mutating an _attached_ object marks it **dirty**; the unit-of-work sees the dirty
object at `commit()` and emits the UPDATE. (2) No — every session runs in a transaction;
without `commit()` the changes are provisional and roll back when the session closes on error
(the INSERT is never even flushed).

---

## 2.6 — Relationships (one-to-many)

**Gotcha:** One-to-many needs two pieces: **FK column** (`owner_id: Mapped[int|None] =
mapped_column(ForeignKey("users.id"), index=True)`) — the _stored_ link, enforced by the DB —
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
  checkers** (mypy/IDE), a separate optional step _before_ running. Three moments: bytecode-compile
  (syntax only) → static type-check (reads hints, optional) → runtime (imports run, hints ignored).

- **Why circular imports crash (single-threaded!):** nothing loads "in parallel." Imports run
  sequentially, but Python caches a **half-initialized** module in `sys.modules` the moment it
  starts loading. If A (mid-load) imports B, and B imports A, Python returns the _half-done_ A —
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
id=owner_id`) at that moment. `owner` is _derived_ from `owner_id`. (This lazy "query on access"
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
True? (2) Why a _slow_ algorithm for passwords? (3) Why can't the hash leak in the response?

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
  `"password123"` get the _same_ hash → a leak reveals who shares passwords, and cracking one
  cracks all of them.
  → **Fix B — salt**: a random value generated _per password_, mixed in before hashing. Now the
  same password hashes _differently_ for every user → kills rainbow tables (can't precompute for
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

- **How can I read a JWT payload with no secret?** Because reading = **base64 _decoding_, not decryption.**
  base64 is just a reversible text encoding (for safe transport), no key involved. The JWT payload
  is plain base64-encoded JSON — never hidden. Only the _signature_ involves the secret.

- **SECRET_KEY vs SIGNATURE:** SECRET_KEY = secret string, **server-only, never in the token**, used
  to create & verify signatures. SIGNATURE = 3rd part of the JWT, **in the token, public**, computed
  as `HMAC(header+payload, SECRET_KEY)`. You can _see_ the signature but can't _reproduce_ it without
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
  dots (`header.payload.signature`). That site _encrypted_ its token (contents hidden, needs key),
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

---

## 3.5 — Celery + Redis (background task queue)

**Gotcha:** Slow/heavy work (processing, embeddings, email, LLM calls) must NOT run in the request
(Phase 0: blocks/slows). Offload it. Two tools: **`BackgroundTasks`** = in-process, after-response,
light & disposable (no retries, dies with app) — for tiny fire-and-forget (email/log). **Celery** =
distributed task queue for heavy/reliable/scalable work. Architecture: FastAPI _pushes_ task →
**broker (Redis)** holds the queue → **worker (separate process)** pulls & _runs_ the code → writes
result to **backend (Redis)**. **Redis never executes code** — it's the middleman queue + result
store; the WORKER runs the task. `task.delay(args)` = serialize args to JSON, push to broker, return
INSTANTLY with a task_id (doesn't wait). Poll `AsyncResult(id)` → status PENDING/STARTED/SUCCESS/
FAILURE + result. Return **202 Accepted** for "accepted, processing async". Task args must be
**JSON-serializable → pass ids/primitives, NOT session/ORM/connections** (can't serialize across
processes); pattern = pass the id, task re-fetches (opens its own session). Celery tasks are plain
sync fns; blocking (`time.sleep`) is fine there (separate process, not the event loop). Run worker:
`celery -A app.worker worker --loglevel=info --pool=solo` (`--pool=solo` avoids macOS fork crash).

**❓ Q:** (1) The task took 5s but the POST returned instantly — where did the work run, and Redis's
role? (2) Why not pass a session/ORM object to a task; what instead? (3) BackgroundTasks vs Celery?

**A:** (1) The work ran in the **Celery worker process** (separate); Redis was only the broker
(passed the task to the worker) + backend (stored the result) — it doesn't run code. (2) Args must be
JSON-serialized to cross to another process; sessions/ORM/connections can't serialize → pass
ids/primitives and let the task re-fetch. (3) BackgroundTasks = light, quick, disposable, in-process;
Celery = heavy, slow, needs retries/reliability/scale, survives restarts.

---

## 3.6 — Redis caching & rate limiting

**Gotcha:** **Cache-aside**: check cache → HIT return it (fast) / MISS do the work, store with **TTL**,
return. TTL bounds staleness (speed vs freshness tradeoff); hardest part = invalidation. Async client:
`redis.asyncio.from_url(url, decode_responses=True)` (decode_responses → str not bytes; use db 1 to
separate from Celery's db 0). Cache: `get` → on None compute → `set(key, val, ex=SECONDS)`.
**Rate limiting** (fixed window): `INCR key` (atomic +1); if count==1 `EXPIRE key WINDOW`; if
count>LIMIT → **429**. `INCR` atomicity (Redis single-threaded) = no lost updates under concurrency.
Applied as a dependency via `@router.get(..., dependencies=[Depends(rate_limit)])` — decorator-level
`dependencies=[]` for **side-effect gates that return no value** (vs a param like `current_user` when
you need the return). Debug lesson: a chained traceback's ROOT cause is at the BOTTOM (the misleading
`IndexError: pop from empty list` hid the real `decode_response` typo — read past "direct cause of").

**❓ Q:** (1) Cache-aside flow (hit vs miss) + what's TTL for? (2) Why must `INCR` be atomic for rate
limiting? (3) Why `dependencies=[Depends(rate_limit)]` in the decorator vs a function parameter?

**A:** (1) HIT → serve the cached value; MISS → compute/query, store it with TTL, return. TTL =
how long the cache entry lives before expiring (bounds staleness). (2) Without atomicity, concurrent
requests can both read the same count and write the same +1 → increments get lost → users slip past
the limit. Atomic `INCR` counts every request. (3) `dependencies=[...]` in the decorator is for a
side-effect gate that returns no value; a function parameter is for when you need the returned value.

---

## 3.7 — WebSockets & SSE (streaming)

**Gotcha:** Normal HTTP = one request→one response→closes; can't push later. For live data:
**WebSocket** = persistent, **two-way** (both sides send anytime); `@app.websocket(...)` →
`await ws.accept()` then a `while True` receive/send loop (function stays alive for the whole
connection), handle `WebSocketDisconnect`. Use for chat/collab/real-time bidirectional. **SSE** =
**one-way** server→client stream over plain HTTP; client makes ONE request, server keeps it open and
flushes chunks. Build with an **async generator** (`yield f"data: {payload}\n\n"` — SSE frame =
`data:` + blank line) + **`StreamingResponse(gen(), media_type="text/event-stream")`**. BOTH pieces
needed: the generator/`yield` produces chunks incrementally, `StreamingResponse` flushes each to the
client instead of buffering. Test SSE with `curl -N` (disables buffering → see the drip). **This is the
exact Phase 4 LLM streaming skeleton** — swap the loop to `async for token in claude_stream(...)`.
SSE fits LLM streaming because token flow is one-directional (server→client); WebSocket would be
overkill (only needed if client must send mid-stream).

**❓ Q:** (1) WebSocket vs SSE — difference + when each? (2) Two things that make SSE stream
gradually? (3) Why SSE (not WebSocket) for streaming an LLM answer?

**A:** (1) WebSocket = persistent two-way (client & server both send); SSE = one-way server→client
stream, client only makes the initial request. WS for bidirectional (chat), SSE for server-push
(tokens, notifications). (2) The async generator with `yield` (produces chunks incrementally) AND
`StreamingResponse(media_type="text/event-stream")` (flushes each chunk as produced instead of
buffering the whole response). (3) The token stream is one-directional (server→client only), which is
exactly SSE's shape — simpler, plain HTTP, auto-reconnect; WS is overkill unless the client sends mid-stream.

---

## 3.8 — Config/secrets (pydantic-settings) & file uploads

**Gotcha:** Don't hardcode config/secrets — a committed `SECRET_KEY` lets anyone with repo access
forge JWTs. **12-factor**: config in **env vars** (from `.env` in dev, gitignored; real env vars in
prod). `pydantic-settings` `class Settings(BaseSettings)` with `model_config =
SettingsConfigDict(env_file=".env", extra="ignore")`; fields = env vars (case-insensitive:
`database_url` ← `DATABASE_URL`); no-default fields are **required** (fail fast if missing). `@lru_cache
get_settings()` parses once. **`model_config` is a RESERVED Pydantic name** (config) — any other name
(`model_string`) is read as a field → "non-annotated attribute" error. Solves: (1) secrets out of git,
(2) per-environment config with no code change. **File uploads** = `multipart/form-data` → `UploadFile`
param (has `.filename`, `.content_type`, `await .read()`; spooled to disk if large). ALWAYS validate
untrusted uploads: **size** (cap → 413, else DoS/memory), **type/encoding** (→ 400, else garbage
downstream), non-empty. Needs `python-multipart` (already installed).

**❓ Q:** (1) Why is a hardcoded SECRET_KEY dangerous + 2 problems `.env`/pydantic-settings solve?
(2) Why validate uploaded files (size/type)? (3) Why did `model_config` work but `model_string` fail?

**A:** (1) Committed secret → anyone with repo access can forge JWTs/impersonate users. Fixes:
secrets out of git (gitignored `.env`) + per-environment config without code changes. (2) Uploads are
untrusted input: cap size (else a huge file exhausts memory/disk = DoS → 413); check type/encoding
(else non-text/binary breaks processing → 400). (3) `model_config` is a reserved Pydantic name for
model configuration; any other name is treated as a data field needing a type annotation.

---

## 4.1 — Calling the LLM API (Google Gemini)

**Gotcha:** Provider = **Google Gemini** (free tier), `google-genai` SDK — `from google import genai`;
`gemini = genai.Client(api_key=...)`. Use the **async** client so a multi-second LLM call doesn't
block the event loop (Phase 0): `await gemini.aio.models.generate_content(model=..., contents=msg)`
→ `response.text`. LLM APIs are **stateless** — the model remembers nothing; for multi-turn YOU resend
the full history each call (growing history = growing cost). Put the LLM call in a **service layer**
(`app/services/chat.py`), not the endpoint → provider is swappable (change one function: Gemini→Claude→
local), testable, reusable. Protect LLM endpoints with **auth + `rate_limit`** (they cost money/tokens —
3.3 + 3.6 paying off). Model in a **setting** (`GEMINI_MODEL`), not hardcoded. Gotcha: brand-new Gemini
free accounts can have **0 quota** on a specific model (`429 limit:0`) — `gemini-flash-latest` worked;
each model has its own free quota. Architecture: HTTP→auth→rate_limit→service→LLM→response; the AI is
one swappable component.

**❓ Q:** (1) Why the async client + `await` instead of the sync call? (2) Gemini is stateless — what
does that mean for multi-turn chat? (3) Why (a) a service module for the LLM call and (b) `rate_limit`
on the endpoint?

**A:** (1) A sync call blocks the single event-loop thread for the multi-second LLM call, freezing
every other request; `await` on the async client yields so other requests keep flowing (Phase 0).
(2) The model remembers nothing between calls, so to continue a conversation you resend the entire
message history every request (and cost grows with it). (3a) Separation of concerns — endpoint owns
HTTP, service owns AI logic → provider is swappable (one function) + testable. (3b) LLM calls cost
money/tokens; without a rate limit one user could drain your quota/bill.

---

## 4.2 — Streaming LLM tokens over SSE

**Gotcha:** Combine 3.7 (SSE) + 4.1 (LLM). Gemini streaming: `async for chunk in await
gemini.aio.models.generate_content_stream(...)` → `chunk.text` (guard `if chunk.text` — some are
empty). Service = an **async generator** yielding text pieces (`-> AsyncIterator[str]`; it uses
`yield` not `return`, so it produces MANY strs over time, not one). Endpoint wraps it in an
`event_generator` yielding `data: {json.dumps(token)}\n\n` (JSON-encode! real LLM chunks contain
newlines/special chars that would break raw SSE framing) + `data: [DONE]\n\n`, via `StreamingResponse`.
**Server is a relay between TWO live streams:** `async for` RECEIVES from Gemini (in), `yield` SENDS to
client (out). Under the hood = **chunked transfer encoding** (`Transfer-Encoding: chunked`, no
Content-Length, connection held open, size-prefixed chunks, ends with a 0-length chunk); each `yield`
→ one ASGI `http.response.body` (more_body=True) → uvicorn writes+flushes a TCP chunk. Buffering hides
the drip: use `curl -N` (curl buffers stdout otherwise); **Swagger `/docs` can't show SSE live** (shows
all at end); prod: disable proxy buffering (nginx `X-Accel-Buffering: no`). BaseHTTPMiddleware here
does NOT break streaming (verified). `yield` (generator) vs `return` (one value).

**❓ Q:** (1) What HTTP mechanism sends a body of unknown length with the connection kept open?
(2) Which keyword receives Gemini's stream vs sends to the client? (3) Why did it look "all at once"
in `/docs` but drip over `curl -N`?

**A:** (1) Chunked transfer encoding (HTTP/1.1) — no Content-Length, connection stays open, body sent
as size-prefixed chunks ending in a zero-length chunk. (2) `async for chunk` receives from Gemini (in);
`yield token` sends to the client (out). (3) Swagger UI buffers the whole SSE response and renders it at
the end (can't display a live stream); `curl -N` flushes each chunk so you see the drip.

**Doubts cleared this session:**

- **Why is `stream_reply`'s return type `AsyncIterator[str]` when it "returns" text?** Because it uses
  `yield`, not `return` — that makes it an **async generator**, not a normal function. Calling it gives
  you an async iterator you `async for` over; each iteration yields a `str`. `AsyncIterator[str]` types
  _what you iterate to get_ (a stream of strs), not a single returned str. `return x` = one value;
  `yield x` = many values over time. (`AsyncGenerator[str, None]` is the more specific equivalent.)

- **Why is `current_user: CurrentUser` there if unused?** It's a **side-effect gate** — declaring it
  runs `get_current_user`, so no/invalid token → 401 before the body runs (requires login). Since we
  don't read the value _yet_, the stricter form is `dependencies=[Depends(get_current_user)]` (like
  `rate_limit`); kept it as a param because 4.5 will use `current_user.id` (tie chat to the user).
  Rule: need the value → parameter; just need the gate → `dependencies=[...]`.

- **How the stream flows API↔service (the line-by-line trace):** returning `StreamingResponse(gen())`
  doesn't run the generator — Starlette _pulls_ from it. `event_generator` `async for`s over
  `stream_reply`, which `async for`s over Gemini. Each Gemini chunk → `stream_reply` `yield`s the text
  → `event_generator` `yield`s the SSE frame → Starlette flushes it to the socket → client sees it now.
  One chunk = one pass through both generators = one flush. Nothing buffered in the middle.

- **Two streaming connections, and which uses `yield`:** (1) server ← Gemini and (2) server → client are
  both open at once; the server is a **relay/proxy** between them. But: you **RECEIVE** conn 1 with
  `async for` (Gemini yields to you over the network; you iterate), and you **SEND** conn 2 with `yield`
  (both `yield`s feed the client's `StreamingResponse`). So `async for` = in, `yield` = out.

- **How streaming works under the hood:** normal HTTP sends `Content-Length` + the whole body, then
  closes. Streaming uses **chunked transfer encoding** (`Transfer-Encoding: chunked`): no Content-Length,
  connection held open, body sent as `<hex-size>\r\n<data>\r\n` chunks, ending with `0\r\n\r\n`. ASGI:
  each `yield` → an `http.response.body` message with `more_body=True` → uvicorn writes+flushes a TCP
  chunk; the generator ending → `more_body=False` closes it. SSE = chunked HTTP with `text/event-stream`
  - `data: ...\n\n` framing. Buffers (curl stdout, nginx, Swagger) hide the drip → `curl -N` / disable
    proxy buffering.

---

## 4.3 — Prompt design & structured outputs

**Gotcha:** Two levers: **`system_instruction`** (persona/rules for the whole conversation) vs the
**user message** (`contents` = the task). In Gemini both go through `config=types.GenerateContentConfig(
system_instruction=..., ...)` (`from google.genai import types`). **Structured output** = force the
model to return JSON matching a schema instead of free text you must parse: `response_mime_type=
"application/json"` + `response_schema=SomePydanticModel` → `response.parsed` is a validated instance
(occasionally `None` → fall back to `json.loads(response.text)`). Why it beats "ask for JSON in the
prompt + parse": prompt-asking is unreliable (model adds prose / markdown fences / malformed JSON /
missing fields / wrong types); `response_schema` is **structurally enforced** — guaranteed shape, typed
object, zero parsing. THE technique for LLMs as pipeline components (extraction, classification, tool
args). Built `POST /documents/{id}/analyze` → `DocumentAnalysis{summary, tags[], key_points[]}`,
composing `get_owned_document_or_404` (authz+404) + `rate_limit` + service layer + structured output.

**❓ Q:** (1) system_instruction vs user message? (2) Why is `response_schema` more reliable than asking
for JSON in the prompt and parsing it yourself? (3) Two things `/analyze` reused from earlier phases?

**A:** (1) system_instruction = standing persona/rules (how it behaves); user message = the specific
task/input. (2) Prompt-asking may not comply (prose, code fences, malformed/missing/wrong-typed JSON) →
brittle parsing that still breaks; `response_schema` enforces the shape at decode time → guaranteed
valid JSON + a validated Pydantic object, no parsing. (3) `get_owned_document_or_404` (exists + owned →
authz/404) and `rate_limit` (caps abuse of an expensive endpoint); also service layer + structured output.

---

## 4.4 — Production concerns (cost, errors, retries, timeouts)

**Gotcha:** Robust LLM call = 4 concerns. (1) **Cost/tokens**: `response.usage_metadata`
(`.prompt_token_count`/`.candidates_token_count`/`.total_token_count`) — log it. NOTE total can be >
prompt+output because of **thinking tokens** (billed on total). (2) **Clean errors**: catch
`google.genai.errors.APIError`, raise a domain `LLMError` → handler → **503** (don't leak provider
stack traces; keeps error contract provider-independent — 1.5 pattern). (3) **Retry w/ exponential
backoff**: retry only **transient** codes (429/500/503) with growing waits (`2**attempt` = 1s/2s/4s);
**don't** retry 400/401/403 (client errors fail identically). Instant retry is harmful (slams the rate
limit / piles onto an overloaded server). (4) **Timeout**: `async with asyncio.timeout(N)` so a hung
call fails fast. Retry-loop control flow: 3 exits — `return` (success), `break` (permanent error → give
up), loop-ends (retries exhausted); the bottom `raise LLMError from last_exc` runs only if we never
returned. `tenacity` is the lib that does retry/backoff via a decorator. Logging gotcha: root logger
defaults to WARNING → app `INFO` is filtered; `logging.basicConfig(level=INFO, force=True)` (force
needed — uvicorn already configured logging).

**❓ Q:** (1) Why retry 429/500 but `break` on 400/401/403? (2) What is exponential backoff + why not
retry instantly? (3) Why raise `LLMError`→503 instead of letting the raw Google error propagate?

**A:** (1) 4xx = your request is wrong → fails identically every retry (waste); 429/5xx = the service's
transient state → often clears. (2) Growing waits (1s→2s→4s) between retries; instant retry slams the
rate limit / adds load to an overloaded server — backoff gives it time to recover. (3) Don't leak
provider internals; map to correct HTTP semantics (503 = transient, retry later) in one handler; and
decouple your error contract from the provider (swap Gemini→Claude, callers still just see LLMError/503).

---

## 4.5 — Grounded document Q&A (Phase 4 finale)

**Gotcha:** **Grounding** = put the document's content INTO the prompt + a system instruction ("answer
ONLY from the provided document; if not there, say so; no outside knowledge") + the user's question →
the answer is grounded in YOUR data, not the model's training. Makes it **trustworthy**: no
hallucination (constrained + admits when unknown), works on private data the model never saw (in real
RAG also + citations). This is **RAG-lite / context-stuffing**: `POST /documents/{id}/ask` composes
owned-doc dep + rate_limit + service. **Limitation that motivates Phase 5:** stuffing the WHOLE doc
doesn't scale — large docs exceed the context window; can't stuff many docs; you pay for the whole doc
EVERY query; irrelevant text hurts quality. Phase 5 fix = **retrieve only the relevant chunks**
(embeddings + vector search) instead of stuffing everything. Refactor lesson: extracted the robust
`generate()` wrapper (timeout/retry/backoff/usage-log/LLMError) into `app/core/llm.py` so ALL services
(chat/analyze/qa) share it (DRY) — streaming excluded (can't cleanly retry a started stream). Consistent
typos (`analyze_document`) RUN but hurt readability — rename def+callsite together.

**❓ Q:** (1) What is grounding + why does it make Cortex trustworthy vs a plain chatbot? (2) Your `/ask`
stuffs the whole doc in the prompt — one reason that won't scale, and what Phase 5 does instead?

**A:** (1) Grounding narrows the answer space to the provided document (+ "say if not found"), so it
answers from YOUR data accurately, can't hallucinate, and admits when it doesn't know — vs a chatbot
that answers vaguely from training and confidently makes things up. (2) A large doc won't fit the
context window (also: many docs / cost per query / noise hurts quality); Phase 5 retrieves only the
relevant chunks (embeddings + vector search) and stuffs just those.

---

## 5.1 — Embeddings (foundation of RAG)

**Gotcha:** An **embedding** = a trained function `text → vector` (a point in an N-dim "meaning space";
768 for text-embedding-004, 3072 for gemini-embedding-001 — fixed size so all texts are comparable).
Key property: **similar meaning → nearby points** (semantic, not keyword — "cat"/"kitten" are close with
0 shared words). Each dimension is a learned, non-interpretable feature; meaning is distributed across
all of them. The array = the text's **coordinates**; the whole corpus = a cloud of points that clusters
by meaning. **Cosine similarity** = angle between two vectors' arrows: `dot(a,b)/(|a||b|)` → 1 same
direction (similar), 0 perpendicular (unrelated), -1 opposite; dividing by magnitudes ignores length,
compares pure direction (works in any # of dims). Semantic search / retrieval = embed the query → find
nearest points (nearest-neighbor). **CRUCIAL: scores aren't calibrated** — unrelated text sits ~0.5–0.6,
not 0, and the scale shifts by model/domain → a fixed threshold (`>0.9`) is fragile (matches nothing or
everything). **Rank by similarity and take top-K** (relative order is reliable, absolute value isn't).
Gemini: `await gemini.aio.models.embed_content(model=..., contents=[...])` → `.embeddings[i].values`.

**❓ Q:** (1) What does an embedding turn text into + the property that makes semantic search work?
(2) How does cosine similarity find relevant docs? (3) Why is a fixed similarity threshold wrong —
what do you do instead?

**A:** (1) A fixed-length vector (a point in meaning-space); property = similar meaning lands at nearby
points (keyword search can't do that). (2) Embed the query, cosine it against each doc's vector, take
the highest (angle-based: 1 similar, 0 unrelated). (3) Absolute scores aren't calibrated (unrelated
≈0.57, scale varies by model/domain) so a fixed threshold matches nothing or everything; sort by
similarity and take the **top-K nearest** — relative ranking is reliable.

**Doubts cleared this session:**

- **Why 768/3072 numbers?** It's the embedding **model's fixed output size** (a design choice — its
  final layer has that many outputs). Fixed so every text (a word or a whole book) → the same-length
  vector, which is required to compare them. More dims = more capacity to encode nuance, but more
  storage/compute. Each number is a **learned, non-interpretable feature** — meaning is spread across
  all of them (you can't point at "dimension 5 = animalness").

- **How does text become those numbers?** Run through a **trained neural net** (transformer):
  tokenize → transformer layers (attention) build contextual meaning → **pool** into one fixed vector.
  The numbers are meaningful because of **training**: the model was trained on billions of pairs to
  "put similar-meaning text at nearby points" (contrastive learning). So it's a learned function
  `text → vector`; you don't program the rules, the model learned them. (Don't need transformer
  internals to *use* it.)

- **The big click — it's a vector space:** 768/3072 = the number of **dimensions** of a "meaning
  space"; the array = the text's **coordinates** (a point) in that space. Same as `[x,y]` (2D) or
  `[x,y,z]` (3D), just more axes. The whole corpus = a cloud of points that **clusters by meaning**;
  retrieval = "find the nearest points to the query point" (nearest-neighbor). pgvector's whole job
  (5.3) = store these points + find nearest ones fast.

- **How cosine works (math):** each vector = an arrow from the origin; cosine = how **aligned** two
  arrows are (the angle), ignoring length. `cos = dot(a,b) / (|a|·|b|)` — dot product is big when they
  point together; dividing by magnitudes (`√Σx²`) strips length so only *direction* counts. 1 = same
  direction (0°), 0 = perpendicular (90°), -1 = opposite. Works identically in 3072-D even though we
  can't picture it. 2D check: `[1,1]` vs `[2,2]` → cos = 1 (same direction, length ignored).

---

## 5.2 — Chunking

**Gotcha:** Split docs into **chunks** before embedding because: (1) embedding input limits, (2) a
whole-doc vector is a **blurry average** → won't match a specific question; small chunks each hold one
idea → precise match, (3) you stuff only the relevant chunk (the 4.5 problem). **Chunk size** trade-off:
too big = blurry/imprecise match + noise + cost; too small = lost context + more chunks to store/search.
Sweet spot ≈ a few hundred tokens. **Overlap** = consecutive chunks share boundary text so an idea at
the seam survives whole in at least one chunk. Fixed-size-with-overlap util: window advances by
`start += chunk_size - overlap` (moves less than a full chunk → re-includes the previous tail).
Char-based (~4 chars/token) is simple but **cuts mid-word/sentence** (saw "Al", "rat", "retri");
boundary-aware/recursive splitting (paragraph→sentence, LangChain 5.6) is cleaner. Later: store each
chunk with source doc id + position for citations.

**❓ Q:** (1) Why chunk instead of embedding the whole doc? (2) What does overlap prevent + which line
creates it? (3) Chunk size too big vs too small?

**A:** (1) A whole-doc vector is a blurry average of all its ideas → won't strongly match a specific
question; small chunks match precisely (also: input limits, stuff-only-relevant). (2) Prevents an
idea/sentence at a chunk boundary from being split so neither chunk captures it; `start += chunk_size -
overlap` (advance by less than a full chunk). (3) Too big → imprecise/blurry match + noise + cost; too
small → lost context + more chunks to store/search.

---

## 5.3 — pgvector (vector DB) & ingestion

**Gotcha:** **pgvector** = Postgres extension adding a **`vector(N)`** column type + distance operators
(`<=>` cosine, `<->` L2, `<#>` inner product) + ANN indexes. Use it over a separate vector DB
(Pinecone/Chroma) because vectors sit **alongside relational data** (JOIN/filter by owner,
transactional, one DB, zero extra infra) — dedicated DBs only win at huge scale. Setup: Docker image
`pgvector/pgvector:pg16` (same PG16 → volume compatible; expect a harmless collation warning →
`ALTER DATABASE .. REFRESH COLLATION VERSION`), `pip install pgvector`, model col
`embedding: Mapped[list[float]] = mapped_column(Vector(dim))`. **Migration gotchas:** add
`op.execute("CREATE EXTENSION IF NOT EXISTS vector")` FIRST in upgrade() (autogen won't), and fix the
autogen import to `from pgvector.sqlalchemy import Vector` + `Vector(dim=768)`. **Dim = 768** (not
3072) because pgvector ANN indexes cap at 2000 dims; Gemini `output_dimensionality=768`. FK string uses
`__tablename__` ("documents") not the class. **Ingestion pipeline = chunk → embed → store** (idempotent:
delete old chunks first). `task_type`: RETRIEVAL_DOCUMENT for stored chunks, RETRIEVAL_QUERY for queries
(asymmetric → better retrieval). **Rate-limit reality:** a big doc = a burst of embed requests (doc =
39.9k chars → 62 chunks → 62 requests/ingest; free tier 100/min) → ingestion must be **throttled +
run in Celery** (3.5) so it doesn't blow limits or block/timeout the request. Extracted generic
`_resilient(call, what)` so both `generate()` and `embed()` get timeout+retry+LLMError.

**❓ Q:** (1) What does pgvector add + why over a separate vector DB? (2) The 3 ingestion steps?
(3) Why does one big doc risk the rate limit + the production fix?

**A:** (1) A `vector` column type + distance operators for nearest-neighbor search; use it because
vectors live beside relational data (JOIN/filter/transactional, one DB, no extra infra) — separate DBs
only win at scale. (2) chunk → embed → store (delete-first = idempotent). (3) A big doc → many chunks →
the calls and doesn't block/timeout the HTTP request.

**Doubts cleared this session:**

- **What is `chunk_index`?** The ordinal position of a chunk within its document (0,1,2,… — the `i`
  from `enumerate`). Store it for: **order** (DB rows come back unordered → `ORDER BY chunk_index` to
  restore reading order), **traceability/citations** ("answer from chunk 2 of doc 5"), and debugging.
  Just bookkeeping: which slice, in what order.

- **How does `ondelete="CASCADE"` delete all entries?** It's a **DB-level** rule on the FK, enforced by
  Postgres. Normally a FK blocks deleting a parent that still has children (would orphan them). `ondelete`
  says what to do to children when the parent is deleted: default `RESTRICT`/`NO ACTION` = block;
  **`CASCADE`** = auto-delete the children too; `SET NULL` = null their FK. So `DELETE FROM documents
  WHERE id=5` makes Postgres also run `DELETE FROM document_chunks WHERE document_id=5` — no orphans, no
  manual cleanup, no app code. Right here because chunks are meaningless without their document. (Per-
  relationship judgment: does the child make sense without the parent? If yes, don't cascade.)

- **Why not reuse the `generate()` wrapper for embeddings?** Because `generate()` is hard-wired to
  `generate_content` (chat); embeddings use a different method (`embed_content`) with a different
  response shape. The RESILIENCE (timeout/retry/backoff/LLMError) isn't chat-specific, so the fix is to
  extract a **generic `_resilient(call, what)`** helper and build both `generate()` and `embed()` on it.
  Pass a **`lambda:` factory** (not the coroutine object) so `_resilient` can create a FRESH coroutine
  per retry — a coroutine can only be awaited once. (Caveat: the wrapper's short retries beat transient
  blips, NOT a sustained 100/min rate limit — that needs throttling/Celery.)

---

## 5.4 — Retrieval (nearest-neighbor search)

**Gotcha:** Retrieval = embed the query (`task_type="RETRIEVAL_QUERY"` — asymmetric with the chunks'
`RETRIEVAL_DOCUMENT`; roles are embedded to align → better matches) → nearest-neighbor search in
pgvector. `distance = DocumentChunk.embedding.cosine_distance(query_vec).label("distance")` builds a
**SQL expression** (`embedding <=> :vec AS distance`), NOT a Python number — Postgres computes it per
row at query time. `select(DocumentChunk, distance).join(Document).where(Document.owner_id == owner_id)
.order_by(distance).limit(k)`. **Cosine DISTANCE: lower = more similar** (0 identical; = 1−similarity),
so ORDER BY ASC + LIMIT k = top-K nearest. **MUST scope to the user** (join documents, filter owner_id)
or user A's query leaks user B's private chunks (multi-tenant breach). `result.all()` → (chunk, dist)
rows. SQLAlchemy build vs run: `select().join()...` constructs SQL; `await session.execute(stmt)` runs
it. Char-chunking's mid-word cuts (5.2) are visible in results but retrieval still works. Bugs seen:
`{...}` (set) vs `(...)` (grouping) around the stmt; `response_model=list[SearchRequest]` vs `SearchResult`
(response_model overrides the return annotation).

**❓ Q:** (1) Why embed the query as RETRIEVAL_QUERY? (2) Cosine distance — lower or higher = more
similar, and why ORDER BY ASC LIMIT k? (3) Why join documents + filter owner_id?

**A:** (1) task_type tells Gemini the text's role (query vs document) so they embed to align → better
retrieval. (2) Lower = more similar (distance = 1−similarity); ORDER BY ascending puts closest first,
LIMIT k takes the top-K nearest. (3) Without the owner filter, search spans ALL users' chunks → user A
could retrieve user B's private content (multi-tenant data leak); the filter scopes it to the caller.

---

## 5.5 — The full RAG pipeline

**Gotcha:** **RAG = Retrieve → Augment → Generate.** Retrieve top-k relevant chunks (5.4) → augment:
stuff ONLY those into the prompt as labelled context (`[source doc:chunk]`) + grounding system
instruction ("answer only from context, cite sources, say if not found, no outside knowledge") →
generate. Return answer **+ citations** (which chunks) = trust/verifiability. Fixes 4.5's whole-doc
stuffing: retrieves relevant chunks across ALL docs → scales to any size + cited. **"Retrieved ≠ used"
trap:** top-K ALWAYS returns k chunks (relative ranking, 5.1), so an off-topic query still returns the
"least-far" chunks → don't blindly cite them. Fix: a **relevance floor** (`dist <= MAX_DISTANCE`); if
nothing passes → "not found", NO citations, and skip the LLM call (saves cost). Floor is a heuristic
(5.1: scores uncalibrated) — tune per data, combine with top-K. Gold-standard citation: have the LLM
report which sources it USED via structured output (4.3), cite only those.

**❓ Q:** (1) The three RAG steps? (2) How does this fix 4.5's whole-doc stuffing? (3) Why did off-topic
queries still return citations before the fix?

**A:** (1) Retrieve (top-k relevant chunks) → Augment (stuff them + grounding into the prompt) →
Generate (LLM answers from that context). (2) It retrieves only the RELEVANT chunks across all docs
instead of stuffing one whole doc → scales past the context window + returns citations. (3) top-K
always returns the k nearest chunks even for an irrelevant query (relative ranking, not a threshold),
and we cited all retrieved chunks — but "retrieved ≠ used"; the relevance floor + short-circuit fixes it.

---

## 5.5b — Auto-ingestion (Celery) + PDF extraction

**Gotcha 1 — async work inside a *sync* Celery task.** A Celery task runs as a plain sync
function — no event loop. Bridge with **`asyncio.run(coro())`**: spins up a fresh loop, runs the async
work, tears it down. Two consequences: (1) the worker has **no request** → can't use `get_db`; it opens
its OWN session from `async_session_maker`. (2) asyncpg connections are **bound to the event loop that
created them**; `asyncio.run` makes a new loop each task, so a pooled connection from the last task is
tied to a dead loop → `got Future attached to a different loop`. Fix: **`await engine.dispose()`** in a
`finally` so the pool starts clean. Also: pass the task the **doc_id (a reference), not the content** —
don't push big payloads through the broker (Redis); let the worker fetch fresh from the DB.

**Gotcha 2 — fire-and-forget decoupling.** `ingest_document_task.delay(id)` just enqueues to Redis and
returns instantly → the HTTP request returns `201` in ms while the slow embedding runs in the worker
process. `create`/`update` must `commit()` before enqueue (they do) so the worker's *separate*
transaction can see the row. Run the worker separately: `celery -A app.worker.celery_app worker`.

**Gotcha 3 — PDFs aren't text.** A PDF is a binary format; `bytes.decode("utf-8")` throws. You must
*extract* text first (`pypdf` `PdfReader`). `page.extract_text() or ""` (text-less pages return None).
Scanned/image PDFs extract nothing → need OCR (out of scope) → fail with 400, don't ingest empty.
`extract_text(filename, bytes)` = a **document loader** built by hand (LangChain ships these as
`PyPDFLoader` etc. — see 5.6). Latent bug fixed: `status.HTTP_413` doesn't exist →
`HTTP_413_REQUEST_ENTITY_TOO_LARGE`.

**❓ Q:** Why does `POST /documents` now return in milliseconds when the embedding still takes 20+s?

**A:** The heavy work (chunk + embed) is offloaded to Celery. `.delay()` only pushes a message onto the
Redis queue and returns immediately; the request no longer waits — a worker process does the embedding
off the request path.

**Doubts cleared this session:**

- **"Is there only ONE worker processing all files serially — isn't that slow?"** No. `celery ... worker`
  starts a *manager* that forks a **pool** of child processes (default = 1 per CPU core), so one command
  already runs N tasks in parallel (`--concurrency=N` to tune). And you can run **many** worker processes
  / machines, all pulling from the same Redis queue → horizontal scaling. "The task is sync" means only
  *one task's body* runs top-to-bottom with no event loop — it does NOT mean the system does one task at
  a time. Real bottleneck for us isn't worker count, it's the **Gemini 100 embeds/min** limit (add a task
  rate-limit so the fleet stays under the ceiling).

- **"Why `asyncio.run` — what does it actually do?"** Calling an `async def` doesn't run it — it returns
  a *coroutine* (a recipe). A coroutine only executes when an **event loop** drives it (and parks it at
  each `await`). FastAPI/uvicorn *already have a loop running*, so in an endpoint you just `await`. A
  Celery task is a plain **sync process with no loop** — so `await` is illegal and calling the coroutine
  does nothing. `asyncio.run(coro)` = "build a fresh event loop, run this coroutine to completion
  (driving every await inside), return its result, close the loop." It's the **bridge from the sync world
  (Celery) into the async world (our await-based ingestion)**. Can't just make the task `async def` —
  Celery calls it as a normal function, not with `await`.

- **"300 users hit /upload at once — will the server survive? there's no rate limit."** Yes, *because*
  we offloaded the work. The request path is now cheap (read → extract → 1 INSERT → `.delay()` → 201, in
  ms); FastAPI (async) juggles hundreds of concurrent I/O-bound connections fine. The **queue absorbs the
  spike** (300 messages pile in Redis instantly; workers drain them N at a time) — that buffering is
  called **backpressure**, the main reason to use a queue. The old *inline* version (300 × 60 embeds
  inside live requests) would have melted — the refactor is what makes the burst survivable. Real limits:
  DB connection pool (jobs queue briefly, fine), downstream embed rate limit (jobs just wait — fine), and
  the one *actual* gap → **no abuse protection on /upload**. Fix = one line: add `Depends(rate_limit)`
  (the Redis INCR+EXPIRE limiter we already built) to `create`/`upload`, like the other endpoints.
  Bonus smell: `extract_text` is sync CPU work called inside an async endpoint → blocks uvicorn's loop
  for big PDFs; at scale, run it in a threadpool or push extraction into the Celery task too.

---

## 5.6 — LangChain / LCEL

**Gotcha:** LangChain = **standard interfaces** (loader / splitter / embeddings / vectorstore / chat
model — all swappable) **+ LCEL** composition. In LCEL you wire pieces with the **`|`** pipe (output of
left → input of right); it works because *every* piece is a **`Runnable`** (`.invoke`/`.ainvoke`/
`.stream`/`.batch`). Data **changes type at every `|`**: `str → dict → PromptValue → AIMessage → str`;
building a chain = making each step's output shape match the next's input. A plain **`{dict}`** in a pipe
is auto-coerced to a **`RunnableParallel`** (runs each branch on the same input → dict of results).
**`RunnablePassthrough()`** passes input through unchanged. **`RunnablePassthrough.assign(k=…)`** =
"keep every existing key, ADD key `k`" (that's how `rows` survived to the end for citations; a plain step
*replaces* the dict). **`RunnableBranch((cond, run), default)`** = LCEL if/else (used for the relevance
floor → no rows ⇒ canned NOT_FOUND, skips the LLM). **Takeaway:** LCEL wins for linear compose +
streaming + provider-swap + ecosystem; hand-roll wins for **branching / control-flow / product rules**
(our floor + citation contract took RunnableParallel + 2×`.assign` + RunnableBranch + 3 lambdas to match
~8 plain lines). Streaming came free (vs the SSE plumbing we wrote in 4.2).

**Trap (bit me 3×):** **bare class vs instance in a pipe.** A bare *callable* in `|` is auto-wrapped and
*called* with the piped value — and a class is callable, so `StrOutputParser` (no `()`) becomes
`StrOutputParser(msg)` → `TypeError: BaseModel.__init__() takes 1 positional argument but 2 were given`;
`RunnablePassthrough` (no `()`) → `ValidationError: func.callable — Input should be callable`. Rule:
**instances go in the pipe** → `StrOutputParser()`, `RunnablePassthrough()`, `RunnableLambda(fn)`. BUT
`RunnablePassthrough.assign(...)` is a **classmethod** → correct *without* `()` on the class (it returns
the instance for you). Separate trap: forgetting `await` on `retrieve_chunks` → `rows` is a coroutine →
`TypeError: 'coroutine' object is not iterable` (missing-await tell).

**❓ Q:** (1) What does `|` do and what interface makes it work on every piece? (2) What does
`RunnablePassthrough.assign(answer=…)` do to the data vs a plain step? (3) When is LCEL worth it vs
hand-rolled?

**A:** (1) Pipes runnables — left's output feeds right's input; the shared **`Runnable`** interface
(`.invoke/.ainvoke/.stream/.batch`) makes any piece connectable. (2) It **adds the `answer` key while
keeping all existing keys** (`{rows,question,context}` → `{…,answer}`); a plain step would *replace* the
whole dict with just its output. (3) LCEL for linear pipelines (compose + free streaming/async/batch +
one-line provider swap + ecosystem); hand-rolled the moment you need branching / custom control flow /
product-specific rules — fewer moving parts, no indirection, easier to debug.

**Doubts cleared this session:**

- **"Where does `distance` come from — `retrieve_chunks` looks like it returns only the chunk?"** It
  returns **`(DocumentChunk, distance)` tuples**, because the query does `select(DocumentChunk, distance)`
  — **two** things per row. `distance` isn't a table column; it's computed by **pgvector in the DB** from
  `DocumentChunk.embedding.cosine_distance(query_vec).label("distance")` (the `<=>` operator), returned as
  an extra column. Also: `.all()` returns whole rows (tuples); `.scalars().all()` would return only the
  first entity (just the chunk) — that's why retrieval uses `.all()` and repos use `.scalars().all()`.

- **"What/why is `_format_docs`?"** Retrieval returns *objects* (`(chunk, distance)` tuples) but a prompt
  needs *text*. `_format_docs` is the adapter: `for c, _ in rows` (unpack tuple, `_` = ignore distance),
  builds a labeled block `[source doc:chunk]\n{content}` per chunk, `"\n\n".join(...)` into one context
  string for the `{context}` slot. Labels enable citing/traceability.

- **"We didn't use RunnableParallel / I don't see citations — is it the prompt?"** (a) The plain `{dict}`
  IS a RunnableParallel (implicit coercion). (b) Two separate reasons for "no citations": the endpoint
  hardcoded `citation=[]` because the chain threw the rows away (fixed by carrying `rows` via
  `.assign`), AND the LCEL prompt didn't instruct the model to cite inline (fixed by adding a cite line to
  `RAG_PROMPT`) — two independent knobs.

- **Re-caught "retrieved ≠ used":** the `citation` array lists **all** retrieved chunks that passed the
  floor (5), but the answer only *used* one (`[source 4:2]`) → 4 citations are noise. Same as 5.5. Both
  `/ask` and `/ask-lc` do this. Gold-standard = cite only *used* sources: parse the `[source d:c]` markers
  out of the answer, or have the LLM return structured `used_sources` (the 4.3 pattern).

---

## 5.7 — RAG evaluation

**Gotcha:** RAG has **two failure points — retrieval & generation — and you MUST measure them
separately**, because a bad answer is either "fetched the wrong chunks" (retrieval) or "hallucinated /
ignored good chunks" (generation), and only separate scores tell you *which half to fix*. **Retrieval
eval** is exact → no LLM: a fixed labeled set (question → expected_doc, plus an off-topic one with
`expected_doc=None` to test the floor), scored with **hit-rate@k** (fraction where the right doc is in
top-k), MRR (rewards higher rank), recall@k. **Generation eval** is fuzzy → you **can't use `==`** (two
answers can be correct but worded differently), so use **LLM-as-judge**: a *second* LLM call that reads
question+context+answer and returns a structured verdict (`Judgment{faithful, relevant, reason}` via
`response_schema` — the 4.3 pattern). Result here: retrieval **67%** (1 real miss on the short/vague
"What is Global?"), generation **faithful 2/2, relevant 2/2** → **diagnosis: generation is trustworthy,
retrieval is the weak link → fix chunking/embeddings/k/query, NOT the prompt.** Caveats: tiny sample
(real evals = 50–200 Qs); the judge is itself an LLM (spot-check vs human; often use a stronger judge
model). This is what **RAGAS** automates.

**❓ Q:** (1) Name RAG's two failure points and why measure them separately. (2) Why can't you grade a
free-text answer with `==`, and what do you use instead? (3) Given retrieval 67% + generation faithful
2/2 — where's the bug and what would you fix?

**A:** (1) Retrieval (wrong chunks fetched) and generation (LLM hallucinates/ignores good chunks);
separately, because the fix is completely different and a single end-to-end score can't tell you which
half broke. (2) Two correct answers can be worded differently so string-equality marks a right answer
wrong; use an **LLM-as-judge** (structured output) that recognizes "these mean the same thing." (3) The
bug is in **retrieval** (67%, the weak link); generation is faithful → fix chunking / embeddings / k /
query handling, **not** the prompt.

**Doubts cleared this session:**

- **"Why did we even do this? It's just a scratch file with predefined questions — what's the point?"**
  It's a **test/measurement harness for the RAG pipeline** — the AI-quality equivalent of unit tests. The
  fixed questions are a **yardstick**: change something in the flow (chunk size, embeddings, k, prompt,
  model, floor, hand-built vs LangChain) → re-run → the number moves → keep or revert. Without it you're
  guessing ("seems better?"); with it you can *say* "retrieval improved 67%→80%." That's the difference
  between shipping AI and just demoing it.

- **"So it's just for testing / when we change the flow?"** Yes. Also (a) a **regression guard** — catches
  silent degradation from a library/model-version bump, not just intended changes; (b) in **production it
  runs continuously**: on every deploy as a CI quality gate (block if score drops), on a schedule (cron)
  to catch **drift** (new docs change the vector space, the provider updates the model under you), and on
  **live traffic** (sample real answers, run the judge on them). Ties to Phase 6 observability + Phase 7.

- **"What are 'the retrieval query' and 'the relevance floor' (things we might change)?"** *Retrieval
  query* = the text you actually search with; currently the raw question is embedded as-is, but you can
  **rewrite/expand** it (e.g. fix a vague "What is Global?") or add keyword/hybrid search before
  embedding. *Relevance floor* = `MAX_DISTANCE` (0.45) cutoff on distance (lower = more similar): lower it
  → stricter (fewer false matches but may drop correct-but-far chunks); raise it → looser (catch more but
  more junk). It's a **precision-vs-recall dial**, and the eval set is exactly how you'd *tune* it.

- **"Where is the LLM-as-judge step in the file?"** `judge()` (`scratch_eval.py`) — sends
  question+context+answer to the LLM, returns a `Judgment`; that's where the model recognizes semantic
  equivalence that `==` can't. Step 1 = `main()` (retrieval, exact `==`/set-membership, no LLM); Step 2 =
  `eval_generation()` (runs real RAG → calls `judge()`). Only whichever `asyncio.run(...)` is at the
  bottom actually runs.
