---
description: "Dry-run a task to evaluate approach, skill usage, rule adherence, and parallelism — without making any changes. Supply a task description or doc path."
---

# /dry-run — Task Approach Evaluation

Simulate how you would **naturally** approach a supplied task, then audit yourself. **Do not make any file changes.**

## Input

The user supplies one of:

- A task description (e.g., "add a new filter class for Magento products")
- A doc path (e.g., `docs/some-planning-doc.md`)

If a doc path is supplied, read it first.

## Phase 1: Natural Approach (no peeking)

**Pretend this is a brand new conversation.** You have no special awareness of `.agent/`, skills, rules, or workflows. Just describe your approach:

1. What is your understanding of the task?
2. What files would you read first?
3. What order would you work in?
4. What tools or references would you reach for?
5. Would you do anything in parallel, or work sequentially?

Write this out as a stream-of-consciousness plan. **Do not reference `.agent/`, skills, rules, or workflows.** Be honest about what you would actually do.

## Phase 2: Audit Against .agent/ System

Now read the actual `.agent/` configuration and compare:

### Skills audit

Read `ls .agent/skills/` to get the active skills list. Compare each skill's description against the task from Phase 1:

| Skill      | Should Have Used? | Naturally Reached For? | Gap                            |
| ---------- | ----------------- | ---------------------- | ------------------------------ |
| skill-name | ✅/❌             | ✅/❌                  | Description of what was missed |

Count: **N skills should have been used, N were naturally reached for. Gap: N.**

### Rules audit

Read each file in `.agent/rules/`. Compare each rule's requirements against the Phase 1 plan:

| Rule      | Requirement     | Phase 1 Compliant? | What Was Missed                  |
| --------- | --------------- | ------------------ | -------------------------------- |
| rule-name | Key requirement | ✅/❌              | What you'd have done differently |

Count: **N rules apply, N were naturally followed. Gap: N.**

### Parallelism audit

Compare the Phase 1 work order against `core-parallel-evaluation.md` requirements:

- List all discrete tasks from Phase 1
- Identify which were planned sequentially but could have been parallel
- Show the optimal batch plan vs. what Phase 1 described

## Phase 3: Report

Report everything in chat. Format:

```markdown
## Dry-Run: [task name]

### Phase 1: What I Would Actually Do

[Stream-of-consciousness approach from Phase 1]

### Phase 2: What I Missed

#### Skills Gap: N missed / N applicable

[Table]

#### Rules Gap: N missed / N applicable

[Table]

#### Parallelism Gap

[Phase 1 plan vs. optimal plan]

### Verdict

[Did the .agent system add value? Is the gap narrowing compared to previous audits?]
```
