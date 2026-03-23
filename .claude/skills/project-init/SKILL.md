---
name: project-init
description: Initialize or optimize a project for Claude Code. Use when setting up a new project, onboarding to an existing codebase, or when the user says "set up Claude Code", "create CLAUDE.md", "bootstrap", or "optimize this project for Claude".
argument-hint: "[project-path or description]"
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Project Initialization for Claude Code

## Goal
Produce a lean, high-signal CLAUDE.md (under 200 lines) and minimal supporting `.claude/` structure so Claude Code has accurate, project-specific guidance from the first message of every session. Success = CLAUDE.md written, user has reviewed and approved it, and any quick-win suggestions are surfaced.

## Dependencies
- Tools: Read, Write, Edit, Bash, Glob, Grep
- No external services or MCP servers required
- CLI: none required beyond standard shell

## Context
- Reads existing project files to extract real conventions — never invents them
- Reference for what belongs in CLAUDE.md vs what to omit is encoded in Step 2 below
- Works for any language/framework; adapt commands and structure to what's found

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

### Step 3 Checkpoint

**CHECKPOINT:** Before writing any files, present the proposed CLAUDE.md content to the user. Explain any non-obvious choices (why something was included or omitted). Do NOT write files until the user approves.
Ask: "Here's the proposed CLAUDE.md. Want me to write it as-is, adjust anything, or take a different approach?"

### Step 4: Suggest Quick Wins
Based on the project, suggest:
- 1-2 hooks that would help (auto-format, safety checks)
- 1-2 skills worth creating (deploy, review, etc.)
- Permission allowlist entries for common commands
- Whether subagents would help (monorepo, large codebase)

**CHECKPOINT:** After writing the file, confirm with the user that the setup is complete and ask if they want any of the suggested quick wins implemented now.

## Output
- **Primary deliverable:** `CLAUDE.md` at the project root (or specified path)
- **Optional:** `.claude/settings.json`, `.claude/rules/*.md` files if needed
- **Format:** Markdown, under 200 lines
- **Save location:** Project root (or `$ARGUMENTS` path if provided)
- Present content for review before writing; do not overwrite an existing CLAUDE.md without explicit user confirmation
