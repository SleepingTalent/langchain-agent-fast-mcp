---
name: execute-task
description: >
  Execute a single task and all its subtasks from a spec's tasks.md using a TDD workflow.
  This skill is typically invoked by the execute-tasks skill for each individual task, but
  can also be called directly. Use when the user wants to implement a specific numbered
  task from a spec, work through a task's subtasks systematically, or resume a task that
  was previously started. Trigger on phrases like "execute task 2", "implement task 1",
  "work on task 3", "let's do task 2", or when called internally by execute-tasks.
  Requires tasks.md to exist in .claude/specs/SPEC-FOLDER/.
---

# Execute Task Skill

Execute a specific parent task and all its subtasks from `tasks.md` using a systematic
TDD workflow. Marks each subtask complete as it finishes, and documents any blockers
encountered.

---

## Process

### Step 1 — Task Understanding

Read the target parent task and all its subtasks from `tasks.md`.

Understand:
- The full scope of what needs to be built
- Dependencies on other tasks or subtasks
- Expected outcomes and deliverables
- Test requirements implied by the subtasks

Do not begin implementation until the full scope is clear.

---

### Step 2 — Load Spec Context

Load relevant context from the spec folder before writing any code:

- `sub-specs/technical-spec.md` — find sections relevant to this task's functionality,
  implementation approach, integration requirements, and performance criteria. Read
  selectively — only extract what applies to the current task, skip unrelated sections.
- `sub-specs/database-schema.md` — if the task involves data layer changes (if present)
- `sub-specs/api-spec.md` — if the task involves API changes (if present)
- `spec-lite.md` — for a quick reminder of the overall goal (if present)

Also check the project for:
- A `STANDARDS.md`, `BEST_PRACTICES.md`, or similar file for coding conventions
- A `CODE_STYLE.md` or equivalent for formatting and style rules
- Any existing test patterns in the codebase to match

Apply whatever conventions exist. If none are found, use sensible defaults for the
project's language and framework.

---

### Step 3 — Execute Subtasks in Order

Work through the subtasks sequentially using TDD:

**First subtask** (typically "Write tests for [component]"):
- Write all tests for the parent feature before any implementation
- Cover unit tests, integration tests, and edge cases
- Run the tests to confirm they fail appropriately (red)
- Mark subtask complete

**Middle subtasks** (implementation steps):
- Implement the specific functionality described
- Make the relevant tests pass (green)
- Refactor while keeping tests green
- Update any adjacent tests if behaviour changes
- Mark each subtask complete as finished

**Final subtask** (typically "Verify all tests pass"):
- Run only the tests relevant to this parent task — not the full suite
- Fix any remaining failures within this task's scope
- Confirm no regressions in changed files
- Mark subtask complete

**Marking complete:** Update each checkbox in `tasks.md` from `- [ ]` to `- [x]`
immediately when done. Do not batch updates.

---

### Step 4 — Blocker Handling

If a subtask cannot be completed after 3 genuine attempts with different approaches:

- Stop attempting
- Document the blocker inline in `tasks.md`:
  ```
  - [ ] 1.3 [SUBTASK_DESCRIPTION]
      ⚠️ Blocking issue: [CLEAR DESCRIPTION OF WHAT'S BLOCKING AND WHAT WAS TRIED]
  ```
- Surface the blocker to the user and ask how to proceed
- Do not mark the subtask complete

---

### Step 5 — Task Completion Summary

Once all subtasks are complete (or blocked), provide a summary:

> ✅ **Task [N] complete — [TASK_TITLE]**
>
> **Tests:** [X] passed, [Y] failed
> **Files modified:** [LIST]
> **Subtasks:** [N/M] complete
>
> [If any blockers]: ⚠️ [N] blocker(s) documented in tasks.md
>
> Ready to proceed to Task [N+1], or let me know if you'd like to review first.

---

## Key Principles

**TDD is non-negotiable.** Tests are written before implementation. Running tests red
before making them green is the process — not a suggestion.

**Task scope only.** Do not implement anything not described in the current task's
subtasks. If something adjacent seems obviously needed, note it rather than doing it.

**Immediate checkbox updates.** Mark subtasks done as they complete — don't wait until
the end. This keeps `tasks.md` accurate if the session is interrupted.

**Focused test runs.** Run only the tests for the current task, not the full suite.
Full suite verification is handled by execute-tasks after all tasks are complete.

**Three strikes on blockers.** Three different approaches, then document and escalate.
Don't spin indefinitely on a stuck subtask.
