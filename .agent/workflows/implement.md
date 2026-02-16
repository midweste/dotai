---
description: "SDLC Step 2/3 — Implement an approved planning document iteratively, working through items one at a time with progress reporting"
---

# /implement — Implement a Planning Document

Execute an approved planning document item by item. Supports resuming across conversation boundaries — reads doc status to pick up where left off.

**Input**: Planning doc path (status must be `Approved` or `In Progress`)
**Output**: Code changes, progress tracked in source doc, blocked items flagged

## SDLC Pipeline

**Full path**: `/plan` → **`/implement`** → `/close`
**Lightweight**: `/capture` (self-contained — for ad-hoc fixes)

**You are here**: `/implement` — executing the approved plan

## Steps

### 1. Load the document and plan

Read the target document. Check the frontmatter `> Status:` line:

- **`Approved`**: Fresh start — set status to `In Progress` and begin
- **`In Progress`**: Resuming — scan the `## Progress` section (see step 2) to identify what's already done vs remaining
- **`Draft` or `Planned`**: Tell user: "This doc needs planning. Run `/plan`."
- **`Done`**: Tell user: "This doc is already done. Run `/close` to file it."
- **Anything else**: Tell user which step to run based on the status.

If an implementation plan artifact exists in the brain directory, load it to understand the reconciliation and work plan. If not, create one using the same structure as `/plan` step 4.

// turbo

### 2. Mark the source document and initialize progress tracking

// turbo

