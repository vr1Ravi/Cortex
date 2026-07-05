# I/O (Input/Output)

**Definition:** Any operation where the CPU communicates with a device *outside itself and RAM* — sending data out or reading data in.

## Key idea
- The CPU's "home turf" = **CPU + RAM** (nanosecond-fast, direct).
- Anything beyond that = **I/O** (send a request → *wait* for a separate device).
- The boundary is **RAM**, not the physical computer. A local SSD is still I/O.

## Types
- **Disk I/O** — files, reading/writing to SSD
- **Network I/O** — HTTP requests, calling APIs
- **Database I/O** — queries (network + disk underneath)
- **User I/O** — keyboard input, terminal output

## Speed (why I/O is "slow")
| Operation | Rough time |
|-----------|-----------|
| CPU ↔ RAM | ~100 ns |
| Read SSD | ~100 µs |
| Network | ~1–100 ms |

## Why it matters
- **I/O-bound** = limited by *waiting* → **async helps** (`await` lets the CPU serve other requests while waiting).
- **CPU-bound** = limited by *computing* → async doesn't help; need more cores.
- Most web work (DB calls, API calls) is **I/O-bound** → the reason FastAPI uses `async`.

> **Mental model:** I/O = CPU asks another device for data and waits. Computation = CPU works with what's already in RAM.


Request →  [ API layer ]      routes: receive request, return response
           [ Service layer ]  business logic: "what should happen"
           [ Data layer ]     models + DB access: "how it's stored"

What ruff is: a linter (finds bugs/bad patterns) and formatter (auto-styles code) in one, written in Rust so it's instant. It's the modern standard — replaces flake8 + isort + black.

