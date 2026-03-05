---
description: "Audit all workflows against core-workflow-authoring rules for structural quality"
---

# /audit-workflows — Audit Workflow Quality

Scan all `.agent/workflows/` files for structural issues, DRY violations, SDLC pipeline consistency, and broken conventions.

**Input**: None — reads all workflow files automatically
**Output**: Audit report with findings and fixes applied

// turbo-all

## Steps

### Load rules and workflows

Read `.agent/rules/core-workflow-authoring.md` and every `.md` file in `.agent/workflows/`.

### Extract structural data

Run this for machine-readable data powering the mechanical checks:

```bash
cd .agent/workflows && python3 -c "
import os, re, json
from collections import defaultdict

data = {}
for fname in sorted(os.listdir('.')):
    if not fname.endswith('.md'): continue
    with open(fname) as f:
        content = f.read()
    fm = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    desc = ''
    if fm:
        for line in fm.group(1).splitlines():
            if 'description:' in line.lower():
                desc = line.split(':', 1)[1].strip().strip('\"').strip(\"'\")[:100]
    headings = [m.group(1).strip() for m in re.finditer(r'^#{3,}\s+(.+)$', content, re.MULTILINE)]
    has_turbo_all = '// turbo-all' in content
    turbo_lines = [i for i, l in enumerate(content.splitlines(), 1) if l.strip() == '// turbo']
    named_refs = re.findall(r'\x60/(\w[\w-]*)\x60(?:\'s|\u2019s)?\s+_([^_]+)_', content)
    stripped = re.sub(r'^---\s*\n.*?\n---', '', content, flags=re.DOTALL)
    non_code = re.sub(r'\x60\x60\x60.*?\x60\x60\x60', '', stripped, flags=re.DOTALL)
    non_code = re.sub(r'\x60[^\x60]+\x60', '', non_code)
    step_nums = re.findall(r'\bsteps?\s+(\d[\d,-]*)\b', non_code, re.IGNORECASE)
    numbered_headings = [h for h in headings if re.match(r'^\d+\.', h)]
    platform_hits = []
    for pat in [r'\bmake\s+(?:phpstan|test|lint|build|deploy|install|artisan[\w-]*)\b',
                r'\bnpm\s+(?:test|run)\b', r'\bcomposer\s+(?:install|require|update)\b',
                r'\bpytest\b', r'\bbundle\s+exec\b',
                r'\bPHPStan\b', r'\bESLint\b', r'\bRuboCop\b', r'\bPylint\b',
                r'\bLaravel\b', r'\bRails\b', r'\bDjango\b', r'\bReact\b']:
        for m in re.finditer(pat, non_code):
            platform_hits.append(m.group())
    step_classes = []
    for h in headings:
        hl = h.lower()
        safe = any(w in hl for w in ['read','load','scan','extract','verify','list','run test','clone','clean','create','ensure','mark','capture','inventory','write','evaluate','consolidate','research','act','handle'])
        unsafe = any(w in hl for w in ['present','approve','review','ask','iterate','report'])
        step_classes.append({'name': h, 'safe': safe, 'unsafe': unsafe})
    data[fname] = {
        'desc': desc, 'headings': headings, 'has_turbo_all': has_turbo_all,
        'turbo_lines': turbo_lines, 'named_refs': [{'wf': r[0], 'step': r[1]} for r in named_refs],
        'step_nums': step_nums, 'numbered_headings': numbered_headings,
        'platform_hits': platform_hits, 'step_classes': step_classes
    }
print(json.dumps(data, indent=2))
"
```

### Run checks

Checks marked **(M)** are mechanical — run against extraction data. Checks marked **(AI)** require reading actual content.

---

#### Check 1 (M): Heading uniqueness

- **Within file**: flag duplicate headings (case-insensitive) in any single workflow
- **Across files**: collect headings that are cross-referenced by other workflows. Flag if two different workflows define the same heading. Exempt generic headings never used as cross-ref targets (e.g., "Steps", "Summary")

#### Check 2 (M): Step references use names, not numbers

From `step_nums` field. Any non-empty value is a violation. Exclude: YAML description fields with `Step N/3`, this audit workflow's own examples.

#### Check 3 (M): Cross-reference resolution

For each `named_refs` entry, verify the target heading exists in the target workflow. Flag dangling refs and missing workflows.

#### Check 4 (M): Frontmatter and labels

- Every workflow must have a non-empty YAML `description`
- SDLC workflows: description must start with `SDLC Step N/3 —`, `SDLC Shortcut —`, or `SDLC Meta —`. Verify numbering is sequential.
- Status reads must target `> Status:` frontmatter, not body text
- Filenames: `YYYY-MM-DDTHHMM` format. Frontmatter dates: `YYYY-MM-DD HH:MM (local)`. Flag deviations.

#### Check 5 (M): Platform-agnostic language

From `platform_hits` field. Flag non-empty values. Exclude meta-examples that describe what violations look like. Use generic: "test suite", "static analysis".

#### Check 6 (M): Turbo annotations

From `has_turbo_all`, `turbo_lines`, `step_classes`:

