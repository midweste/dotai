---
description: Generate a project-specific skills bundle by analyzing the codebase
---

# Generate Skills Bundle

Clone the full skills repo to a temp directory, analyze the codebase, pick up to 20 relevant skills, copy them to `.agent/skills/`, and clean up.

// turbo-all

## Steps

1. **Clone skills repo to temp directory**:

```bash
SKILLS_TMP=$(mktemp -d)
echo "Cloning skills to $SKILLS_TMP..."
git clone --depth 1 https://github.com/sickn33/antigravity-awesome-skills.git "$SKILLS_TMP" 2>&1 | tail -1
echo "Done. Skills at: $SKILLS_TMP/skills/"
ls "$SKILLS_TMP/skills/" | wc -l
```

If the clone fails, stop and tell the user.

2. **Scan skill descriptions** — build a catalog from each SKILL.md:

```bash
for d in "$SKILLS_TMP"/skills/*/; do
  name=$(basename "$d")
  desc=""
  if [ -f "$d/SKILL.md" ]; then
    desc=$(head -5 "$d/SKILL.md" | grep -i 'description:' | head -1 | sed 's/.*description: *//')
  fi
  printf '%-45s %s\n' "$name" "$desc"
done
```

> The output will be large (700+ skills). Skim it to understand what's available — you don't need to read every line.

3. **Analyze the codebase** to identify:
   - Primary languages (check file extensions, `composer.json`, `package.json`, etc.)
   - Frameworks (WordPress, Laravel, React, Django, etc.)
   - Key patterns (testing setup, API endpoints, security, CI/CD, etc.)
   - Project type (plugin, library, application, service, etc.)

4. **Select up to 20 skills** that match the project. Prioritize:
   - Language-specific skills matching the project's primary languages
   - Framework skills matching detected frameworks
   - Architecture/pattern skills matching the codebase structure
   - Testing/security/deployment skills if those concerns exist in the project

5. **Clear existing skills and copy selected ones from the temp clone**:

```bash
# Remove existing curated skills (preserve .gitignore and README if present)
find .agent/skills/ -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} +
mkdir -p .agent/skills

# Copy each selected skill from temp clone
for skill in <space-separated list of selected skill names>; do
  if [ -d "$SKILLS_TMP/skills/$skill" ]; then
    cp -r "$SKILLS_TMP/skills/$skill" ".agent/skills/$skill"
    echo "✅ $skill"
  else
    echo "⚠️ $skill not found in repo"
  fi
done
```

6. **Clean up temp directory**:

```bash
rm -rf "$SKILLS_TMP"
echo "Temp skills repo removed."
```

7. **Verify** the bundle:

```bash
echo "Skills installed:"
ls -1 .agent/skills/ | grep -v '^\.' | grep -v '^README' | wc -l
ls -1 .agent/skills/ | grep -v '^\.' | grep -v '^README'
```

Confirm count is ≤ 20 and each directory contains a SKILL.md.

## Selection Guidelines

**Always include if detected:**

- Project's primary language skill (e.g., `php-pro`, `python-pro`, `golang-pro`)
- Project's framework skill (e.g., `django-pro`, `fastapi-pro`, `nestjs-expert`)

**Include if relevant:**

- `clean-code` — for any codebase
- `backend-architect` or `frontend-developer` — based on project type
- `docker-expert` — if Dockerfile/docker-compose exists
- `testing-patterns` or language-specific test skills — if test suite exists
- `security-auditor` or `backend-security-coder` — if auth/payments exist
- `database-design` or `sql-optimization-patterns` — if DB access exists
- `api-design-principles` — if API endpoints exist

**Do NOT include:**

- Skills for languages/frameworks not used in the project
- Penetration testing skills (unless it's a security project)
- Platform-specific skills that don't match (e.g., no Shopify skills for a Django project)

## Output

Report to the user:

- How many skills were selected and why
- The full list of installed skills
- Any skills that were considered but excluded (and why)
