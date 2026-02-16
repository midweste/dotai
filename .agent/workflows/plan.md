---
description: "SDLC Step 1/3 — Plan a feature or change by reconciling requirements against actual code, producing an implementation plan, and iterating until approved"
---

# /plan — Plan a Feature or Change

Research the codebase, reconcile intent against reality, surface questions, and produce an implementation plan artifact for inline iteration. The source document is only written/augmented on approval.

**Input**: A description, existing doc, or debt doc
**Output**: Approved planning doc (status `Approved`) + implementation plan artifact

## SDLC Pipeline

**Full path**: **`/plan`** → `/implement` → `/close`
**Lightweight**: `/capture` (self-contained — for ad-hoc fixes)

**You are here**: `/plan` — creating the implementation plan and iterating until approved

## Key Principle

**The artifact is the working draft. The source doc is the final record.**

- All iteration (inline comments, revisions, decisions) happens on the **implementation plan artifact**
- The source doc is only written/augmented **after the user approves**
- This avoids dual-document maintenance and revision churn during iteration

## Steps

### 1. Capture the intent

Read what the user provided. This can be:

- **A description** in conversation ("I want to add caching to the pipeline")
- **An existing doc** (`/plan @[docs/some-spec.md]`) — old planning doc, spec from Slack, rough notes
- **A debt doc** from a previous `/close`

For existing docs, read the full document and **check its frontmatter `> Status:` line** (not body text):

| Status                     | Action                                                                                 |
| -------------------------- | -------------------------------------------------------------------------------------- |
| No status / unknown format | Continue — needs planning work                                                         |
| `Draft`                    | Continue — needs planning work                                                         |
| `Planned`                  | Continue — needs implementation plan (skip to step 4)                                  |
| `Approved`                 | Tell user: "This doc is approved. Run `/implement`."                                   |
| `In Progress`              | Tell user: "This doc is in progress. Run `/implement` to resume."                      |
| `Done`                     | Tell user: "This doc is already done. If not in `finished/`, run `/close` to file it." |

This makes `/plan` the safe default entry point — you can always run `/plan @[any-doc.md]` without reading it first, and it will either do planning work or redirect you.

> [!CAUTION]
> **Do NOT augment the source doc yet.** Read it for context only. The source doc gets written/augmented in step 7 (after approval). For existing docs, treat the content as requirements — the original text is the spec.

> **Note**: For small fixes already done in this conversation, use `/capture` instead — it's faster and self-contained.

Identify:

- **Goal**: What outcome the user wants
- **Scope**: What's in vs out
- **Constraints**: Must-use patterns, existing infrastructure, things to avoid
- **Referenced code**: Files, classes, or modules mentioned or implied

If intent is unclear, ask the user to clarify **before** doing any research. Batch all questions into one ask.

### 2. Research the codebase (deep)

// turbo

Investigate the actual code to understand current state. For each area the plan touches:

- Read relevant files, classes, and interfaces
- Check for existing patterns the plan should follow
- Identify what already exists vs what needs to be built
- Note any dependencies or downstream effects
- **Trace construction sites**: For every class being modified, find all places it's instantiated or injected. These are often missed in plans.
- **Trace internal dependencies**: For methods being moved or extracted, check what other `$this->` methods they call (logging helpers, utility methods, traits). These must exist on the destination class.
- **Identify affected tests**: Search for test files that mock, instantiate, or assert on any class being changed. These MUST be included in the work plan.

**Do NOT make assumptions.** If the plan says "we already have X", verify it exists and works as described.

### 3. Ensure a source doc exists (stub only)

// turbo

The source doc is the permanent record that lives in `docs/`. At this stage, create only a minimal stub if one doesn't already exist. **Do not add planning sections yet.**

**If a source doc already exists**: Leave it as-is. Do not modify it.

**If no source doc exists** (user gave a description in chat): Create a stub:

```markdown
# <Title>

> Created: YYYY-MM-DD HH:MM (local)
> Status: Draft

## Requirement (Original)

<paste the user's original requirement or description here>
```

Use datetime-prefixed naming: `docs/YYYY-MM-DDTHHMM--<slug>.md`

That's it — just frontmatter and the original requirement. The full planning sections come later (step 7).

### 4. Create the implementation plan artifact

Create an Antigravity **implementation_plan** artifact in the brain directory (`implementation_plan.md`). This is the **primary working document** — all iteration happens here via inline comments.

**Do NOT ask questions in chat.** Batch all questions, decisions, and findings directly into the artifact so the user can comment contextually on every line.

> [!IMPORTANT]
> **Mid-implementation detection**: If reconciliation reveals most items are already done (e.g., 8 of 10 phases complete), the doc is not really `Draft` — it's mid-implementation without tracking. Flag this to the user:
>
> "This doc appears to be mid-implementation (N of M items already done). Consider running `/implement` to add a Progress table and track the remaining work, rather than re-planning."
>
> Let the user decide whether to continue with `/plan` or switch to `/implement`.

**Template enforcement**: The following sections are REQUIRED and must not be empty:

- **Reconciliation** — verify every claim against actual code
- **Decisions Needed** — surface unknowns explicitly (even if you think you know the answer)
- **Decisions Made** — capture decisions made during planning (even if tentative)