- **Dangerous turbo** (High): `// turbo` on steps classified as `unsafe`
- **Redundant turbo** (Low): Individual `// turbo` when `// turbo-all` is set
- **Missing turbo-all** (Medium): All steps safe but no `// turbo-all`

#### Check 7 (M): Step numbering convention

From `numbered_headings`. Any non-empty value is a violation — use descriptive names, not `### 3. Run tests`.

#### Check 8 (M): Skills loading

- Every workflow needing skill evaluation should reference `/skills`'s _Evaluate skills_ with a one-liner. Flag inline copies.
- _Evaluate skills_ must appear **before** any substantive work step (research, scanning, implementing). Flag violations as Medium.

#### Check 9 (AI): Canonical ownership and DRY

Read workflows with `named_refs`. Verify referencing workflows don't also contain inline copies of the same logic. Canonical owners:

| Concern                                                                 | Owner         |
| ----------------------------------------------------------------------- | ------------- |
| Evaluate skills                                                         | `/skills`     |
| Append walkthrough, Finalize, Move to finished, Create debt doc, Report | `/close`      |
| Clone skills repo, Extract catalog                                      | `/add-skills` |
| Smell checklist, Logging format                                         | `/sniff`      |

Flag parallel definitions of the same concern without a reference relationship.

#### Check 10 (AI): Document template quality

Workflows creating documents must use consistent templates:

- **Debt docs**: must reference `/close`'s _Create debt doc_ step. Must use `> Status: Debt`. Must include `## Requirement` with actionable items.
- **Source docs**: must include `> Status:` and `> Created:` frontmatter.
- **Status values**: every `> Status:` value written must be accepted by at least one downstream workflow's routing table. Flag orphaned statuses.

#### Check 11 (AI): SDLC pipeline integrity

**Status lifecycle**: `Draft → Planned → Approved → In Progress → Done → finished/`

| Workflow     | Accepts                     | Outputs       | Next accepts    |
| ------------ | --------------------------- | ------------- | --------------- |
| `/plan`      | Draft, Debt, Planned, none  | `Approved`    | `/implement` ✅ |
| `/implement` | Approved, In Progress       | `In Progress` | `/close` ✅     |
| `/close`     | In Progress, Done (unfiled) | `Done`        | (terminal)      |
| `/capture`   | (self-contained)            | `Done`        | (terminal)      |
| `/hotfix`    | (self-contained)            | `Done`        | (terminal)      |

Verify: outputs match next workflow's accepts, guard redirects name exact commands, every SDLC workflow has `## SDLC Pipeline` block with "You are here" marker.

#### Check 12 (AI): Link rebasing and test policy

- Every workflow moving to `finished/` must rebase relative links. Verify `/capture` and `/hotfix` reference `/close`'s step.
- All test/analysis gates must require **all failures fixed** — including pre-existing. Flag "note but don't fix" language.

#### Check 13 (AI): Document pluggability

For each doc type (source docs, debt docs), trace creation → consumption path. Verify consumer can pick up the doc without user formatting. Flag format mismatches.

---

### Report findings

| #   | Check | File | Issue | Severity |
| --- | ----- | ---- | ----- | -------- |

Severity: **High** = wrong agent action. **Medium** = DRY violation, inconsistency. **Low** = style.

### Fix issues

Fix all High and Medium. Present Low for user review. Re-run extraction and all checks to confirm no regressions.

### Dry-run walkthrough

Simulate end-to-end SDLC, verifying each handoff:

1. User describes feature → `/plan` _Capture the intent_ → no doc, description input ✅
2. `/plan` _Ensure a source doc exists (stub only)_ → stub with `Draft`. Template matches `/implement` expectations?
3. `/plan` _Create the implementation plan artifact_ → has all sections `/implement` references?
4. `/plan` _Present for review_ / _Iterate until approved_ → user iterates
5. `/plan` _Write the source document_ → full doc with Proposal, Reconciliation, Decisions
6. `/plan` _Mark as approved_ → `Approved`. `/implement` accepts? ✅
7. `/implement` _Load the document and plan_ → reads doc + artifact. Missing artifact handling?
8. `/implement` _Mark the source document and initialize progress tracking_ → Progress table from Proposal phases
9. `/implement` _Report completion_ → `/close` accepts `In Progress`? ✅
10. `/close` _Load and verify_ → Progress table all terminal?
11. `/close` _Append walkthrough to the source document_ → references source doc data?
12. `/close` _Move to finished_ → rebase links ✅

**Edge cases**: mid-plan interrupt (stub + artifact, `Draft`), resume `/implement` (`In Progress`, scans for `⬜ Ready`), debt flow (`Debt` → `/plan` accepts, created via canonical step, `## Requirement` usable?), `/capture` bypass (produces `finished/`-ready doc?).

Flag any broken handoff.

### Self-audit

Verify this workflow is current: dry-run uses named refs, edge cases are realistic, checks cover all active conventions, workflow list matches actual files.

### Summary

Report: total checks, workflows scanned, issues by severity, issues fixed, remaining items.
