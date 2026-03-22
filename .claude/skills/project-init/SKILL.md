---
name: project-init
description: Initialize or optimize a project for Claude Code. Use when setting up a new project, onboarding to an existing codebase, or when the user says "set up Claude Code", "create CLAUDE.md", "bootstrap", or "optimize this project for Claude".
argument-hint: "[project-path or description]"
disable-model-invocation: true
---

# Project Initialization for Claude Code

Set up or optimize a project to work effectively with Claude Code. This creates a lean, high-signal CLAUDE.md and supporting structure.

## Process

### Step 1: Assess the Project
- Read existing CLAUDE.md, README.md, package.json, Makefile, pyproject.toml, or similar
- Identify: language, framework, build system, test runner, linter
- Check for existing `.claude/` directory, skills, agents, settings
- Look for Cursor rules (`.cursor/rules/`), Copilot rules (`.github/copilot-instructions.md`)

### Step 2: Create CLAUDE.md
Write a CLAUDE.md following these rules:

**MUST include:**
- Project purpose (1 line)
- Build, test, lint commands (exact commands, not descriptions)
- Architecture overview (only what requires reading multiple files to understand)
- Non-obvious conventions and gotchas
- Hard rules (NEVER/ALWAYS items specific to this project)

**MUST NOT include:**
- Generic development practices Claude already knows
- File-by-file descriptions discoverable by reading code
- Long explanations or tutorials
- Obvious instructions ("write clean code", "add error handling")
- API documentation (link to it with `@path` imports instead)

**Format rules:**
- Target under 200 lines (under 100 is better)
- Use markdown headers and bullets
- Use emphasis for critical rules: "IMPORTANT:", "NEVER:", "ALWAYS:"
- Use `@path/to/file.md` imports for detailed docs

### Step 3: Create Supporting Structure
Only create what's needed:

```
.claude/
├── settings.json        # Only if permissions or hooks needed
├── skills/              # Only if reusable workflows identified
├── agents/              # Only if specialized roles needed
└── rules/               # Only if path-specific rules needed
```

**Rules files** (`.claude/rules/`) - create when:
- Different conventions apply to different directories
- Frontend vs backend have different patterns
- Test files need different rules than source files

Format:
```yaml
paths:
  - "src/api/**/*.ts"

Rules content here...
```

### Step 4: Suggest Quick Wins
Based on the project, suggest:
- 1-2 hooks that would help (auto-format, safety checks)
- 1-2 skills worth creating (deploy, review, etc.)
- Permission allowlist entries for common commands
- Whether subagents would help (monorepo, large codebase)

## Output
Present the CLAUDE.md content for review before writing. Explain any non-obvious choices.
