---
name: create-tasks
description: >
  Generate a structured task list from an approved feature spec. Use this skill whenever
  the user wants to break a spec down into implementation tasks, create a checklist for a
  feature, or move from a formal spec to actionable work. Trigger on phrases like "create
  tasks", "generate tasks", "break this into tasks", "what do I need to build", "create
  a task list", or after /create-spec completes and the user is ready to start
  implementation. Requires an approved spec.md in .claude/specs/ before proceeding.
  Produces a tasks.md file in the same spec folder.
---

# Create Tasks Skill

Generate a structured, TDD-ordered task list from an approved feature spec. Tasks live
alongside the spec in `.claude/specs/<spec-folder>/tasks.md` and serve as the canonical
checklist for implementation.

---

## Preconditions

Before generating tasks, verify:

1. A spec folder exists at `.claude/specs/<spec-folder>/`
2. `spec.md` inside that folder contains `Status: approved` (case-insensitive)
3. If `tasks.md` already exists, perform an idempotent merge (see Merge Rules below)

**Failure handling:**
- No spec folder → tell the user to run `/create-spec` first
- Spec not approved → ask the user to add `Status: approved` near the top of `spec.md`
- Unparseable existing `tasks.md` → append a `REVIEW REQUIRED` block and stop

---

## Process

### Step 1 — Load Spec Context

Read the following files from the spec folder:

- `spec.md` — main requirements, scope, user stories, deliverables
- `spec-lite.md` — condensed summary (if present)
- `brainstorm.md` — design decisions and selected approach (if present)
- `sub-specs/technical-spec.md` — technical requirements (if present)
- `sub-specs/database-schema.md` — schema changes (if present)
- `sub-specs/api-spec.md` — API endpoints (if present)

Use all available context to derive tasks. The more sub-specs present, the more precise
the task breakdown can be.

---

### Step 2 — Generate Tasks

Derive 1–5 major tasks from the spec scope. Each major task maps to a distinct feature,
component, or layer of the implementation.

**Task structure:**
- Major tasks: numbered `1.`, `2.`, etc. — grouped by feature or component
- Subtasks: decimal notation `1.1`, `1.2`, etc. — up to 8 per major task
- First subtask: always write tests for the component (TDD)
- Last subtask: always verify all tests pass

**Ordering principles:**
- Respect technical dependencies (e.g. DB schema before API before UI)
- Follow TDD — tests before implementation at every level
- Build incrementally — each major task should be independently shippable where possible
- Group related functionality together

**File location:** `.claude/specs/<spec-folder>/tasks.md`

---

### Step 3 — Write tasks.md

Create (or merge into) `tasks.md` using the template below.

**Template:**

```markdown
# Spec Tasks

> Spec: [SPEC_NAME]
> Created: [YYYY-MM-DD]

## Tasks

- [ ] 1. [MAJOR_TASK_DESCRIPTION]
  - [ ] 1.1 Write tests for [COMPONENT]
  - [ ] 1.2 [IMPLEMENTATION_STEP]
  - [ ] 1.3 [IMPLEMENTATION_STEP]
  - [ ] 1.4 Verify all tests pass

- [ ] 2. [MAJOR_TASK_DESCRIPTION]
  - [ ] 2.1 Write tests for [COMPONENT]
  - [ ] 2.2 [IMPLEMENTATION_STEP]
  - [ ] 2.3 [IMPLEMENTATION_STEP]
  - [ ] 2.4 Verify all tests pass
```

---

## Merge Rules (if tasks.md already exists)

When `tasks.md` exists, merge rather than overwrite:

- Preserve all existing completed checkboxes (`[x]`) — never uncheck them
- Do not reorder completed major tasks or their completed subtasks
- Append new major tasks at the end of the list (continue numbering from highest N)
- Append new subtasks at the end of their parent block (continue decimal series)
- If duplicate numbering or structural conflicts are detected, append a `REVIEW REQUIRED`
  block at the end of the file and stop — do not modify further

---

### Step 4 — Execution Readiness

After writing the file, present a summary and prompt the user to confirm before starting
implementation:

> ✅ **Tasks created — [SPEC_NAME]**
>
> **Task file:** `.claude/specs/<spec-folder>/tasks.md`
> **Tasks generated:** [N] major tasks, [M] subtasks total
>
> **Task 1:** [FIRST_TASK_TITLE]
> [Brief description of Task 1 and its subtasks]
>
> Ready to start implementing Task 1, or would you like to review the task list first?
> Run `/execute-tasks` to begin, or let me know if anything needs adjusting.

Wait for the user to confirm before proceeding to implementation. When confirmed, focus
only on Task 1 and its subtasks unless the user explicitly requests otherwise.

---

## Key Principles

**TDD first.** Every major task starts with writing tests. This is non-negotiable — it
forces clarity on what "done" means before implementation begins.

**One task at a time.** Do not proceed to Task 2 without explicit user confirmation.
Each task should be fully complete (all subtasks checked, tests passing) before moving on.

**Derive from spec, not imagination.** Tasks must map directly to items in the spec scope
and technical spec. Do not add tasks for features not in the spec.

**Incremental and shippable.** Each major task should leave the codebase in a working
state. Avoid tasks that require multiple other tasks to be complete before anything runs.
