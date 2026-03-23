---
name: new-project
description: Create a fully configured new project with Claude Code best practices, skills, and agents. Use when the user says "new project", "start a project", "create a project", "set up a new", or "bootstrap a project".
argument-hint: "[project name or description]"
disable-model-invocation: true
---

# New Project Creator

Create a new project folder adjacent to this expertise repo, fully configured with Claude Code best practices, selected skills, agents, and a customized CLAUDE.md.

## Process

### Phase 1: Choose Setup Style
Ask the user how they want to set up:

**Option A: Quick Setup** (default — light Q&A, ~5 questions)
Get the essentials and start building. Best for simple projects or users who want to get going fast.

**Option B: Deep Setup** (`/grill-me` — thorough interview)
Walk every branch of the design tree. Best for complex projects or when the user wants to think everything through before starting.

Suggest Quick Setup as default. If the user says "grill me" or asks for the thorough version, switch to Option B (run `/grill-me` and use its output to inform the rest of the setup).

### Phase 1a: Quick Setup Interview
Ask the user (keep it conversational, not a form):

1. **Project name** - What should the folder be called?
2. **What are you building?** - Web app, API, CLI tool, Python package, static site, content project, data pipeline, mobile app, or something else?
3. **Tech stack** - Languages, frameworks, databases? (If they don't know, recommend based on what they're building)
4. **Scope** - Quick prototype, side project, or production app?
5. **Document formats** - Will you need to create or work with any of these?
   - PDF (create, read, merge, OCR)
   - Word documents (.docx)
   - PowerPoint presentations (.pptx)
   - Excel spreadsheets (.xlsx)
   Install the corresponding skill for each one they say yes to.
6. **Special needs** - Any of these relevant?
   - SEO / content marketing
   - Brand voice / content creation
   - Complex frontend / web design
   - API design / full-stack
   - Data science / ML
   - DevOps / deployment

### Phase 2: Select the Kit
Based on the interview, assemble the package:

**Always included (essential kit):**
- `wizard/` - 8-phase production implementation
- `plan-and-spec/` - Spec-driven planning
- `tdd/` - Test-driven development
- `code-review/` - Code review via subagent
- `refactor/` - Safe refactoring
- `grill-me/` - Deep interview before building
- `git-workflow/` - Structured git operations
- `progress-tracker/` - State persistence across sessions
- `context-doctor/` - Context window troubleshooting
- `research/` - Web research with source evaluation
- `voice-style/` - Interaction style switching (with all style templates)
- `workflow/` - Multi-step pipeline orchestration with state tracking
- `wrap-up/` - End-of-session learning capture
- `project-optimizer/` - Deep project scan and optimization (from `available-skills/`)

**Always included agents:**
- `orchestrator.md` - Workflow coordination (sonnet)
- `code-reviewer.md` - Code review (sonnet)
- `debugger.md` - Root cause analysis (sonnet)
- `researcher.md` - Codebase exploration (haiku)

**Offer based on project type:**

| Project Type | Recommended Skills | Recommended Agents |
|-------------|-------------------|-------------------|
| Web app / frontend | web-scaffold | web-designer, fullstack-dev |
| Python project | python-scaffold | python-expert |
| API / backend | python-scaffold or web-scaffold | fullstack-dev, python-expert |
| Content / marketing | seo-content, brainstorm | creative-writer, seo-expert, brand-voice-expert |
| Product / startup | brainstorm | product-designer, brainstormer |
| Any large project | deploy-checklist | (based on stack) |

Present the recommended package and let the user add/remove before proceeding.

### Phase 3: Create the Project
The new project folder is created **adjacent to this repo** (in the parent directory).

