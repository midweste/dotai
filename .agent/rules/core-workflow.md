# Workflow Rules

Optimize for correctness, minimalism, and developer experience.

## Operating Principles

- Correctness over cleverness; prefer boring, readable solutions.
- Smallest change that works; don't refactor adjacent code unless it reduces risk.
- Leverage existing patterns before introducing new abstractions.
- Prove it works — validate with tests/build/lint, not "seems right."
- Be explicit about uncertainty; propose safest next step when you can't verify.

## Orchestration

- **Plan mode** for non-trivial tasks (3+ files, multi-component, architectural, production-impacting). Include verification steps in the plan. Stop and re-plan when new information invalidates assumptions.
- **Subagents**: one focused objective per subagent with a concrete deliverable. Merge outputs into actionable synthesis before coding.
- **Incremental delivery**: thin vertical slices → implement → test → verify → expand. Use feature flags/config switches when feasible.
- **Self-improvement**: after corrections, add to `LESSONS.md` (failure mode, signal, prevention rule). Review at session start.
- **Verification before done**: evidence required (tests, lint, build, logs). Ask: "Would a staff engineer approve this diff?"
- **Demand elegance**: pause on non-trivial changes — "Is there a simpler structure?" Don't over-engineer simple fixes.
- **Bug fixing**: reproduce → isolate → fix → regression test → verify. Don't offload debugging to user unless blocked.

## Task Management

Write checklists to `TODO.md`. Include verification tasks. Define acceptance criteria. Mark progress. Capture checkpoint notes. Add results section when done. Update `LESSONS.md` after corrections.

## Communication

- Lead with outcome/impact, not process. Reference concrete artifacts.
- Ask questions only when blocked; batch them with recommended defaults.
- State inferred assumptions. Show verification story (what ran, outcome).
- No busywork updates — checkpoint only on scope changes, risks, or decisions needed.

## Context Management

- Read before write — find authoritative source of truth first. Prefer targeted reads.
- Keep working notes in `TODO.md`; compress when context grows large.
- Prefer explicit names and direct control flow. Control scope creep — log follow-ups as TODOs.

## Error Recovery

- **Stop-the-line**: on unexpected failures, stop features → preserve evidence → re-plan.
- **Triage**: reproduce → localize → reduce → fix root cause → guard with test → verify e2e.
- **Safe fallbacks**: prefer "safe default + warning" over silent failure.
- **Rollback**: keep changes reversible (flags, isolated commits). Ship risky changes disabled-by-default.
- **Instrumentation**: add logging only when it reduces debugging time; remove temp debug output.
