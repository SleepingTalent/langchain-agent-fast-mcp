---
name: brainstorm
description: >
  Run a structured brainstorming session to explore and refine ideas before committing to a plan,
  design, or specification. Use this skill whenever the user wants to think through an idea
  collaboratively — especially before writing a spec, designing a feature, solving a technical
  problem, planning a project, or making a design decision. Trigger on phrases like "let's
  brainstorm", "I have an idea", "help me think through", "not sure how to approach", "explore
  options", "what are my options", or any time the user presents a rough or unformed idea that
  needs structured exploration before action. Also trigger when the user is about to create a
  formal document (spec, plan, PRD, design doc) and hasn't yet validated their approach.
---

# Brainstorm Skill

Explore and refine ideas through natural collaborative dialogue. Turn rough ideas into
well-formed designs by asking questions, exploring alternatives, and validating assumptions
incrementally — before committing to a plan or writing formal documentation.

**Purpose:** Surface critical decisions early, reduce rework, and build clarity through
structured exploration.

---

## Core Principles

**One question at a time.** Never overwhelm. Ask one question, wait for a response,
synthesise, then ask the next. This is non-negotiable.

**Prefer multiple choice.** When possible, offer 2–4 specific options rather than open-ended
questions. Makes it easier for the user to respond quickly and move forward.

**YAGNI ruthlessly.** Apply "You Aren't Gonna Need It" to every feature and component.
Start with the simplest approach that solves the core problem. Note future enhancements
separately — don't design them in.

**Explore alternatives.** Always present 2–3 different approaches before settling on one.
Show trade-offs clearly so the user can make an informed choice.

**Incremental validation.** Present design in small sections (~200–300 words). Validate
each section before continuing. It's much cheaper to adjust now than after implementation.

**Stay flexible.** Be ready to backtrack, clarify, or adjust when something doesn't land.
The goal is understanding, not completing a checklist.

---

## Process

### Step 1 — Capture the Initial Idea

Let the user describe their idea in any format (brief or detailed, prose or bullets,
problem or feature request). Reflect it back for confirmation before proceeding.

**Reflection template:**

> I understand you want to [BRIEF_SUMMARY].
>
> Before we explore this, let me confirm:
> - **Goal:** [PERCEIVED_GOAL]
> - **Users/stakeholders affected:** [WHO]
> - **Rough scope:** [INITIAL_ESTIMATE]
>
> Is this right, or should I adjust my understanding?

Wait for confirmation before moving to Step 2.

---

### Step 2 — Explore Through Targeted Questions

Ask questions one at a time to deepen understanding. Focus on *why*, *who*, and *what*
before touching *how*.

**Question types:**
- **Multiple choice (preferred):** Offer 2–4 options. E.g. "Which matters more right now:
  A) speed of delivery, B) long-term maintainability, C) minimal scope?"
