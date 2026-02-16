---
description: Generate a project-specific skills bundle by analyzing the codebase
---

# Generate Skills Bundle

Clone the skills repo, extract a catalog, summarize the codebase, reason about which skills match, and install them.

// turbo-all

## Steps

1. **Clone skills repo to tmp**:

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

2. **Extract frontmatter from every SKILL.md into a plain text catalog**:

One skill per line: `slug - description`

```bash
SKILLS_TMP=$(cat /tmp/.skills_tmp_path)
python3 -c "
import os, re

base = os.path.join('$SKILLS_TMP', 'skills')
lines = []
for name in sorted(os.listdir(base)):
    skill_md = os.path.join(base, name, 'SKILL.md')
    if not os.path.isfile(skill_md):
        continue
    desc = ''
    with open(skill_md) as f:
        content = f.read(2000)
    fm = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if fm:
        for line in fm.group(1).splitlines():
            if line.strip().lower().startswith('description:'):
                desc = line.split(':', 1)[1].strip().strip('\"').strip(\"'\")[:150]
                break
    if not desc:
        body = content.split('---', 2)[-1].strip() if '---' in content else content
        for line in body.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('---'):
                desc = line[:150]
                break
    lines.append(f'{name} - {desc}')

with open('/tmp/.skills_catalog.txt', 'w') as f:
    f.write('\n'.join(lines) + '\n')
print(f'Catalog: {len(lines)} skills, one per line')
"
```

3. **Reason through the codebase** to understand what this project is:

Explore the project freely — look at file extensions, directory structure, dependency files (composer.json, package.json, etc. wherever they live), infrastructure (Dockerfile, docker-compose, Makefile, CI configs), and any other signals that reveal the tech stack, architecture, and domain.

Use whatever tools make sense: `find`, `ls`, `cat`, `view_file`, etc. Don't rely on a single fixed script — poke around until you understand:

- What languages/frameworks are used
- What the project actually does (its domain)
- How it's built, tested, and deployed
- What kinds of problems developers face working on it

After exploring, write a 3-5 line **project profile** summarizing the tech stack, architecture, domain, and key concerns.

4. **Read the catalog and reason about skill selection**:

Read `/tmp/.skills_catalog.txt` using `view_file`.

You now have:

- The **project profile** from step 3
- The **full skill catalog** with slug + description for every skill

Using both, reason about which skills genuinely match this project — the same way you'd answer "which of these skills are relevant to this project?" if someone pasted both into a conversation.

**Selection rules:**

- Select 10-20 skills maximum
- Max ONE skill per concern area (e.g., one code review skill, one testing skill, one bash skill)
- Skip skills for languages/frameworks/platforms NOT in the project
- Skip penetration testing unless it's a security project
- Prefer specific skills (e.g., `laravel-expert`) over generic ones (e.g., `backend-architect`) when both exist
- Do NOT keyword-match — match based on what the project actually does and what problems its developers face

> ❌ Bad: "project has PHP files → pick `php-pro`"
> ✅ Good: "project has complex OOP patterns, generators, SPL usage → `php-pro` helps write idiomatic PHP"

5. **Install selected skills**:

```bash
SKILLS_TMP=$(cat /tmp/.skills_tmp_path)

# Remove existing skills
find .agent/skills/ -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} +
find .agent/skills/ -mindepth 1 -maxdepth 1 -type l -exec rm -f {} +
mkdir -p .agent/skills

# Copy each selected skill
for skill in <space-separated slugs from step 4>; do
  if [ -d "$SKILLS_TMP/skills/$skill" ]; then
    cp -r "$SKILLS_TMP/skills/$skill" ".agent/skills/$skill"
    echo "✅ $skill"
  else
    echo "⚠️  $skill not found in repo"
  fi
done
```

6. **Clean up**:

```bash
SKILLS_TMP=$(cat /tmp/.skills_tmp_path)
rm -rf "$SKILLS_TMP"
rm -f /tmp/.skills_tmp_path /tmp/.skills_catalog.txt
echo "Cleaned up."
```

7. **Verify**:

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

Confirm count is ≤ 20 and every directory has a SKILL.md.

## Output

Report to the user:

### Project Profile

[3-5 line summary from step 3]

### Selected Skills (N/20)

| #   | Skill      | Reason                             |
| --- | ---------- | ---------------------------------- |
| 1   | skill-name | Why it matches a real project need |

### Notable Exclusions

| Skill      | Reason                                |
| ---------- | ------------------------------------- |
| skill-name | Why excluded despite seeming relevant |
