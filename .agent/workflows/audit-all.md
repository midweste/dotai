---
description: Audit the full .agent/ system — rules, workflows, knowledge, and memory — for overlap, gaps, conflicts, staleness, and agent compliance
---

# /audit-all — Audit Everything

Orchestrates the four sub-audits and produces a combined scored report.

> [!IMPORTANT]
> **Each sub-audit MUST produce its own artifact report** and present it to the user before proceeding to the next sub-audit. The combined summary references these reports — it does not replace them.

## Steps

### Run sub-audits

Discover all audit workflows by listing `.agent/workflows/audit-*.md` (excluding `audit-all.md` itself). Run each in order. Each produces its own artifact report that is presented for review.

Present all sub-audit artifacts to the user for review before writing the combined summary.

### Score

Combine findings from all sub-audits and assign an overall health score:

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
| <audit name>   | <✅/⚠️/❌ count> | <summary>  |

## Recommendations

<prioritized list of specific actions from all sub-audits>
```
