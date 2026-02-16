---
description: "CRITICAL: All work MUST be parallelized. Split into gateway agents via run_command whenever possible."
---

# Parallel Evaluation

> [!CAUTION]
>
> CRITICAL: All work MUST be parallelized. Evaluate every task for parallelism before starting. If it can be split, it MUST be split.

This applies to **all work** — implementation, edits, analysis, research, testing, verification. You are the orchestrator: dispatch, work in parallel, validate results.

## Mechanism

`run_command` dispatching to `.agent/bin/gemini-gateway` is the ONLY parallel mechanism.

```bash
run_command("echo '...' | .agent/bin/gemini-gateway --model <quick|fast|think|deep> --label 'description' --timeout <30|45|90>")
```

## Parallelism Decision

1. **List** all discrete tasks (e.g., "update 5 classes" = 5 tasks)
2. **Check independence** — parallel only if: different files, no output dependency, no shared mutable state
3. **Batch** independent tasks into parallel groups; sequence dependent ones
4. **Dispatch** batch → work on your own tasks → validate → dispatch next batch

### Common Patterns

| Parallel ✅                    | Sequential ❌                 |
| ------------------------------ | ----------------------------- |
| Edit different files           | Edit same file                |
| Write impl + tests (from spec) | Add method + test that method |
| Research topic A + B           | Update interface + consumers  |
| Spot-check N items (read-only) | Task B depends on A's output  |

## Orchestrator Role

1. **Evaluate** parallelism graph before work starts
2. **Dispatch** independent tasks to gateway
3. **Work** on your own tasks (never idle-wait)
4. **Validate** agent output for correctness
5. **Fix** minor issues inline; **retry** wrong approaches (max 2, then do it yourself)

## Model Selection

| Tier    | Use for                                  | Timeout |
| ------- | ---------------------------------------- | ------- |
| `quick` | Config, spot-checks, single reads        | 30s     |
| `fast`  | Log analysis, data sampling, small impls | 45s     |
| `think` | Multi-file refactors, complex validation | 90s     |
| `deep`  | Architecture review, complex reasoning   | 90s     |

## Health Check

```bash
.agent/bin/gemini-gateway --status
```

`ok` → dispatch freely · `slow` → 1 at a time · `saturated` → do it yourself

## Dispatch Flow

Dispatch as background `run_command` → work on own tasks → check `--jobs` after ~30s → cancel if over timeout threshold → validate on completion.

## When NOT to Split

Same file edits, output dependencies, singular tasks (one grep/one edit), gateway saturated, gateway binary not installed — proceed single-threaded without parallelism reporting.

## Mandatory Reporting

> [!IMPORTANT]
> Always report parallel usage to user.

- **On dispatch**: count, task descriptions, model tier, what you're doing meanwhile
- **On complete**: each result (pass/fail), issues resolved, time saved
- **On skip**: why (shared files, dependencies, <30s task, saturated)
