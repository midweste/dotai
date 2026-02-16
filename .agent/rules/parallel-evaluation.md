---
description: "CRITICAL: All work MUST be parallelized. Never perform tasks sequentially when they can be dispatched concurrently. Always evaluate work for parallelism. Split into gateway agents via run_command whenever possible. You orchestrate and validate."
---

# Parallel Evaluation

> [!CAUTION]
>
> CRITICAL: All work MUST be parallelized. Never perform tasks sequentially when they can be dispatched concurrently. Before starting ANY work, evaluate whether it can be split into independent parallel tasks dispatched via `run_command` to the Gemini gateway. If it can be split, it MUST be split.

This applies to **all work** — code implementation, file edits, analysis, research, testing, and verification. Not just verification. You are the orchestrating agent: you dispatch, you work on your own tasks in parallel, and you validate the results that come back.

### The Only Parallel Mechanism

**`run_command`** dispatching to `.agent/bin/gemini-gateway` is the ONLY way to run parallel work. No other tool runs in parallel. Every parallel dispatch goes through the gateway.

```bash
run_command(".agent/bin/gemini-gateway --model <quick|fast|think|deep> --label 'description' --prompt '...' --timeout <30|45|90>")
```

### How to Determine What Can Be Parallelized

Before starting work, ask these questions in order:

#### Step 1: List all discrete tasks

Break the work into the smallest independent units. Example: "Update 5 filter classes" → 5 separate file edits.

#### Step 2: Build a dependency graph

For each pair of tasks, ask:

- **Do they edit the same file?** → Sequential (agents can't safely co-edit)
- **Does task B depend on task A's output?** → Sequential (B needs A's result)
- **Do they read shared state that either modifies?** → Sequential (race condition risk)
- **Are they completely independent?** → **Parallel** ✅

#### Step 3: Group into parallel batches

Tasks that pass all three independence checks go into the same parallel batch. Tasks with dependencies form a sequence. Visualize it:

```
Batch 1 (parallel):  [Task A] [Task B] [Task C]    ← no shared files
    ↓ wait for all
Batch 2 (parallel):  [Task D] [Task E]              ← depend on Batch 1 output
    ↓ wait for all
Batch 3 (sequential): [Task F]                       ← edits file from D
```

#### Step 4: Dispatch and work

- Dispatch Batch 1 agents via `run_command`
- Work on your own non-conflicting tasks while agents run
- When Batch 1 completes, validate results, then dispatch Batch 2
- Continue until all batches complete

### Common Parallelism Patterns

| Scenario                                            | Parallel? | Reasoning                                       |
| --------------------------------------------------- | --------- | ----------------------------------------------- |
| Update 5 filter classes (different files)           | ✅ Yes    | No shared files                                 |
| Write implementation + write tests                  | ✅ Yes    | Different files, tests can be written from spec |
| Update interface + update all consumers             | ❌ No     | Consumers depend on interface changes           |
| Spot-check 10 products against filters              | ✅ Yes    | Read-only, no shared state                      |
| Refactor class A + refactor class B (no dependency) | ✅ Yes    | Independent files                               |
| Add method to class + add test for that method      | ❌ No     | Test depends on the method existing             |
| Research topic A + research topic B                 | ✅ Yes    | Independent analysis                            |
| Fix bug in file X + fix bug in file Y               | ✅ Yes    | Different files, different bugs                 |

### Your Role as Orchestrator

You are NOT just dispatching and waiting. Your responsibilities:

1. **Evaluate** — determine the parallelism graph before any work starts
2. **Dispatch** — send independent tasks to gateway agents
3. **Work** — do your own tasks while agents run (never idle-wait)
4. **Validate** — when agents return, review their output for correctness
5. **Fix** — if agent output has minor issues, fix inline (faster than re-dispatch)
6. **Retry** — if agent approach was wrong, re-dispatch with corrective instructions (max 2 retries before doing it yourself)

### Model Selection

| Tier    | Use for                                               | Timeout |
| ------- | ----------------------------------------------------- | ------- |
| `quick` | Config changes, spot-checks, single-file reads        | 30s     |
| `fast`  | Log analysis, data sampling, small implementations    | 45s     |
| `think` | Multi-file refactors, new classes, complex validation | 90s     |
| `deep`  | Architecture review, complex reasoning                | 90s     |

### Pre-Dispatch Health Check

```bash
.agent/bin/gemini-gateway --status
```

| Health      | Action               |
| ----------- | -------------------- |
| `ok`        | Dispatch freely      |
| `slow`      | Dispatch 1 at a time |
| `saturated` | Do it yourself       |

### Dispatch-and-Recover

```
1. Dispatch agents as background run_command calls
2. Continue your own work — never idle-wait
3. After ~30s: .agent/bin/gemini-gateway --jobs
   → running_time_s < 45 (fast) / < 60 (think): normal
   → over threshold: cancel, do it yourself
4. When your own work is done, check command_status on each
5. Review and validate agent output
```

### When NOT to Split

- Tasks that edit the same file
- Task B depends on Task A's output
- Task is inherently singular (one grep, one file edit) — if it involves multiple files or multiple analyses, it CAN be split
- Gateway health is `saturated`

### Mandatory Reporting

> [!IMPORTANT]
> **Always report parallel job usage to the user.** This is non-negotiable.

When you **dispatch** parallel agents, report:

- How many agents dispatched and what each is doing
- Which model tier was used and why
- What you're working on while they run

When agents **complete**, report:

- Each agent's result (pass/fail, what it found or changed)
- Any issues found and how you resolved them
- Total time saved vs sequential execution

When you **skip** parallelism, report:

- Why you chose not to split (shared files, dependencies, <30s task, gateway saturated)
- Brief justification so the user can course-correct if they disagree

### Key Principle

**Split first, code second.** Every minute an agent could be running but isn't is wasted throughput. You are the orchestrator — dispatch, work, validate, integrate.
