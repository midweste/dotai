---
description: Audit the full .agent/ system — rules, workflows, and knowledge — for overlap, gaps, conflicts, staleness, and agent compliance
---

# /audit-all — Audit Everything

Orchestrates the three sub-audits and produces a combined scored report.

> [!IMPORTANT]
> **Each sub-audit MUST produce its own artifact report** and present it to the user before proceeding to the next sub-audit. The combined summary references these reports — it does not replace them.

## Steps

### Run sub-audits

Run each sub-audit in order. Each produces its own artifact report that is presented for review:

1. **`/audit-policy`** — rules & policy health (structure, effectiveness, cross-cutting). Write artifact: `audit_policy.md`
2. **`/audit-workflows`** — workflow structural quality (mechanical + AI checks). Write artifact: `audit_workflows.md`
3. **`/audit-knowledge`** — KI accuracy, staleness, duplication, structural integrity. Write artifact: `audit_knowledge.md`

Present all three sub-audit artifacts to the user for review before writing the combined summary.

### Score

Combine findings from all three sub-audits and assign an overall health score:

| Score | Meaning                           |
| ----- | --------------------------------- |
| A     | Clean — no ❌, ≤2 ⚠️              |
| B     | Healthy — no ❌, 3-5 ⚠️           |
| C     | Needs attention — 1-2 ❌ or 6+ ⚠️ |
| D     | Overhaul recommended — 3+ ❌      |

### Recommendations

For every ⚠️ and ❌ across all sub-audits, propose a specific fix:

- Files to merge, split, rename, or delete
- Rules to reword, elevate, or remove
- Missing rules or workflows to create
- Sections to move from rules into workflows (or vice versa)

## Output

Write the combined summary to an artifact file (`audit_report.md`) and present for review:

```markdown
# Agent System Audit — <date>

## Summary

| Metric          | Value     |
| --------------- | --------- |
| Score           | <A/B/C/D> |
| Rule files      | <count>   |
| Workflow files  | <count>   |
| Knowledge items | <count>   |
| Total size      | <KB>      |

## Sub-Audit Results

| Audit          | Findings         | Key Issues |
| -------------- | ---------------- | ---------- |
| Rules & Policy | <✅/⚠️/❌ count> | <summary>  |
| Workflows      | <✅/⚠️/❌ count> | <summary>  |
| Knowledge      | <✅/⚠️/❌ count> | <summary>  |

## Recommendations

<prioritized list of specific actions from all sub-audits>
```
