---
description: "SDLC Step 3/3 — Close a completed planning document by appending a walkthrough, creating a debt doc if needed, and moving to finished/"
---

# /close — Close a Planning Document

Finalize a completed planning document: append walkthrough, create debt doc for parked items, and move to `finished/` with a finish-time filename.

**Input**: Planning doc path (status must be `In Progress`)
**Output**: Walkthrough appended, debt doc if needed, source doc moved to `finished/`

## SDLC Pipeline

**Full path**: `/plan` → `/implement` → **`/close`**
**Lightweight**: `/capture` (self-contained — for ad-hoc fixes)

**You are here**: `/close` — finalizing and filing the completed work

## Steps

### 1. Load and verify

Read the target document. Check the frontmatter `> Status:` line:

- **`In Progress`**: Proceed with closing
- **`Done` but not in `finished/`**: Proceed — just needs filing (skip to step 4)
- **`Draft` or `Planned`**: Tell user: "This doc needs planning. Run `/plan`."
- **`Approved`**: Tell user: "This doc hasn't been implemented yet. Run `/implement`."
- **Anything else**: Tell user which step to run based on the status.

#### Verify Progress table

If the document has a `## Progress` table (created by `/implement`), check that **every item** has a terminal status (`✅ Done`, `🚫 Blocked`, or `🗑️ Debt`).

If any items are `⬜ Ready` or `🔧 In Progress`, list them and ask the user to resolve each one:

> These items aren't marked complete:
>
> - Phase 3: `🔧 In Progress`
> - Phase 4: `⬜ Ready`
>
> For each, choose: **✅ Done** | **🗑️ Debt** | **🚫 Blocked**

Update the Progress table with their answers, then proceed. Items marked as debt/blocked will flow into the debt doc (step 2).

If no Progress table exists (older docs), infer completion from the document content and confirm with the user.

### 2. Run tests (mandatory gate)

Before closing, verify all tests pass. This is a **hard gate** — do not proceed to walkthrough or filing until tests are green.

#### Discover how to run tests

// turbo

Check for test infrastructure in this order:

1. **Makefile**: Look for `test`, `artisan-test`, or similar targets (`grep -i test Makefile`)
2. **docker-compose.yml / lando.yml**: If tests fail locally due to PHP version or missing deps, look for containerized commands:
   - **Lando**: `lando php artisan test`, `lando phpunit`
   - **Docker Compose**: `docker compose exec app php artisan test`
   - **Make targets**: `make artisan-test`, `make test`
3. **package.json**: `npm test`, `npx vitest`, etc.
4. **Direct**: `php artisan test`, `phpunit`, `pytest`, etc.

> [!IMPORTANT]
> If you see a PHP version mismatch error (e.g., "requires >= 8.2.0, running 8.1"), **do not skip tests**. Find the containerized command (Makefile, Lando, Docker) that runs tests in the correct environment.

#### Run the tests

// turbo

Run the full test suite (or the relevant subset if the project is very large). Capture the output.

#### Handle failures

- **Failures caused by your changes**: Fix them inline. This is expected — refactors often break mocks, assertions, or constructor signatures in tests you didn't directly modify. After fixing, re-run tests.
- **Pre-existing failures** unrelated to changes: Note them in the walkthrough but don't block closing.
- **Cannot determine**: If unsure whether a failure is yours, check `git diff` to see if the failing test's dependencies were modified.

**Repeat until all tests pass** (or only pre-existing failures remain). Then proceed.

### 3. Create the debt document (if needed)

When any items were parked:

// turbo

Create a sister document with the same slug but `-debt` suffix:

```
Original:  docs/2026-02-12T0744--shopify-auditor.md
Debt doc:  docs/2026-02-12T0744--shopify-auditor-debt.md
```

The datetime prefix matches the **original** document (not the current time).

Structure the debt doc as a **planning doc with status `Draft`** — it flows directly into `/plan`:

```markdown
# <Original Title> — Remaining Debt

> Created: YYYY-MM-DD HH:MM (local)
> Status: Draft
> Parent: <link to original document in finished/>

## Requirement

The following items from the parent plan were parked during implementation.

### <Item Name>

- **What it is**: <what was originally planned>
- **Why parked**: <reason it couldn't be completed>
- **What's needed**: <what must happen before this can proceed>
- **Priority**: High | Medium | Low
```

Debt docs stay in the **active** `docs/` directory — they represent open work ready for `/plan`.

Tell the user: `Debt doc created. Run /plan docs/<debt-filename>.md when ready.`

### 4. Append walkthrough to the source document

// turbo

Append a `## Walkthrough` section to the **original planning document**. This is the permanent record of what happened.

```markdown
## Walkthrough

> Executed: YYYY-MM-DD HH:MM (local)

### Plan vs Reality

| Phase | Planned                  | Outcome                | Notes                                |
| ----- | ------------------------ | ---------------------- | ------------------------------------ |
| 1a    | Validators + AuditEngine | ✅ Done (pre-existing) | Already implemented before this plan |
| 2a    | Migration + model        | ✅ Done                | Created product_audits table         |
| 2b    | Queue job                | ❌ Removed             | Decision: run inline, no job needed  |
| 3a    | Admin panel extension    | 🚫 Debt                | Parked: requires separate session    |

### Files Created

| File                         | Purpose     |
| ---------------------------- | ----------- |
| [filename.php](file:///path) | Description |

### Files Modified

| File                         | Change           |
| ---------------------------- | ---------------- |
| [filename.php](file:///path) | What was changed |

### Decisions Made

1. **<Topic>**: <answer> — Rationale: <why>

### Open Debt

List of parked items with link to debt doc (if created).
```

### 5. Finalize the original document

// turbo

Update the original document frontmatter:

- Set status to `Done` (whether or not debt exists — the plan's work is finished)
- Add a `> Finished: YYYY-MM-DD HH:MM (local)` line (current datetime)
- If a debt doc was created, add a `> Debt: <link to debt doc>` line
- Update the Changelog table

### 6. Move to finished

// turbo

Rename the file's datetime prefix to the **current finish time**, then move to `finished/`:

```bash
# Example: created at 07:44, finished at 13:48
mv docs/2026-02-12T0744--shopify-auditor.md docs/finished/2026-02-12T1348--shopify-auditor.md
```

The filename reflects **when the work was completed**, not when the doc was created. This keeps `finished/` in chronological completion order.

For module-specific docs, move to the module's `docs/finished/` directory.

### 7. Report

Summarize to the user:

- Items completed (count and key highlights)
- Items parked as debt (count and reasons)
- Decisions recorded
- File paths created/moved
- Test results (pass count, assertion count)
- Any follow-up actions needed

#### Git commit message

Provide a **copy-paste ready** commit message following conventional commits format. Use the doc slug as the scope:

```
feat(wp-plugin-api): fix auth bypass, refactor findProductByUrl

- Remove `return true;` permission bypass on 5 REST endpoints
- Refactor findProductByUrl → findProductIdByUrl (uses rr/products/meta)
- Update 7 test methods for new mock expectations

Closes: docs/2026-02-13T2119--wp-plugin-api-reconciliation.md
```

Rules:

- **Type**: `feat` for features, `fix` for bugs, `refactor` for restructuring, `security` for security fixes
- **Scope**: Derive from the doc slug (e.g., `wp-plugin-api` from `--wp-plugin-api-reconciliation.md`)
- **Body**: One line per logical change, prefixed with `-`
- **Footer**: Reference the planning doc
