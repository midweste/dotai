---
description: Generate a project-specific skills bundle by analyzing the codebase
---

# Generate Skills Bundle

Clone the full skills repo, analyze the codebase, use AI to match the best skills, install them to `.agent/skills/`, and clean up.

// turbo-all

## Steps

1. **Clone skills repo and save the path**:

```bash
SKILLS_TMP=$(mktemp -d)
echo "$SKILLS_TMP" > /tmp/.skills_tmp_path
echo "Cloning skills to $SKILLS_TMP..."
git clone --depth 1 https://github.com/sickn33/antigravity-awesome-skills.git "$SKILLS_TMP" 2>&1
if [ $? -ne 0 ]; then
  echo "ERROR: Clone failed"
  exit 1
fi
echo "Done. Skills available:"
ls "$SKILLS_TMP/skills/" | wc -l
```

If the clone fails, stop and tell the user.

2. **Analyze the codebase** — understand what this project is:

```bash
echo "=== Package Managers ==="
for f in composer.json package.json requirements.txt Gemfile go.mod Cargo.toml pyproject.toml; do
  found=$(find . -maxdepth 3 -name "$f" -not -path "*/vendor/*" -not -path "*/node_modules/*" 2>/dev/null | head -3)
  [ -n "$found" ] && echo "$f: $found"
done

echo "=== Top 15 File Extensions ==="
find . -type f -not -path "*/vendor/*" -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/.agent/*" 2>/dev/null \
  | grep -oP '\.[^./]+$' | sort | uniq -c | sort -rn | head -15

echo "=== Framework Detection ==="
for f in $(find . -maxdepth 3 -name "composer.json" -not -path "*/vendor/*" 2>/dev/null); do
  echo "--- $f ---"
  cat "$f" | python3 -c "import json,sys; d=json.load(sys.stdin); [print(k) for k in list(d.get('require',{}).keys())[:10]]" 2>/dev/null
done
for f in $(find . -maxdepth 3 -name "package.json" -not -path "*/node_modules/*" 2>/dev/null | head -2); do
  echo "--- $f ---"
  cat "$f" | python3 -c "import json,sys; d=json.load(sys.stdin); [print(k) for k in list(d.get('dependencies',{}).keys())[:10]]" 2>/dev/null
done

echo "=== Infrastructure ==="
ls -1 Dockerfile docker/Dockerfile docker-compose.yml docker-compose*.yml Makefile .github/workflows/*.yml 2>/dev/null

echo "=== Project Structure ==="
find . -maxdepth 2 -type d -not -path "*/vendor/*" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | sort | head -30
```

After reading this output, write a 3-5 line **project profile** for use in step 4.

3. **Extract skill catalog as JSON** — use Python (more reliable than bash for 800+ entries):

```bash
SKILLS_TMP=$(cat /tmp/.skills_tmp_path)
python3 -c "
import os, json
skills = {}
base = '$SKILLS_TMP/skills'
for name in sorted(os.listdir(base)):
    skill_md = os.path.join(base, name, 'SKILL.md')
    if os.path.isfile(skill_md):
        desc = ''
        with open(skill_md) as f:
            for line in f:
                if line.strip().lower().startswith('description:'):
                    desc = line.split(':', 1)[1].strip().strip('\"').strip(\"'\")[:200]
                    break
        skills[name] = desc
    elif os.path.isdir(os.path.join(base, name)):
        skills[name] = ''
print(json.dumps(skills, indent=None, separators=(',', ':')))
" > /tmp/.skills_catalog.json
echo "Catalog size: $(wc -c < /tmp/.skills_catalog.json) bytes, $(python3 -c "import json; print(len(json.load(open('/tmp/.skills_catalog.json'))))" ) skills"
```

4. **Select up to 20 skills** using your project understanding from step 2 and the catalog from step 3.

Read the catalog output. Think about what this project **actually does** and what problems its developers face — then pick skills that address those real needs.

> **Do NOT keyword-match.** The skill name `data-engineer` doesn't match because the project has "data" in it — it matches because the project is an ecommerce product pipeline that syncs, transforms, and pushes data between systems. That's data engineering work.
>
> ❌ Bad: "project has PHP files → pick `php-pro`"
> ✅ Good: "project has 11K+ PHP files with complex OOP patterns, generators, and SPL usage → `php-pro` will help write idiomatic PHP"

For each selected skill, state WHY it's relevant — citing a specific aspect of the project, not just a keyword overlap.

**Hard rules:**

- Max ONE skill per concern area (e.g., pick one code review skill, one testing skill)
- Skip skills for languages/frameworks/platforms NOT in the project
- Skip penetration testing unless it's a security project
- Prefer specific skills (e.g., `laravel-expert`) over generic ones (e.g., `backend-architect`) when both exist

5. **Install selected skills**:

```bash
SKILLS_TMP=$(cat /tmp/.skills_tmp_path)

# Remove existing curated skills (both directories and symlinks)
find .agent/skills/ -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} +
find .agent/skills/ -mindepth 1 -maxdepth 1 -type l -exec rm -f {} +
mkdir -p .agent/skills

# Copy each selected skill from temp clone
for skill in <space-separated list from step 4>; do
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
SKILLS_TMP=$(cat /tmp/.skills_tmp_path)
rm -rf "$SKILLS_TMP"
rm -f /tmp/.skills_tmp_path /tmp/.skills_catalog.json
echo "Cleaned up."
```

7. **Verify** the bundle:

```bash
echo "Skills installed:"
count=$(ls -1d .agent/skills/*/ 2>/dev/null | wc -l)
echo "Count: $count"
echo ""
for d in .agent/skills/*/; do
  name=$(basename "$d")
  if [ -f "$d/SKILL.md" ]; then
    echo "✅ $name"
  else
    echo "❌ $name (missing SKILL.md)"
  fi
done
```

Confirm count is ≤ 20 and every directory contains a SKILL.md.

## Output

Report to the user with your reasoning:

### Project Profile

[3-5 line summary from step 2]

### Selected Skills (N/20)

| #   | Skill      | Reason         |
| --- | ---------- | -------------- |
| 1   | skill-name | Your reasoning |

### Notable Exclusions

| Skill      | Reason                                       |
| ---------- | -------------------------------------------- |
| skill-name | Why it was excluded despite seeming relevant |
