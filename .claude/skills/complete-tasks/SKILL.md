---
name: complete-tasks
description: >
  Run final quality gates and delivery steps after all tasks in a spec are complete.
  Automatically invoked by execute-tasks at the end of a task session, but can also be
  called directly to re-run finalization — for example after resolving a blocker,
  recovering from a failed regression, or resuming an interrupted session. Trigger on
  phrases like "complete the tasks", "finalise the feature", "run final checks",
  "create the PR", "we're done implementing", or at the end of any task execution
  session. Requires all tasks in tasks.md to be marked complete before proceeding.
---

# Complete Tasks Skill

Run final quality gates and delivery steps after all assigned parent tasks are complete.
This is the last step before a feature is ready for review.

---

## Process

### Step 1 — Verify Task Completion

Check `tasks.md` to confirm all assigned parent tasks and their subtasks are marked
complete (`[x]`).

If any uncompleted tasks remain, stop and return to the execute-tasks skill to finish
them before proceeding.

---

### Step 2 — Environment Sanity

Ensure the environment is clean before running final checks:

- No unexpected uncommitted changes (commit or stash as appropriate)
- Dependencies are installed and up to date
- Build passes if the project has a build step

---

### Step 3 — Full Regression

Run the complete test suite and static checks to confirm the feature is release-ready.

**Test scope:**
- All unit tests
- All integration tests
- End-to-end tests (if present)

**Static checks:**
- Lint
- Type checking
- Basic security scan (if configured)

**Discover test commands** by checking `package.json` scripts, `pyproject.toml`,
`Makefile`, or project conventions. Use the appropriate command for the stack.

**Report:**

> ## Full Regression — [FEATURE_NAME]
>
> **Status:** ✅ PASS / ❌ FAIL
> **Duration:** [X]m [Y]s
> **Tests:** [TOTAL] total, [PASSED] passed, [FAILED] failed
>
> **Static checks:** ✅ Lint  ✅ Type check  ✅ Security scan
>
> **Quality gate:** PASS / FAIL

**Gate policy:**
- Block delivery on any test failures or high-severity static check issues
- Flaky tests should be noted but are non-blocking if tagged as such
- Fix failures before proceeding — do not skip the gate

---

### Step 4 — Versioning and Release Notes (conditional)

Apply this step only if the project uses explicit versioning. Check for:
- `CHANGELOG.md` at the repository root
- A `version` field in `package.json` or `pyproject.toml`
- A `version.json` or equivalent

If none of these exist, skip this step silently.

If versioning applies:
- Apply a version bump (patch/minor/major) appropriate to the change
- Write a `CHANGELOG.md` entry summarising what was added, changed, or fixed

---

### Step 5 — Commit and Pull Request

Commit all final changes and open a PR for review.

**Commit:**
- Stage all modified files
- Show the exact commit message to the user before committing
- Ask: *"Confirm commit now? (yes/no)"* — proceed only on explicit yes
- Use `TASK: [feature summary]` as the commit prefix

**PR:**
- Title: concise description of the feature
- Description should include:
  - Summary of what was built
  - Key decisions made
  - Test results summary
  - Any known risks or follow-up items
- Target branch: `main` (or the project's default branch)

---

## Completion Summary

> ✅ **Feature complete and ready for delivery**
>
> **Full regression:** [N] tests passed, 0 failed ([X]m [Y]s)
> **Static checks:** All passed
> **Quality gate:** ✅ PASS
>
> **Files changed:** [N] files across [M] tasks
> **Pull request:** Created — "[PR TITLE]"
>
> Ready for review and merge.

---

## Key Principles

**Full regression is a hard gate.** Do not create the PR if tests are failing. Fix
failures first.

**Commit confirmation always.** Show the exact message, wait for explicit yes.

**Versioning is optional but consistent.** Only bump versions if the project already
uses versioning — don't introduce it for projects that don't have it.

**PR description is load-bearing.** Reviewers shouldn't have to dig through commits to
understand what was built. Write a clear, complete description.
