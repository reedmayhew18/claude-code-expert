---
name: existing-project
description: Install Claude Code expert toolkit into an existing project. Use when the user says "add to my project", "install into existing", "set up existing project", "integrate", "add skills to this project", or wants to enhance an already-started codebase with Claude Code best practices.
argument-hint: "[project path or 'here' for current directory]"
disable-model-invocation: true
---

# Existing Project Integration

Add the Claude Code expert toolkit to a project that already exists. Non-destructive by default. Only adds files — never modifies or deletes existing ones without explicit permission.

## Process

### Phase 1: Assess Current State
Scan the target project silently. Read but do not modify:
- `CLAUDE.md` — read fully, note line count, understand existing rules
- `.claude/` — check for skills, agents, settings, rules
- `.claude/settings.json` — note existing permissions and hooks
- `reference/` — check if our guides are already installed
- Tech stack files: package.json, pyproject.toml, Cargo.toml, go.mod, Makefile, etc.
- README.md for project context

Present a brief summary: "Here's what your project has, here's what I'll add."

### Phase 2: Interview (Light)
Only ask questions not already answered by the scan:
1. Any conventions or rules you want Claude to know about? (Skip if CLAUDE.md already covers this)
2. Show the available skills/agents list — want any extras beyond the essentials?
3. Which CLAUDE.md integration level do you want? (Explain the three options below)

### Phase 3: Install Reference Library
Copy `reference/*.md` to `<target>/reference/`.
- NEVER overwrite existing files in the target's reference/ directory
- Skip files that already exist with the same name

### Phase 4: Install Skills
Copy essential skills to `<target>/.claude/skills/`:

**Always install:**
- wizard, plan-and-spec, tdd, code-review, refactor
- grill-me, git-workflow, progress-tracker, context-doctor
- research, voice-style (with all style templates), voice-creator
- project-optimizer (from `available-skills/` — deep scan and optimization tool)

**Install if requested:**
- Any skills from `available-skills/` the user selected

**Rules:**
- NEVER overwrite existing skills — if a skill folder exists, skip it
- Note any conflicts: "Skipped `/tdd` — you already have one"

### Phase 5: Install Agents
Copy core agents to `<target>/.claude/agents/`:

**Always install:**
- code-reviewer.md, debugger.md, researcher.md

**Auto-add if tech stack matches:**
- python-expert.md (Python projects)

**Install if requested:**
- Any from `available-agents/`

NEVER overwrite existing agents.

### Phase 6: CLAUDE.md Integration (3 tiers)

Present these options to the user:

---

**Option 1: Minimal (just register what we added)**

Only append to the bottom of their existing CLAUDE.md:
```markdown

## Installed Skills
[List of skills we just added with one-line descriptions]

## Claude Code Reference
Consult `reference/` guides for Claude Code optimization, context management, and skill creation.
```

Does NOT change anything else. Their CLAUDE.md stays exactly as-is. Use this when the user has a well-crafted CLAUDE.md they don't want touched.

---

**Option 2: Standard (add essentials without changing existing content)**

Keep everything in their existing CLAUDE.md untouched, but ADD these sections if they don't already exist:
- Installed Skills list
- Claude Code Reference pointers
- MCP Security Warning (the full warning block from our CLAUDE.md)
- Python venv rule: "NEVER use --break-system-packages" (if Python project)
- Platform environment rules (if relevant)

Check the total line count after additions. If it would exceed 200 lines, warn the user and suggest Option 3 or trimming. Do NOT silently exceed 200 lines.

---

**Option 3: Full optimization (merge and rewrite)**

Read their CLAUDE.md thoroughly, then rewrite the entire file to be optimized per our best practices:

1. PRESERVE every existing rule, convention, command, and project-specific instruction
2. REORGANIZE into our recommended structure (Project Overview, Tech Stack, Commands, Architecture, Conventions, Skills, Rules)
3. COMPRESS verbose sections — replace paragraphs with bullets, remove redundant instructions
4. ADD missing essentials (MCP warning, venv rule, skills list, reference pointers)
5. REMOVE generic advice Claude already knows ("write clean code", "add error handling")
6. TARGET under 150 lines (absolute max 200)
7. USE progressive disclosure — move detailed docs to `.claude/rules/` files if needed

**Present the rewritten version to the user for review before saving.** Never overwrite CLAUDE.md without showing them the diff.

---

### Phase 7: Offer Skill Customization

ONLY customize the skills WE just added. Never touch pre-existing skills.

Ask: "Want me to customize any of the new skills for your project?"

If yes, for each skill they want customized:
1. Read the skill's SKILL.md
2. Rewrite descriptions and instructions to reference their specific:
   - Test runner and test commands
   - Build system and commands
   - Linter/formatter
   - Framework conventions
   - Branch naming and PR conventions
3. Add project-specific examples
4. Save the customized version (this only modifies files WE just created)

### Phase 8: Post-Install Optimization Scan (Optional)

After everything is installed, offer: "Want me to scan your project for Claude Code optimization opportunities?"

If yes, check for:

**CLAUDE.md health:**
- Over 200 lines? → Suggest trimming or splitting into `.claude/rules/`
- Missing build/test/lint commands? → Suggest adding them
- Contains generic advice Claude already knows? → Suggest removing
- Has contradictory instructions? → Flag them
- Missing @-imports for detailed docs? → Suggest progressive disclosure

**Skills & agents health:**
- More than 30 skills loaded? → Suggest moving some to available-skills/
- Skill descriptions vague or too broad? → Suggest rewrites for better activation
- Missing skills for detected workflows? → Suggest from our library

**Settings health:**
- No permissions configured? → Suggest common allow rules for their build tools
- No hooks configured? → Suggest auto-format hook for their language
- No `.gitignore` for `.claude/settings.local.json`? → Add it

**Project structure:**
- No PROGRESS.md or PLAN.md patterns? → Explain the Document & Clear workflow
- Large monorepo without subdirectory CLAUDE.md files? → Suggest adding them
- No `.claude/rules/` for path-specific conventions? → Suggest if applicable

Present findings as a checklist with severity (recommended / nice-to-have / FYI). Let the user pick which to implement.

### Phase 8.5: Deep Project Optimization (Optional)

After the quick scan, offer one more option:

"Want me to do a deep dive? I can read through your actual codebase — your code, tests, CI/CD, documentation — and suggest workflow and structural improvements based on Claude Code best practices."

If yes, run `/project-optimizer full` (which we just installed). This does a comprehensive read-only analysis of their entire project including code patterns, test coverage gaps, documentation quality, CI/CD opportunities, and produces a prioritized report. See the project-optimizer skill for the full process.

This is the difference between "is your Claude Code setup good?" (Phase 8) and "is your project itself good?" (Phase 8.5).

### Phase 9: Summary

Report everything:
```
Installed:
  Skills: 12 added, 2 skipped (already existed)
  Agents: 4 added
  Reference guides: 8 added
  Voice styles: 8 added

CLAUDE.md: [Option chosen] - [what changed]

Post-install scan: [findings if run, or "skipped"]

Next steps:
  - cd to your project and run `claude`
  - Try `/wizard` to implement your next feature
  - Try `/voice-style concise` for terse responses
  - Run `/context` to see your context budget
```

## Important Rules
- NEVER delete or overwrite existing files (skills, agents, CLAUDE.md, settings)
- Only MODIFY files we just created (during customization phase)
- For CLAUDE.md Option 3: always show diff and get approval before saving
- If `.claude/settings.json` exists, preserve ALL existing permissions and hooks
- Ask before every write if the target is outside the current directory
- If the target IS the current directory, warn that this IS the expert toolkit
