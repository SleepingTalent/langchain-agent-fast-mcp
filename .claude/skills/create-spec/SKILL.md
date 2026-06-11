---
name: create-spec
description: >
  Generate a detailed feature specification from a rough idea or confirmed brainstorm.
  Use this skill whenever the user wants to create a formal spec, write up a feature
  requirement, document a technical design, or formalise a plan before implementation.
  Trigger on phrases like "create a spec", "write up the spec", "formalise this",
  "document this feature", "ready to spec this out", or after a brainstorm session
  concludes and the user wants to move to a formal document. Also trigger when the user
  asks "what's next?" in a project context — check for the next unimplemented item and
  suggest speccing it. Produces a structured set of spec files in .claude/specs/.
---

# Create Spec Skill

Generate detailed feature specifications aligned with the project's goals and technical
constraints. Produces a structured folder of spec documents in `.claude/specs/` that
serve as the source of truth before implementation begins.

---

## Output Structure

For each spec, create the following in `.claude/specs/YYYY-MM-DD-spec-name/`:

| File | Purpose | Always? |
|------|---------|---------|
| `spec.md` | Main requirements document | ✅ Always |
| `spec-lite.md` | Condensed 1–3 sentence summary for AI context | ✅ Always |
| `sub-specs/technical-spec.md` | Technical requirements and dependencies | ✅ Always |
| `sub-specs/database-schema.md` | Schema changes, migrations, indexes | Only if DB changes needed |
| `sub-specs/api-spec.md` | Endpoints, parameters, responses | Only if API changes needed |

---

## Process

### Step 1 — Initiation

Two entry points:

**A) "What's next?"** — If the user asks what to work on next, check for a roadmap or
backlog file in the project (e.g. `ROADMAP.md`, `.claude/product/roadmap.md`, or similar).
Find the next uncompleted item, suggest it to the user, and wait for approval before
proceeding.

**B) Specific idea** — Accept the user's spec idea in any format (brief description,
bullet points, feature request, post-brainstorm summary). Proceed to Step 2.

---

### Step 2 — Load Brainstorm (if available)

Before asking any clarifying questions, check whether a `brainstorm.md` already exists
for this topic in `.claude/specs/`.

- Scan `.claude/specs/` for a folder whose name matches the topic (by date or keyword).
- If found, read `brainstorm.md` and use it as the primary input for the spec:
  - Use the **Problem Statement** as the basis for the Overview section.
  - Use **Approaches Considered / Selected** to inform scope and technical decisions.
  - Use **Key Decisions** to pre-populate rationale in the technical spec.
  - Use **Open Questions** to guide any remaining clarification needed.
- Tell the user: *"I found a brainstorm for this topic — I'll use it as the basis for
  the spec."* Then summarise the selected approach in one line and confirm before
  proceeding.
- If no brainstorm exists, proceed normally to Step 3.

---

### Step 3 — Requirements Clarification

Ask any questions needed to clarify scope before writing. Keep to one question at a time.
Focus on:

- **Scope:** What's in, what's explicitly out?
- **Users:** Who does this affect and how?
- **Technical:** Any known constraints, integration points, or dependencies?
- **Success:** What does "done" look like?

If the spec idea is already detailed enough (e.g. it came from a brainstorm), skip
straight to Step 4 — don't ask questions for the sake of it.

---

### Step 4 — Create Spec Folder and Files

Determine the current date (use system date or `date -u +%Y-%m-%d` if needed).

Create the folder: `.claude/specs/YYYY-MM-DD-spec-name/`

Folder naming rules:
- Date prefix: `YYYY-MM-DD`
- Spec name: kebab-case, max 5 words, descriptive
- Examples: `2026-05-23-password-reset-flow`, `2026-05-23-api-rate-limiting`

Then create each file per the templates below.

---

## File Templates

### `spec.md`

