---
name: existing-project
description: Install Claude Code expert toolkit into an existing project. Use when the user says "add to my project", "install into existing", "set up existing project", "integrate", "add skills to this project", or wants to enhance an already-started codebase with Claude Code best practices.
argument-hint: "[project path or 'here' for current directory]"
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Existing Project Integration

Add the Claude Code expert toolkit to a project that already exists. Non-destructive by default. Only adds files — never modifies or deletes existing ones without explicit permission.

## Goal
Install skills, agents, and reference guides into an existing codebase non-destructively. Configure CLAUDE.md to register them. Leave the user with a working Claude Code setup tailored to their tech stack. Done when the summary report is presented and user confirms.

## Dependencies
- Tools: Read, Write, Bash, Glob, Grep
- Source paths: `available-skills/`, `available-agents/`, `reference/` (must run from claude-code-expert project root)

## Context
Reads `available-skills/INDEX.md` and `available-agents/INDEX.md` to know what's installable. Reads the target project's existing CLAUDE.md, settings, and config files to avoid conflicts.

## Process

### Phase 1: Analyze the Project
Scan the target project thoroughly. Read but do not modify:
- `CLAUDE.md` — read fully, note line count, understand existing rules
- `.claude/` — check for skills, agents, settings, rules
- `.claude/settings.json` — note existing permissions and hooks
- `reference/` — check if our guides are already installed
- Tech stack files: package.json, pyproject.toml, Cargo.toml, go.mod, Makefile, Dockerfile, etc.
- README.md, CONTRIBUTING.md for project context
- Source directory structure (src/, lib/, app/, etc.)
- Test directory structure and test framework
- CI/CD config (.github/workflows/, .gitlab-ci.yml)

**Auto-detect and recommend** relevant available skills and agents based on what you find:

| You detect... | Recommend |
|---|---|
| Python files, pyproject.toml, requirements.txt | `python-expert` agent, `python-scaffold` skill |
| React/Vue/Svelte, package.json with frontend deps | `web-designer` agent, `frontend-design` skill |
| PyTorch, transformers, ML model code | `pytorch-dev` agent, `neural-architect` agent, ML skills |
| Express/Fastify/Next.js, API routes | `fullstack-dev` agent |
| Dockerfile, K8s manifests, IaC | `deploy-checklist` skill |
| .docx/.pdf/.xlsx/.pptx files or generation code | Corresponding document format skills |
| Marketing/content directories, blog posts | `seo-content`, `creative-writer` agent |
| Test files with low coverage | `tdd` skill emphasis |
| Playwright/Cypress config | `webapp-testing` skill |

Present: "I've analyzed your project. Here's what I found: [summary]. Based on your tech stack, I'd recommend these additional skills/agents: [list]. Want to include them?"

### Phase 2: Interview (Light)
Only ask questions not already answered by the scan:
1. Any conventions or rules you want Claude to know about? (Skip if CLAUDE.md already covers this)
2. **Document formats** — Will you need to create or work with any of these?
   - PDF (create, read, merge, OCR)
   - Word documents (.docx)
   - PowerPoint presentations (.pptx)
   - Excel spreadsheets (.xlsx)
   Install the corresponding skill for each one they say yes to.
3. Present auto-recommended skills/agents from Phase 1 — confirm or adjust
4. Want any additional extras from the available library? (Show remaining options)
5. Which CLAUDE.md integration level do you want? (Explain the three options below)

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
- workflow, wrap-up (AGI Flow: pipeline chaining and learning capture)
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
4. Append ` (Customized)` to the end of the `description:` field in the YAML frontmatter — this marks it so `/skill-store restore` can identify and revert it later
5. Save the customized version (this only modifies files WE just created)

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

### Phase 9: Write post_install.md

**Always create `post_install.md` in the target project root.** This is the handoff document that the user's next Claude session will execute to finish setup.

The file should follow this structure:

```markdown
# Post-Install — Claude Code Expert Toolkit ([date])

[User name] just installed the Claude Code expert toolkit into this project. Here's what changed and what needs to happen next.

## What Was Installed

### [N] new skills in `.claude/skills/`
[List skills by category. Note which ones were customized with (Customized) tag.]

### [N] new agents in `.claude/agents/`
[List agents and their roles.]

### [N] reference guides in `reference/`
[Brief note about the expertise library.]

### [N] voice style templates
[Note available styles.]

### CLAUDE.md updated ([integration level chosen])
[What was added/changed. Note final line count.]

## Action Items

### 1. [Most critical post-install task]
[Specific command to run, e.g., install a linter, verify test runner]

### 2. [Second task]
[...]

### 3. [Optimization recommendations if scan was run]
[From Phase 8/8.5 findings]

### N. Delete this file
Once you've read and acted on this, delete `post_install.md` — it's a one-time handoff document.

---

## Key Skills to Try
[Table of most relevant installed skills with one-line descriptions and when to use each]
```

Include action items for:
- Any tools referenced in CLAUDE.md that aren't yet installed (linters, test runners, formatters)
- Permission adjustments needed in settings
- Optimization recommendations from Phase 8/8.5 (if run)
- Any customization follow-ups

### Phase 10: Final Instructions to User

Tell the user:
```
Installation complete! To finish setup:

1. cd <target-project-path>
2. Start Claude: `claude`
3. Run: `execute post_install.md`

Claude will read the handoff document and complete the remaining setup steps.
```

## Important Rules
- NEVER delete or overwrite existing files (skills, agents, CLAUDE.md, settings)
- Only MODIFY files we just created (during customization phase)
- For CLAUDE.md Option 3: always show diff and get approval before saving
- If `.claude/settings.json` exists, preserve ALL existing permissions and hooks
- Ask before every write if the target is outside the current directory
- If the target IS the current directory, warn that this IS the expert toolkit
