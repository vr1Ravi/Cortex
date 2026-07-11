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