```markdown
# Spec Requirements Document

> Spec: [SPEC_NAME]
> Created: [YYYY-MM-DD]

## Overview

[1-2 sentences describing the goal and objective of this feature.]

## User Stories

### [STORY_TITLE]

As a [USER_TYPE], I want to [ACTION], so that [BENEFIT].

[Detailed workflow description — what the user does step by step, what the system does,
what the outcome is.]

## Spec Scope

1. **[Feature Name]** - [One sentence description.]
2. **[Feature Name]** - [One sentence description.]

## Out of Scope

- [Excluded functionality]
- [Excluded functionality]

## Expected Deliverable

1. [Testable, browser-verifiable outcome]
2. [Testable, browser-verifiable outcome]
```

**Constraints:**
- Overview: 1–2 sentences only
- User stories: 1–3 stories
- Spec scope: 1–5 features, one sentence each
- Expected deliverables: 1–3, focused on observable/testable outcomes

---

### `spec-lite.md`

```markdown
# Spec Summary (Lite)

[1–3 sentences summarising the spec's core goal and objective. Optimised for AI context —
dense, precise, no padding.]
```

**Purpose:** This file is loaded into AI context during implementation to orient the model
without loading the full spec. Keep it tight.

---

### `sub-specs/technical-spec.md`

```markdown
# Technical Specification

> For spec: [SPEC_NAME]

## Technical Requirements

- [Specific technical requirement]
- [Specific technical requirement]

## External Dependencies

[Only include if new libraries or packages are needed. Omit section entirely otherwise.]

- **[library-name]** - [Purpose]
  - Justification: [Why this is needed rather than building from scratch]
  - Version: [Required version or constraint]
```

---

### `sub-specs/database-schema.md` *(conditional — only if DB changes needed)*

```markdown
# Database Schema

> For spec: [SPEC_NAME]

## Changes

### New Tables

[Table name, columns, types, constraints]

### Modified Tables

[Table name, changes, migration notes]

## Indexes and Constraints

[Any indexes, foreign keys, unique constraints]

## Migration Notes

[Order of operations, rollback considerations, data backfill if needed]
```

---

### `sub-specs/api-spec.md` *(conditional — only if API changes needed)*

```markdown
# API Specification

> For spec: [SPEC_NAME]

## Endpoints

### [HTTP_METHOD] [/endpoint/path]

**Purpose:** [What this endpoint does]
**Auth required:** [Yes/No]

**Parameters:**
- `param_name` (type, required/optional) — description

**Request body:**
```json
{ "example": "shape" }
```

**Response:**
```json
{ "example": "shape" }
```

**Errors:**
- `400` — [Reason]
- `401` — [Reason]
- `404` — [Reason]
```

---

## Step 5 — User Review

Once all files are created, present a summary and ask for review:

> ✅ Spec created — **[SPEC_NAME]**
>
> **Folder:** `.claude/specs/YYYY-MM-DD-spec-name/`
>
> **Files created:**
> - `spec.md` — main requirements
> - `spec-lite.md` — condensed summary
> - `sub-specs/technical-spec.md` — implementation details
> - *(list any conditional files created)*
>
> Please review and let me know if anything needs adjusting.
> When you're happy, we can move on to creating tasks or starting implementation.

Wait for approval or revision requests before considering the spec done.

---

## Key Principles

**Be concrete.** Name actual files, functions, endpoints, and data shapes where relevant.
Vague specs lead to vague implementations.

**YAGNI.** Only spec what's needed for this feature. Park future enhancements in Out of
Scope rather than designing them in.

**spec-lite is load-bearing.** Write it carefully — it's what the AI reads during
implementation when the full spec is too large for context.

**Conditional sub-specs.** Don't create `database-schema.md` or `api-spec.md` unless
the feature actually requires them. Empty or near-empty files add noise.

**One spec per feature.** If scope creep appears during clarification, note the new idea
as a separate future spec rather than expanding this one.