```
../                              # Parent directory
├── claude-code-expert/          # This repo (stays untouched)
└── <new-project-name>/          # NEW - created here
    ├── CLAUDE.md                # Customized for this project
    ├── .claude/
    │   ├── skills/              # Selected skills copied here
    │   ├── agents/              # Selected agents copied here
    │   └── settings.json        # Basic permissions setup
    ├── reference/               # Claude Code expertise (always included)
    │   ├── 01-official-docs.md
    │   ├── 02-best-practices.md
    │   ├── 03-skills-and-agents.md
    │   ├── 04-context-and-memory.md
    │   ├── 05-workflows-and-automation.md
    │   ├── 06-guides-and-tutorials.md
    │   ├── 07-brand-and-content-skills.md
    │   └── 08-cross-platform-environments.md
    ├── .gitignore
    └── (project-specific files based on scaffold skill if used)
```

Steps:
1. Create the project directory at `../<project-name>/`
2. Copy `reference/*.md` to `../<project-name>/reference/` (the Claude Code expertise library - this is ALWAYS included so the project has full Claude Code knowledge)
3. Copy selected skills from `.claude/skills/` and `available-skills/`
4. Copy selected agents from `.claude/agents/` and `available-agents/`
5. Copy voice style templates
6. Create `.gitignore` with `.claude/settings.local.json`, `.venv/`, `node_modules/`, etc.
7. Initialize git repo

NOTE: The reference files are the project's "Claude Code brain." They are NOT loaded into context automatically - Claude reads them on demand when it needs to look up best practices, skill architecture, context management strategies, etc. There is zero context cost to including them. They ensure every project created from this toolkit has the same expert-level Claude Code knowledge.

### Phase 4: Customize CLAUDE.md
Write a CLAUDE.md tailored to their project. This is NOT a copy of our CLAUDE.md. It should be:

- **Under 150 lines** (ideally under 100)
- **Project-specific**: tech stack, build commands, conventions
- **Include the MCP security warning** (always)
- **Include the Python venv rule** (if Python project)
- **Reference their chosen skills** so they know what's available

Use this structure:
```markdown
# CLAUDE.md
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
[One line: what this project is]

## Tech Stack
[Languages, frameworks, key dependencies]

## Commands
[Build, test, lint, run - exact commands]

## Architecture
[Only what requires reading multiple files to understand]

## Conventions
[Project-specific rules, not generic advice]

## Available Skills
[List of installed skills with one-line descriptions]

## Claude Code Expertise
This project includes Claude Code reference guides in `reference/`. Consult them when you need to:
- Optimize context management: `reference/02-best-practices.md`
- Create or improve skills: `reference/03-skills-and-agents.md`
- Manage context/compaction: `reference/04-context-and-memory.md`
- Set up automation/hooks: `reference/05-workflows-and-automation.md`
- Handle platform differences: `reference/08-cross-platform-environments.md`

## Rules
[NEVER/ALWAYS items, MCP warning, venv rule if applicable]
```

### Phase 5: Offer Customization
Ask: "Would you like me to customize any of the skills for your specific project?"

If yes, for each skill they want customized:
1. Read the skill's SKILL.md
2. Rewrite the description and instructions to reference their specific tech stack, conventions, and patterns
3. Add project-specific examples
4. Append ` (Customized)` to the end of the `description:` field in the YAML frontmatter — this marks it so `/skill-store restore` can identify and revert it later
5. Save the customized version (replacing the generic one in their project)

Common customizations:
- **TDD**: Add their specific test runner commands and patterns
- **Code review**: Add their specific conventions and anti-patterns to check
- **Git workflow**: Add their branch naming convention and PR template
- **Wizard**: Add their specific build/test/lint commands to each phase

### Phase 6: Confirm
Summarize what was created:
- Project path
- Skills installed (count)
- Agents installed (count)
- Voice styles available
- Next steps for the user

Suggest: "cd into your new project and start with `/grill-me` to plan your first feature, or `/wizard` to implement something right away."

## Important Notes
- This skill creates files OUTSIDE the current project directory (in the parent). This is the intended behavior.
- Never modify the claude-code-expert repo itself during project creation.
- The new project should be immediately usable - `cd ../new-project && claude` should work.
- If a scaffold skill is selected (web-scaffold, python-scaffold), offer to run it after the base setup.
