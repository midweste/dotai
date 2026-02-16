---
description: Audit .agent/rules/ and .agent/workflows/ for overlap, gaps, conflicts, staleness, and agent compliance
---

# Audit Agent System

Systematically evaluate every file in `.agent/rules/` and `.agent/workflows/` against the criteria below. Produce a scored report with concrete recommendations.

## Steps

1. **Inventory** — list every file in both directories with size and last-modified date:

```bash
ls -lh .agent/rules/ .agent/workflows/
```

2. **Read every file** — load all rule and workflow files so you have full context before evaluating.

3. **Evaluate each category** below. For each question, answer with ✅ (pass), ⚠️ (concern), or ❌ (fail) plus a brief explanation.

---

### Rules: Structure & Organization

| #   | Question                                                                                                                                           |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Overlap** — Do any two rule files cover the same topic? List specific duplicated guidance.                                                       |
| 2   | **Granularity** — Are any rule files too large (>5KB) to be a single rule? Should they be split?                                                   |
| 3   | **Naming** — Is the `core-*` / `language-*` / `platform-*` convention clear? Would an agent know where to look?                                    |
| 4   | **Missing coverage** — Are there languages, platforms, or concerns used in projects that have no rule file?                                        |
| 5   | **Misplaced rules** — Are there rules in one file that belong in a different file? Flag any rules whose topic doesn't match the file they live in. |
| 6   | **Condensation** — Could any rule files be merged without losing clarity? Flag files too thin to justify standalone existence.                     |

### Rules: Effectiveness

| #   | Question                                                                                         |
| --- | ------------------------------------------------------------------------------------------------ |
| 7   | **Actionability** — Is every rule concrete enough to act on? Flag any that are too vague.        |
| 8   | **Testability** — For each rule, could an agent verify it followed it? Flag unenforceable rules. |
| 9   | **Conflicts** — Do any rules contradict each other across files? Quote the conflicting lines.    |
| 10  | **Priority** — When rules conflict, is it clear which wins? Is priority documented?              |

### Workflows: Structure & Organization

| #   | Question                                                                                                   |
| --- | ---------------------------------------------------------------------------------------------------------- |
| 11  | **Overlap** — Do any two workflows cover the same task? List specific duplicated steps.                    |
| 12  | **Naming** — Are workflow filenames descriptive and consistent? Would a user know which to invoke?         |
| 13  | **Missing coverage** — Are there common agent tasks (debugging, refactoring, deployment) with no workflow? |
| 14  | **Descriptions** — Does every workflow have a YAML `description` that clearly explains when to use it?     |

### Workflows: Effectiveness

| #   | Question                                                                                                                             |
| --- | ------------------------------------------------------------------------------------------------------------------------------------ |
| 15  | **Frontmatter** — Does every workflow have valid YAML frontmatter with a `description` field? Flag missing or malformed frontmatter. |
| 16  | **Actionability** — Is every workflow step concrete enough to execute? Flag vague steps.                                             |
| 17  | **Turbo annotations** — Are `// turbo` annotations applied correctly? Read-only steps should have it; mutating steps should not.     |
| 18  | **Self-containment** — Can each workflow be executed with only its own instructions, or does it depend on undocumented context?      |

### Cross-Cutting

| #   | Question                                                                                                                                                                                                                                                                                                                                                           |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 19  | **Rule/workflow boundary** — Do any rules duplicate what a workflow orchestrates? Rules should define the _what_; workflows the _how_.                                                                                                                                                                                                                             |
| 20  | **Scope & portability** — Do any rules or workflows reference specific repos, file paths, or tools that won't exist in every project?                                                                                                                                                                                                                              |
| 21  | **Conditional activation** — Do platform/language rules document when to skip them? Are workflows scoped to the right contexts?                                                                                                                                                                                                                                    |
| 22  | **Orphan references** — Do any rules or workflows reference files, workflows, or rules that don't exist? Cross-check all internal references.                                                                                                                                                                                                                      |
| 23  | **Absolute paths** — Do any rules or workflows use `file://` URIs or absolute paths? All paths must be relative for portability.                                                                                                                                                                                                                                   |
| 24  | **Staleness** — Are any rules or workflows outdated (deprecated APIs, old patterns, stale cross-references)?                                                                                                                                                                                                                                                       |
| 25  | **Token budget** — Total size of all rule + workflow files in KB/tokens. Reasonable for agent context windows?                                                                                                                                                                                                                                                     |
| 26  | **Pre-flight compliance** — Does the pre-flight rule clearly instruct agents to read all rule files? Any gaps?                                                                                                                                                                                                                                                     |
| 27  | **Signal-to-noise** — Are there rules or workflows agents would likely ignore due to length, vagueness, or low relevance?                                                                                                                                                                                                                                          |
| 28  | **Sweep coverage** — Do all sweeps in `core-quality-assurance.md` map to a concrete declarative section?                                                                                                                                                                                                                                                           |
| 29  | **Plugin sync** — Is `.agent/index.md` content synced to all AI plugin configs? Diff each target against `index.md` and flag drift. Targets: `.gemini/styleguide.md`, `.github/copilot-instructions.md`, `.windsurf/rules/rules.md`, `.continue/rules/rules.md`, `.cursor/rules/policy.mdc` (has frontmatter), `.codex/config.toml` (TOML format), `.cursorrules`. |

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
   - Missing rules or workflows to create
   - Sections to move from rules into workflows (or vice versa)

## Output

```
## Agent System Audit — <date>

### Summary
- Rule files: <count>
- Workflow files: <count>
- Total size: <KB>
- Score: <A/B/C/D>

### Findings
<table of all 29 questions with ✅/⚠️/❌ and explanation>

### Recommendations
<numbered list of specific actions>
```
