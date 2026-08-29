# PROJECT BOARD — wechat-miniapp-launchpad

## MODE
`MAINTENANCE`

## STATE
- Reusable WorkBuddy skill for taking a WeChat mini-program idea through planning, account/tool setup, project skeleton, implementation, assets/package size, debugging and release.
- Contains `SKILL.md`, references, and `scripts/gen_sfx.py`.

## QUEUE
### WML-P0-001 — Skill/reference consistency audit
- status: READY
- goal: Verify SKILL flow, references, examples, package-size guidance, and publishing guidance are internally consistent; fix clear documentation drift.

### WML-P0-002 — `gen_sfx.py` smoke/test audit
- status: READY
- goal: Run non-network smoke checks where possible, validate argument/error behavior and document dependencies; fix deterministic low-risk bugs.

### WML-P1-001 — Packaging/install instructions audit
- status: READY
- goal: Check folder/zip installation instructions and skill structure for reproducibility; improve only where evidence supports it.

## IDEA INBOX
New capabilities or broad new templates belong here until clearly approved.

## BLOCKED
Real WeChat account registration, AppID, privacy review, submission, production publishing, and any credentials require human action.

## LAST CHECKPOINT
ChatGPT PM initialized Night Shift maintenance mode on 2026-08-30.