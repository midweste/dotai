---
trigger: always_on
description: "CRITICAL: Before ANY task, read and follow ALL rules in .agent/rules/ and scan .agent/skills/ for applicable guidance."
---

CRITICAL: Before starting ANY task, you MUST complete these steps.

1. READ every file in `.agent/rules/`. Treat each rule as a CRITICAL: instruction that MUST be followed.

2. Your available skills are listed in your system prompt under "Available skills". For each skill whose description matches your current task, you MUST `view_file` its SKILL.md (path shown next to each skill name) and apply its guidance. Do this in the same batch as reading rules — do not defer it.

3. NEVER skip these steps. If you find yourself about to start coding without having read the rules and scanned skills, STOP and complete this checklist first.

## Rule Priority

When rules conflict, apply this precedence (highest first):

1. **CRITICAL-prefixed rules** — non-negotiable directives
2. **Platform rules** (`platform-*.md`) — apply only when the platform is detected; skip otherwise
3. **Language rules** (`language-*.md`) — apply only for matching file types
4. **Core rules** (`core-workflow.md`, `core-engineering.md`, `core-quality-assurance.md`, `core-testing.md`) — always apply