- **Open-ended (when options aren't clear yet):** E.g. "What problem does this solve that
  the current approach doesn't?"

**Focus areas to cover (in any order, following the conversation):**

*Purpose*
- What problem does this solve?
- Who benefits and how?
- What does success look like?

*Constraints*
- Technical limitations or hard requirements
- Performance or scale expectations
- Integration points with existing systems

*Scope boundaries*
- What's explicitly in?
- What's explicitly out?
- What can be deferred?

Adapt to the conversation. Don't force a rigid order — follow interesting threads.

---

### Step 3 — Propose Alternative Approaches

Once you have enough context, present 2–3 distinct approaches with trade-offs. Lead with
a recommendation and explain the reasoning.

**Structure for each approach:**
- Brief description (1–2 sentences)
- Key benefits
- Key drawbacks or risks
- Rough complexity: Simple / Moderate / Complex

**Presentation template:**

> Based on what you've shared, here are a few ways to approach this:
>
> **Approach A: [NAME]** *(Recommended)*
> [DESCRIPTION]
> ✅ Benefits: [LIST]
> ⚠️ Trade-offs: [LIST]
> Complexity: [Simple/Moderate/Complex]
>
> **Why I recommend this:** [REASONING — mission alignment, constraints, effort, impact]
>
> **Approach B: [NAME]**
> [DESCRIPTION]
> ✅ Benefits: [LIST]
> ⚠️ Trade-offs: [LIST]
> Complexity: [Simple/Moderate/Complex]
>
> **Approach C: [NAME]** *(if applicable)*
> ...
>
> Which direction resonates? We can also blend aspects of these.

Wait for the user to select or suggest a hybrid before proceeding.

---

### Step 4 — Present Design Incrementally

Once an approach is chosen, build out the design in sections of ~200–300 words each.
After each section, ask: *"Does this make sense so far? Any concerns before I continue?"*

**Typical section order** (adapt as needed):
1. Architecture overview — components and their relationships
2. Data flow — how information moves through the system
3. Key components — detailed breakdown of main pieces
4. Integration points — how this connects to existing systems or workflows
5. Error handling — failure modes and recovery
6. Testing / validation strategy — how to know it works

Apply YAGNI at every section. If something feels speculative, flag it and park it rather
than designing it in.

---

### Step 5 — Document the Brainstorm

Once the design is validated, write the brainstorm to disk before summarising.

**Folder:** `.claude/specs/YYYY-MM-DD-topic/`
- Date: current date in `YYYY-MM-DD` format (use `date -u +%Y-%m-%d` if needed)
- Topic: kebab-case, max 5 words, descriptive
- Examples: `2026-05-23-auth-flow`, `2026-05-23-rate-limiting`

**File:** `brainstorm.md` inside that folder

This folder is the same one `/create-spec` will write into — `brainstorm.md` serves as
the reference document when formalising the spec.

**`brainstorm.md` template:**

```markdown
# Brainstorm: [FEATURE_NAME]

> Created: [YYYY-MM-DD]
> Status: Design Exploration (not yet a formal spec)

## Problem Statement

[Description of the problem being solved.]

**Target Users:** [Who benefits]
**Success Criteria:** [How we know it works]

## Approaches Considered

### Approach A: [NAME]
[Description]
✅ Benefits: [list]
⚠️ Trade-offs: [list]

### Approach B: [NAME]
[Description]
✅ Benefits: [list]
⚠️ Trade-offs: [list]

### Selected: Approach [A/B/Hybrid]
**Reasoning:** [Why this approach]

## Design Overview

### Architecture
[High-level component structure]

### Data Flow
[How data moves through the system]

### Key Components
[Detailed breakdown of main pieces]

### Integration Points
[How this connects to existing systems]

### Error Handling
[Failure modes and recovery]

### Testing Strategy
[How to validate it works]

## Key Decisions

1. **[Decision topic]:** [Decision made] — [Rationale]
2. **[Decision topic]:** [Decision made] — [Rationale]

## Open Questions

- [ ] [Question to resolve before spec creation]
```

Only include Open Questions if there are genuinely unresolved items. Omit the section
if everything is settled.

---

### Step 6 — Summarise and Suggest Next Steps

After writing the file, provide a summary and clear next step.

> ✅ **Brainstorm complete — [TOPIC]**
>
> **Saved to:** `.claude/specs/YYYY-MM-DD-topic/brainstorm.md`
>
> **Summary:**
> - **Problem:** [BRIEF]
> - **Approach selected:** [CHOSEN] — [ONE LINE REASON]
> - **Key decisions:** [2–3 BULLET POINTS]
> - **Open questions:** [LIST OR "None — ready to proceed"]
>
> **Next step:** Run `/create-spec` to formalise this into a full specification.
> The brainstorm will be used as input and will remain as reference documentation.
>
> Want to refine anything first, or ready to move forward?

---

## Notes

- If the user says "just vibe with me" or wants a less structured session, drop the
  templates and have a natural exploratory conversation. The principles still apply —
  especially one-question-at-a-time.
- For highly technical topics, name actual files, functions, endpoints, or data shapes
  when concrete examples would help clarity.
- If a brainstorm reveals that the idea needs more research or has a blocking dependency,
  surface that clearly rather than designing around it.
