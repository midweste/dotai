---
description: Audit how effectively .agent rules, skills, and tools are being used across recent conversations. Run periodically to identify gaps and improvements.
---

# /audit-agent — Agent Effectiveness Audit

Evaluate whether the `.agent/` system (rules, skills, parallelism, workflows) is working in practice. Produces a report with findings and recommendations.

**Run periodically** (e.g., weekly or after a batch of conversations) to catch drift.

## Steps

### 1. Inventory the current .agent setup

// turbo

List what's currently configured:

```bash
echo "=== Rules ===" && ls -1 .agent/rules/
echo "=== Skills (active) ===" && ls -1 .agent/skills/
echo "=== Skills (available) ===" && ls -1 .agent/skills-available/ | wc -l
echo "=== Workflows ===" && ls -1 .agent/workflows/
```

Record the counts for the report.

### 2. Scan recent conversations for skill usage

// turbo

Search conversation artifacts for evidence of SKILL.md files being read:

```bash
grep -rl "SKILL.md" ~/.gemini/antigravity/brain/ --include="*.txt" --include="*.md" 2>/dev/null
```

For each hit, check whether the skill was **read for guidance** (good) or just **mentioned** (doesn't count). Record:

- Total conversations scanned
- Conversations where a skill was actually read and applied
- Which skills were used
- Which active skills have NEVER been used

### 3. Check parallelism rule adherence

Search recent conversation artifacts for parallelism-related keywords:

```bash
grep -rl "parallelism\|parallel\|dispatch\|gateway" ~/.gemini/antigravity/brain/ --include="*.txt" --include="*.md" 2>/dev/null
```

For each recent conversation, check:

- [ ] Was parallelism evaluated before starting work?
- [ ] Was the evaluation reported to the user?
- [ ] Were agents dispatched when work was parallelizable?
- [ ] If skipped, was a valid reason given?

### 4. Check rule adherence

For each file in `.agent/rules/`, check whether the rule's requirements were followed in recent conversations:

- Read each rule file to understand its requirements
- Search conversation artifacts for evidence of compliance or violation
- Flag rules that appear to be consistently ignored

### 5. Evaluate skill relevance

Review the active skills list against recent work:

- Which skills match the actual tasks performed?
- Are there skills that should be **added** (task needed guidance that wasn't available)?
- Are there skills that should be **removed** (present but never relevant)?
- Check `.agent/skills-available/` for skills that would have been useful but aren't linked

### 6. Generate the report

Create the report at `docs/agent-audit-YYYY-MM-DD.md`:

```markdown
# Agent Effectiveness Audit — YYYY-MM-DD

## Summary

| Metric                | Value          |
| --------------------- | -------------- |
| Conversations scanned | N              |
| Skills used           | N / N active   |
| Parallelism evaluated | N / N eligible |
| Rules followed        | N / N rules    |

## Skill Usage

### Used

- skill-name — used in conversation [ID], for [purpose]

### Never Used (candidates for removal)

- skill-name — active but unused in N conversations

### Missing (candidates for addition)

- skill-name — available in skills-available, would have helped with [task]

## Rule Adherence

### Followed

- rule-name — consistently followed

### Violated

- rule-name — violated in conversation [ID]: [description]

### Not Testable

- rule-name — cannot determine from artifacts alone

## Parallelism

### Dispatched

- Conversation [ID]: dispatched N agents for [task]

### Missed Opportunities

- Conversation [ID]: [task] had N independent sub-tasks but ran sequentially

## Recommendations

1. **[Action]** — [rationale]
2. **[Action]** — [rationale]
```

### 7. Present findings

Report the summary to the user with the full audit doc path. Highlight:

- Top 3 most impactful recommendations
- Any rules that need revision (like the <30s exception we found)
- Skill additions/removals to action immediately
