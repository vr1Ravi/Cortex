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
