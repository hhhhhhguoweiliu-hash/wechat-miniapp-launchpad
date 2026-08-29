# NIGHT SHIFT

1. Read `AGENTS.md`, `.ai/PROJECT_BOARD.md`, `.ai/LEASE.md`, README/SKILL and task-relevant files.
2. `git fetch origin`; use `origin/codex/night-shift` as durable checkpoint; never force.
3. Acquire lease; if another unexpired ACTIVE run owns it, exit.
4. Resume RUNNING, otherwise highest READY.
5. Use small milestones: inspect → change → verify → update board/lease → commit → push `codex/night-shift`.
6. Continue safe maintenance tasks while available.
7. Account/credential/production/publishing gates go to BLOCKED and do not stop other work.
8. Do not invent new product scope just to consume quota.
9. Normal end releases lease; hard interruption may leave ACTIVE until TTL takeover.