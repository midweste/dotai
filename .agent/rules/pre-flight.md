---
trigger: always_on
description: "CRITICAL: Before ANY task, read and follow ALL rules in .agent/rules/ and scan .agent/skills/ for applicable guidance."
---

CRITICAL: Before starting ANY task, you MUST complete these steps.

1. READ every file in `.agent/rules/`. Treat each rule as a CRITICAL: instruction that MUST be followed.

2. SCAN every skill description in `.agent/skills/`. If a skill's domain matches the current task, `view_file` its SKILL.md and apply its guidance BEFORE writing any code.

3. NEVER skip these steps. If you find yourself about to start coding without having read the rules and scanned skills, STOP and complete this checklist first.
