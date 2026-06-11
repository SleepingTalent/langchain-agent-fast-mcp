---
name: execute-tasks
description: >
  Orchestrate execution of all tasks in a spec's tasks.md, delegating each parent task
  to the execute-task skill and running integration and regression checks between tasks.
  Use this skill when the user wants to implement an entire spec end-to-end, run all
  remaining tasks for a feature, or resume a partially completed task set. Trigger on
  phrases like "execute all tasks", "implement the spec", "run the tasks", "let's build
  this", "start implementation", or after /create-tasks completes and the user confirms
  they are ready to begin. Requires an approved spec with tasks.md in
  .claude/specs/SPEC-FOLDER/. Calls execute-task for each parent task and
  complete-tasks when all tasks are done.
---

# Execute Tasks Skill

Orchestrate the full implementation of a spec by executing all parent tasks in order,
running integration checks after each task, and handing off to the complete-tasks skill
when everything is done.

---

## Preconditions

- A spec folder exists at `.claude/specs/SPEC-FOLDER/`
- `tasks.md` exists in that folder
- At least one uncompleted parent task exists

---

## Process

### Step 1 — Task Assignment

Identify which tasks to execute.

**If the user specifies tasks** (e.g. "run tasks 2 and 3"): use those.
**If no tasks specified**: find the next uncompleted parent task in `tasks.md` and
confirm with the user before proceeding.

Ask: *"I'll start with Task [N]: [TITLE]. Shall I proceed?"* — wait for confirmation.

---

### Step 2 — Load Context

Before starting, load the following from the spec folder (only what isn't already in
context):

- `tasks.md` — full task list and current completion state
- `spec-lite.md` — condensed feature summary
- `sub-specs/technical-spec.md` — technical approach

This ensures each task is executed with full awareness of the spec's intent.

---

### Step 3 — Environment Check

Check whether a local development server is running. If one is detected, ask the user
whether to shut it down before proceeding to avoid port conflicts.

> "A development server appears to be running. Should I shut it down before starting?
> (yes/no)"

Proceed immediately if no server is detected.

---

### Step 4 — Git Branch Setup

Before writing any code, ensure the correct git branch is set up for this spec:

- Derive branch name from the spec folder slug by stripping the date prefix
  (`^\d{4}-\d{2}-\d{2}-`) from the folder name
- Branch naming rules:
  - lowercase, kebab-case, only `[a-z0-9-]`
  - collapse multiple hyphens, trim leading/trailing hyphens
  - if branch already exists for this spec, check it out; otherwise create it
  - if name collides with an unrelated branch, append `-2`, `-3`, etc.
- Examples:
  - `2026-05-23-password-reset-flow` → branch `password-reset-flow`
  - `2026-05-23-api-rate-limiting` → branch `api-rate-limiting`

Handle any uncommitted changes before switching (stash or commit as appropriate).

---

### Step 5 — Task Execution Loop

For each assigned parent task, invoke the **execute-task skill** with the task number
and its subtasks. Continue until all assigned tasks are complete.

**After each parent task completes:**

**5a — Integration checks:** Run integration tests for the affected feature slice —
endpoints, DB interactions, UI happy-path flows, cross-component interactions. These
are in addition to the unit tests run during execute-task; do not re-run unit tests here.

Discover integration test commands by checking for:
- `npm run test:integration`
- `pytest tests/integration/`
- `make integration-test`
- Any test files/directories with "integration" in the path

Report: *"✅ Integration tests passed for Task [N] — API/DB/UI flows verified ([X]s)"*

**5b — Context refresh:** Check for `llm.txt` in the project root. If present, read it
to refresh understanding of project structure and key paths before the next task. If
absent, skip silently — do not prompt the user or block execution.

**Loop exit conditions:**
- All assigned tasks are marked complete in `tasks.md`
- User requests early termination
- A blocking issue cannot be resolved

**Commit behaviour:** Before each commit, show the exact commit message and ask:
*"Confirm commit now? (yes/no)"* — proceed only on explicit yes. Use `TASK:` as the
commit message prefix.

---

### Step 6 — Incremental Regression (optional)

After all tasks complete, run an incremental regression suite before final handoff.
This step can be skipped for trivially small changes.

**Test selection algorithm:**
1. Identify all files modified across the task batch
2. Include any test file whose source path matches or imports a modified file
3. Always include global smoke tests (`tests/smoke/`, `e2e/smoke.test.js`, or similar)

Report: *"✅ Incremental regression passed — [N] tests, 0 failures ([X]s)"*

If failures are found, debug and fix before proceeding to Step 7.

---

### Step 7 — Finalisation

Once all tasks are complete and incremental regression passes, invoke the
**complete-tasks skill** to run final quality gates and prepare delivery.

---

## Completion Summary

> ✅ **All tasks complete — [SPEC_NAME]**
>
> **Tasks executed:** [N] parent tasks
> **Integration tests:** All passed
> **Incremental regression:** [N] tests passed, 0 failures ([X]s)
>
> Handing off to complete-tasks for final regression and PR creation.

---

## Key Principles

**One task at a time.** Do not start the next parent task without completing and verifying
the current one. Confirm with the user after each if they want to continue.

**Integration after every task.** Unit tests alone aren't enough — verify component
interactions after each parent task completes.

**Context refresh between tasks.** Long sessions drift. Read `llm.txt` between tasks
if it exists to stay oriented on project structure.

**Commit confirmation always.** Never commit without showing the message and getting
explicit user approval.

**Blockers stop the loop.** If execute-task surfaces a blocker that can't be resolved,
stop and surface it to the user rather than skipping ahead.