If any of these are empty when presenting for review, go back and fill them. A plan with no open questions is suspicious — it usually means questions weren't asked, not that there aren't any.

```markdown
# <Plan Title> — Implementation Plan

Source: [<filename>](file:///absolute/path/to/source/doc.md)

## Reconciliation

For each actionable item, report its status against actual code:

| Item | Intent | Code Reality | Status |
| ---- | ------ | ------------ | ------ |
| ...  | ...    | ...          | ...    |

Statuses: `✅ Confirmed` | `⚠️ Needs verification` | `⬜ Needs implementation` | `🚫 Blocked` | `❌ Drift`

## Decisions Needed

Questions that must be answered before implementation. Number each one:

1. **<Topic>**: <question> (affects phases X, Y)

## Decisions Made

Record answers as they come in. Keep the numbering matched:

1. **<Topic>**: <answer> — Rationale: <why>

## Work Plan

Table of remaining items (confirmed-done items excluded). Include files and parallelism:

| Phase | Description   | Files Touched        | Parallelism               |
| ----- | ------------- | -------------------- | ------------------------- |
| 1     | <description> | file1.php, file2.php | `parallel:A`              |
| 2     | <description> | file3.php            | `parallel:A`              |
| 3     | <description> | file1.php, file4.php | `sequential (depends: 1)` |

**Parallelism rules:**

- `parallel:X` — can run concurrently with other items in the same group
- `sequential` or `sequential (depends: N)` — must wait for dependencies
- **Items in the same parallel group must NOT share files** — if two phases touch the same file, they MUST be `sequential`
- Default is `sequential` if not annotated

### Subagent Dispatch Plan

For each parallel group, specify the dispatch strategy. This section is read by `/implement` during the parallelism triage gate:

| Group | Phases | Model Tier | Timeout | Rationale                             |
| ----- | ------ | ---------- | ------- | ------------------------------------- |
| A     | 1, 2   | fast       | 45s     | Simple file moves + namespace changes |

Model tiers: `quick` (trivial), `fast` (simple), `think` (multi-file), `deep` (complex logic).
If **no phases are parallelizable**, write: "All phases are sequential — no subagent dispatch needed" and explain why (e.g., "every phase depends on the previous one's output").

## Proposed Changes

Group by component. For each file, note [NEW], [MODIFY], or [DELETE]:

### <Component Name>

#### [MODIFY] [filename.php](file:///path/to/file)

Brief description + code sketch if helpful.

## Test Impact

List test files that need updating due to mock/assertion changes:

- [ ] [TestFile.php](file:///path) — what needs to change

## Verification Plan

How you'll verify each change works.
```

### 5. Present for review

Present the **implementation plan artifact** to the user for review using `notify_user` with `BlockedOnUser: true`.

The artifact IS the communication channel. Keep the chat message brief — just flag:

- How many decisions need answers
- Any critical drift or blockers found
- That the user should comment inline on the artifact

> [!NOTE]
> Only present the implementation plan artifact for review — not the source doc. The source doc is a stub at this point and doesn't need review.

### 6. Iterate until approved

The user may:

- **Add inline comments** on specific sections (questions, proposed changes, etc.)
- **Answer decision questions** (move answers to Decisions Made)
- **Request changes** to scope, phasing, or approach

When the user responds:

1. Read feedback (inline comments + chat)
2. Re-research any code areas they questioned
3. Update the **implementation plan artifact only**
4. Move answered questions from Decisions Needed to Decisions Made
5. Present for re-review

**Repeat until the user approves.** Approval signals = "looks good", "approved", "let's do it", `/implement`, or similar.

### 7. Write the source document

// turbo

Once approved, **now** augment the source document with the finalized plan. This is the permanent record.

**For existing docs**: Add the planning sections below existing content. Do NOT rewrite or reorganize the original content.

**For stub docs**: Expand the stub with the full planning sections.

> [!CAUTION]
> **Never overwrite existing doc content.** The original text — code blocks, architecture diagrams, phase descriptions, method signatures — is the spec. Preserve it. Add sections around it or below it.

Add these sections (sourced from the finalized artifact):

```markdown
## Context

Why this work exists. Link to prior art, conversations, or docs.

## Goals

- Goal 1
- Goal 2

## Current State

What exists today. Reference actual code with file links.

## Proposal

### Phase 1: <Name>

What will change, which files, what approach.

#### Affected Files

- [MODIFY] [filename.php](file:///path) — what changes
- [NEW] [filename.php](file:///path) — what it does

## Reconciliation

| Item | Intent | Code Reality | Status |
| ---- | ------ | ------------ | ------ |

## Decisions

1. **<Topic>**: <what was decided>
   - **Rationale**: <why>

## Open Questions

(All resolved — see Decisions above)

## Verification Plan

How each phase will be verified.

## Changelog

| Datetime         | Change        |
| ---------------- | ------------- |
| YYYY-MM-DD HH:MM | Initial draft |
| YYYY-MM-DD HH:MM | Approved      |
```

### 8. Mark as approved

// turbo

- Set the source document's status to `Approved`
- Add a changelog entry with the approval datetime

Tell the user: `Plan approved. Run /implement docs/<filename>.md to begin implementation.`
