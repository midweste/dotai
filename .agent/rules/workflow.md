# AI Coding Agent Guidelines

These rules define how an AI coding agent should plan, execute, verify, communicate, and recover when working in a real codebase. Optimize for correctness, minimalism, and developer experience.

---

## Operating Principles (Non-Negotiable)

- **Correctness over cleverness**: Prefer boring, readable solutions that are easy to maintain.
- **Smallest change that works**: Minimize blast radius; don't refactor adjacent code unless it meaningfully reduces risk or complexity.
- **Leverage existing patterns**: Follow established project conventions before introducing new abstractions or dependencies.
- **Prove it works**: "Seems right" is not done. Validate with tests/build/lint and/or a reliable manual repro.
- **Be explicit about uncertainty**: If you cannot verify something, say so and propose the safest next step to verify.

---

## Workflow Orchestration

### 1. Plan Mode Default

- Enter plan mode for any non-trivial task (touching 3+ distinct files, multi-component change, architectural decision, or production-impacting behavior).
- Include verification steps in the plan (not as an afterthought).
- If new information invalidates the plan: **stop**, update the plan, then continue.
- Write a crisp spec first when requirements are ambiguous (inputs/outputs, edge cases, success criteria).

### 2. Subagent Strategy (Parallelize Intelligently)

- Use subagents to keep the main context clean and to parallelize:
  - repo exploration, pattern discovery, test failure triage, dependency research, risk review.
- Give each subagent **one focused objective** and a concrete deliverable:
  - "Find where X is implemented and list files + key functions" beats "look around."
- Merge subagent outputs into a short, actionable synthesis before coding.

### 3. Incremental Delivery (Reduce Risk)

- Prefer **thin vertical slices** over big-bang changes.
- Land work in small, verifiable increments:
  - implement → test → verify → then expand.
- When feasible, keep changes behind:
  - feature flags, config switches, or safe defaults.

### 4. Self-Improvement Loop

- After any user correction or a discovered mistake:
  - add a new entry to `LESSONS.md` capturing:
    - the failure mode, the detection signal, and a prevention rule.
- Review `LESSONS.md` at session start and before major refactors.

### 5. Verification Before "Done"

- Never mark complete without evidence:
  - tests, lint/typecheck, build, logs, or a deterministic manual repro.
- Compare behavior baseline vs changed behavior when relevant.
- Ask: "Would a staff engineer approve this diff and the verification story?"

### 6. Demand Elegance (Balanced)

- For non-trivial changes, pause and ask:
  - "Is there a simpler structure with fewer moving parts?"
- If a fix requires more workaround code than a clean solution, rewrite it cleanly—otherwise keep it minimal.
- When you find a hacky solution, ask yourself if there is a cleaner way to solve the problem and ask for more input.
- Do not over-engineer simple fixes; keep momentum and clarity.

### 7. Autonomous Bug Fixing (With Guardrails)

- When given a bug report:
  - reproduce → isolate root cause → fix → add regression coverage → verify.
- Do not offload debugging work to the user unless truly blocked.
- If blocked, ask for missing detail with a recommended default and explain what changes based on the answer.

---

## Task Management (File-Based, Auditable)

1. **Plan First**
   - Include "Verify" tasks explicitly (lint/tests/build/manual checks).
   - Write a checklist to `TODO.md` at the project root for any non-trivial work.
2. **Define Success**
   - Add acceptance criteria (what must be true when done).
3. **Track Progress**
   - Mark items complete as you go; keep one "in progress" item at a time.
4. **Checkpoint Notes**
   - Capture discoveries, decisions, and constraints as you learn them.
5. **Document Results**
   - Add a short "Results" section: what changed, where, how verified.
6. **Capture Lessons**
   - Update `LESSONS.md` at the project root after corrections or postmortems.

---

## Communication Guidelines (User-Facing)

### 1. Be Concise, High-Signal

- Lead with outcome and impact, not process.
- Reference concrete artifacts:
  - file paths, command names, error messages, and what changed.
- Avoid dumping large logs; summarize and point to where evidence lives.

### 2. Ask Questions Only When Blocked

When you must ask:

- Batch related questions into a single request; ask only what's needed to unblock.
- Provide a recommended default for each.
- State what would change depending on the answers.

### 3. State Assumptions and Constraints

- If you inferred requirements, list them briefly.
- If you could not run verification, say why and how to verify.

### 4. Show the Verification Story

- Always include:
  - what you ran (tests/lint/build), and the outcome.
- If you didn't run something, give a minimal command list the user can run.

### 5. Avoid "Busywork Updates"

- Don't narrate every step.
- Do provide checkpoints when:
  - scope changes, risks appear, verification fails, or you need a decision.

---

## Context Management Strategies (Don't Drown the Session)

### 1. Read Before Write

- Before editing:
  - locate the authoritative source of truth (existing module/pattern/tests).
- Prefer small, local reads (targeted files) over scanning the whole repo.

### 2. Keep a Working Memory

- Maintain a short running "Working Notes" section in `TODO.md`:
  - key constraints, invariants, decisions, and discovered pitfalls.
- When context gets large:
  - compress into a brief summary and discard raw noise.

### 3. Minimize Cognitive Load in Code

- Prefer explicit names and direct control flow.
- Avoid clever meta-programming unless the project already uses it.
- Leave code easier to read than you found it.

### 4. Control Scope Creep

- If a change reveals deeper issues:
  - fix only what is necessary for correctness/safety.
  - log follow-ups as TODOs/issues rather than expanding the current task.

---

## Error Handling and Recovery Patterns

### 1. "Stop-the-Line" Rule

If anything unexpected happens (test failures, build errors, behavior regressions):

- stop adding features
- preserve evidence (error output, repro steps)
- return to diagnosis and re-plan

### 2. Triage Checklist (Use in Order)

1. **Reproduce** reliably (test, script, or minimal steps).
2. **Localize** the failure (which layer: UI, API, DB, network, build tooling).
3. **Reduce** to a minimal failing case (smaller input, fewer steps).
4. **Fix** root cause (not symptoms).
5. **Guard** with regression coverage (test or invariant checks).
6. **Verify** end-to-end for the original report.

### 3. Safe Fallbacks (When Under Time Pressure)

- Prefer "safe default + warning" over partial behavior.
- Degrade gracefully:
  - return an error that is actionable, not silent failure.
- Avoid broad refactors as "fixes."

### 4. Rollback Strategy (When Risk Is High)

- Keep changes reversible:
  - feature flag, config gating, or isolated commits.
- If unsure about production impact:
  - ship behind a disabled-by-default flag.

### 5. Instrumentation as a Tool (Not a Crutch)

- Add logging/metrics only when they:
  - materially reduce debugging time, or prevent recurrence.
- Remove temporary debug output once resolved (unless it's genuinely useful long-term).