- Set the source document's status to `In Progress` (if not already)
- If the source document has a Decisions section, sync decisions from the artifact into it
- **Add a `## Progress` section** to the source document (if it doesn't exist). This is the checkpoint that enables multi-session resumption:

```markdown
## Progress

| Phase | Status   | Notes |
| ----- | -------- | ----- |
| 1     | ⬜ Ready |       |
| 2     | ⬜ Ready |       |
| 3     | ⬜ Ready |       |
```

Phase statuses: `⬜ Ready` | `🔧 In Progress` | `✅ Done` | `🚫 Blocked` | `🗑️ Debt`

This table is the **single source of truth** for resumption. A new conversation reads this table to know exactly where to pick up.

### 3. Implement iteratively

Work through items from the Progress table. **Before touching any code**, triage for parallelism.

// turbo

#### Parallelism triage (MANDATORY — do this first)

Scan the implementation plan's Work Plan table for `parallel:X` annotations:

1. **If parallel groups exist**: dispatch subagents for those groups FIRST (see "Parallel items" below), then work on sequential items while agents run.
2. **If no parallel annotations exist**: ask yourself — "Could any of these phases run independently?" Phases that touch **completely different files** are candidates. If yes, annotate them and dispatch.
3. **If everything is truly sequential**: proceed to sequential items below.

> [!IMPORTANT]
> **Dispatch parallel work before starting sequential work.** Subagents take wall-clock time. If you start sequential work first, you waste the time those agents could have been running in the background. The optimal pattern is: dispatch parallel agents → work on non-conflicting sequential items → check agent results when your work is done.
>
> If you choose NOT to dispatch subagents for phases marked `parallel:X`, you MUST note why in the Progress table (e.g., "files overlap", "too simple to justify overhead", "gateway saturated").

#### Sequential items (default)

- Pick the next `⬜ Ready` or `🔧 In Progress` item from the Progress table
- Set its status to `🔧 In Progress`
- Implement it (code changes, config, migrations, etc.)
- Verify it works (run tests, lint, manual check as appropriate)
- Set its status to `✅ Done` in the Progress table
- Commit or note the changes

#### Parallel items (when Work Plan has `parallel:X` annotations)

When the implementation plan's Work Plan table includes `Parallelism` annotations:

1. **Group** all `⬜ Ready` items that share the same `parallel:X` annotation
2. **Validate file isolation** — confirm no files are shared between items in the group. If overlap exists, fall back to sequential.
3. **Select model and timeout** per phase based on complexity:
   - **Quick** (`quick`, `--timeout 30`) — trivial one-liners, config changes, version bumps (2.5 Flash)
   - **Fast** (`fast`, `--timeout 45`) — simple methods, renames, small refactors (3 Flash)
   - **Think** (`think`, `--timeout 90`) — multi-file refactors, new classes (2.5 Pro)
   - **Deep** (`deep`, `--timeout 90`) — architecture, complex logic, deepest reasoning (3 Pro)
4. **Pre-batch health check** — before dispatching a parallel group, query the gateway:
   ```bash
   .agent/bin/gemini-gateway --status   # queue depth + health per model
   .agent/bin/gemini-gateway --stats    # p95_execution_s, success_rate, current_min_gap_ms
   ```
   Use this to decide:
   - **`health: ok`** → dispatch full batch
   - **`health: slow`** → dispatch 1 at a time, wider spacing — gateway is recovering from rate limits
   - **`health: saturated`** → no slots available, do the work yourself or wait
   - **`p95_execution_s`** → use as `--timeout` if available (e.g., p95 is 15s for fast → `--timeout 30` gives 2× headroom)
   - **`success_rate < 0.7`** → high failure rate, consider doing work sequentially on the main thread
5. **Dispatch via gateway** — one `run_command` per agent. The gateway handles pacing, queueing, and rate-limit retries. **No manual stagger needed.**
   - Available models: `quick`, `fast`, `think`, `deep`
   - Only 2 per model run concurrently — additional jobs **queue automatically** and execute when a slot opens
   - **Fire-and-forget pattern**: if you're working on a complex task for several minutes, queue many small jobs upfront — they'll trickle through while you work. Check `command_status` on each when your own work is done.

```bash
.agent/bin/gemini-gateway --model <quick|fast|think|deep> --label "Phase N: description" --prompt "
You are implementing Phase N of a plan for the project at $(pwd).
```

## Task

<phase description from Work Plan>

## Acceptance Criteria

- <specific measurable outcomes this phase must achieve>
- All modified code must pass linting and existing tests
- Follow existing patterns in the codebase (check neighboring methods for style)

## File Scope

ONLY edit these files: <files from Files Touched column>
Do NOT create new files or touch any other files.

## Output

When done, report:

1. What you changed (file + line range)
2. How it satisfies the acceptance criteria
3. Any concerns or assumptions you made
   " --timeout <45|90>

```

> **Timeout guidance**: Use `--timeout 45` for flash tasks (they average 11s). Use `--timeout 90` for pro tasks (they average 30s with p95 at 63s). Omit `--timeout` to use the 90s default.

If any dispatch returns **exit code 2** (`QUEUE_FULL`): do that work yourself on the main thread.

5. **Work while agents run** — do NOT idle-poll. While agents execute, proceed with:
   - Sequential items from the Work Plan that don't conflict with agent-owned files
   - Documentation updates, code review, or other non-conflicting work

> **If there's nothing to do while agents run, just implement the tasks yourself** — the overhead of dispatch + monitor + review isn't worth it when you're idle anyway.

6. **Dispatch-and-recover pattern** (monitor running agents):
```

After ~30s, check: .agent/bin/gemini-gateway --jobs
→ running_time_s < 45 (flash) / < 60 (pro): normal, keep working
→ running_time_s > 60 (flash) / > 90 (pro): likely stuck → cancel, do it myself
When my own work is done, check command_status on each agent
→ Done: review the diff
→ Still running past threshold: cancel, do it myself
Never idle-wait for agents. Always be doing useful work.

```
If a rate-limited agent retried and succeeded, `--stats` will show it. If pacing is `slow`, the gateway is recovering — expect subsequent dispatches to take slightly longer.
7. **Review** — for each completed agent, review its changes:
a. Read the diff (`git diff <file>`) for each modified file
b. Verify the changes match the phase description and acceptance criteria
c. Check code quality: correct patterns, proper docblocks, no regressions
8. **Handle review outcomes**:
- **Acceptable**: Keep the changes, proceed to verification
- **Minor issues**: Fix inline (faster than re-dispatching)
- **Wrong approach / doesn't match plan**: Revert that agent's files (`git checkout -- <files>`), re-dispatch with corrective instructions explaining what was wrong and what to do differently. Max 2 retry attempts per phase before falling back to sequential.
9. **Verify** — run the project test suite after the entire parallel batch is accepted.
10. **On success**: Mark all items in the group as `✅ Done`
11. **On failure**: Revert the parallel batch (`git checkout -- .`) and re-implement the failed items sequentially.

After all parallel groups are resolved, continue with any remaining sequential items.

**Between items**, briefly report progress to the user:

- What was just completed
- What's next
- Any blockers discovered

### 4. Handle test failures

Test failures discovered during implementation are **expected** in refactoring work. Handle them as follows:

- **Failures caused by your changes** (e.g., mock types changed, constructor signatures updated): Fix inline as part of the current phase. Do NOT park as debt.
- **Pre-existing failures** unrelated to your changes: Note them but don't fix them — they're outside scope.
- **Failures revealing design issues**: If fixing tests requires rethinking the approach, stop and discuss with the user before proceeding.

When fixing tests inline, include the test file updates as part of the phase they belong to. Don't create a separate "fix tests" phase.

### 5. Handle blockers

When an item **cannot be completed** in the current session:

- Missing external dependency (API keys, third-party setup)
- Requires architectural decision not yet made
- Out of scope for the current work
- Blocked by another team or system

**Do NOT skip silently.** Flag it to the user and confirm it should be parked as debt. Mark the phase as `🚫 Blocked` or `🗑️ Debt` in the Progress table with notes explaining why.

### 6. Session boundary (if stopping mid-work)

When a conversation is ending but work remains:

// turbo

- Ensure the Progress table is up to date (all completed items marked ✅, current item marked 🔧)
- Add a note to the current `🔧 In Progress` item describing exactly where you stopped
- The source document's status stays `In Progress`

The next session runs `/implement` on the same doc and resumes from the Progress table.

### 7. Report completion

When all items are done (or no more can be progressed), summarize:

- Items completed (count and key highlights)
- Items parked as debt (count and reasons)
- Any follow-up actions needed

Tell the user: `Implementation complete. Run /close docs/<filename>.md to finalize.`
```
