---
description: Audit .agent/rules/ for overlap, gaps, conflicts, staleness, and agent compliance
---

# Audit Rules

Systematically evaluate every file in `.agent/rules/` against the criteria below. Produce a scored report with concrete recommendations.

## Steps

1. **Inventory** — list every file in `.agent/rules/` with its size and last-modified date:

```bash
ls -lh .agent/rules/
```

2. **Read every rule file** — load all files in `.agent/rules/` so you have full context before evaluating.

3. **Evaluate each category** below. For each question, answer with ✅ (pass), ⚠️ (concern), or ❌ (fail) plus a brief explanation.

---

### Structure & Organization

| #   | Question                                                                                                    |
| --- | ----------------------------------------------------------------------------------------------------------- |
| 1   | **Overlap** — Do any two files cover the same topic? List specific duplicated guidance.                     |
| 2   | **Granularity** — Are any files too large (>5KB) to be a single rule? Should they be split?                 |
| 3   | **Naming** — Is the `language-*` vs `platform-*` convention clear? Would an agent know where to look?       |
| 4   | **Missing coverage** — Are there languages, platforms, or concerns used in projects that have no rule file? |

### Effectiveness

| #   | Question                                                                                         |
| --- | ------------------------------------------------------------------------------------------------ |
| 5   | **Actionability** — Is every rule concrete enough to act on? Flag any that are too vague.        |
| 6   | **Testability** — For each rule, could an agent verify it followed it? Flag unenforceable rules. |
| 7   | **Conflicts** — Do any rules contradict each other across files? Quote the conflicting lines.    |
| 8   | **Priority** — When rules conflict, is it clear which wins? Is priority documented?              |

### Scope & Portability

| #   | Question                                                                                                                            |
| --- | ----------------------------------------------------------------------------------------------------------------------------------- |
| 9   | **Project-specific leakage** — Do any rules reference specific repos, file paths, or tools that won't exist in every project?       |
| 10  | **Conditional activation** — Should platform rules only apply when that platform is detected? How would an agent know to skip them? |
| 11  | **Distribution fitness** — Are all rules appropriate for all projects, or should some be opt-in?                                    |

### Maintenance

| #   | Question                                                                                                                                                |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 12  | **Staleness** — Are any rules likely outdated based on their content (deprecated APIs, old patterns)?                                                   |
| 13  | **Token budget** — Total size of all rule files in KB/tokens. Is this reasonable for agent context windows? Could rules be more concise?                |
| 14  | **Duplication with workflows** — Do any rules duplicate what a workflow already orchestrates? Should the rule be the _what_ and the workflow the _how_? |

### Agent Behavior

| #   | Question                                                                                                          |
| --- | ----------------------------------------------------------------------------------------------------------------- |
| 15  | **Pre-flight compliance** — Does the pre-flight rule clearly instruct agents to read all files? Any gaps?         |
| 16  | **Signal-to-noise** — Are there rules agents would likely ignore due to length, vagueness, or low relevance?      |
| 17  | **Prompt-alias coverage** — Do all aliases in `prompt-aliases.md` map to a concrete section in another rule file? |

---

4. **Score** — assign an overall health score:

| Score | Meaning                           |
| ----- | --------------------------------- |
| A     | Clean — no ❌, ≤2 ⚠️              |
| B     | Healthy — no ❌, 3-5 ⚠️           |
| C     | Needs attention — 1-2 ❌ or 6+ ⚠️ |
| D     | Overhaul recommended — 3+ ❌      |

5. **Recommendations** — for every ⚠️ and ❌, propose a specific fix:
   - Files to merge, split, rename, or delete
   - Rules to reword, elevate, or remove
   - Missing rules to create
   - Sections to move from rules into workflows (or vice versa)

## Output

```
## Rules Audit — <date>

### Summary
- Files: <count>
- Total size: <KB>
- Score: <A/B/C/D>

### Findings
<table of all 17 questions with ✅/⚠️/❌ and explanation>

### Recommendations
<numbered list of specific actions>
```
