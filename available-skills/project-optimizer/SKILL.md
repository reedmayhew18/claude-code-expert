---
name: project-optimizer
description: Deep scan and optimization of your project's Claude Code setup, workflows, and codebase patterns. Use when the user says "optimize", "audit my project", "scan for improvements", "how can I improve", "check my setup", or "what am I doing wrong".
argument-hint: "[focus area or 'full' for complete scan]"
disable-model-invocation: true
context: fork
agent: Explore
---

# Project Optimizer

Deep analysis of your project's structure, Claude Code configuration, and development workflows. Produces a prioritized list of actionable improvements.

This is a read-only scan. Nothing is modified. You review the findings and decide what to implement.

## Process

### Phase 1: Project Discovery

Read everything relevant to understand the project holistically:

**Codebase scan:**
- Read CLAUDE.md, README.md, CONTRIBUTING.md, any docs/ folder
- Identify tech stack from config files (package.json, pyproject.toml, Cargo.toml, go.mod, Makefile, Dockerfile, etc.)
- Identify test framework, linter, formatter, build system
- Check directory structure — is it flat? deeply nested? monorepo?
- Estimate project size (file count, major directories)
- Read `.gitignore` for patterns
- Check recent git history if available: how often are commits made? by how many people?

**Claude Code setup scan:**
- Read CLAUDE.md line by line — check for: length, specificity, contradictions, generic advice, missing essentials
- Inventory `.claude/skills/` — read each SKILL.md description, check activation patterns
- Inventory `.claude/agents/` — check descriptions, model choices, tool restrictions
- Read `.claude/settings.json` — permissions, hooks, configuration
- Check `.claude/rules/` — path-scoped rules, coverage
- Check `reference/` — are Claude Code guides installed?
- Count total skill descriptions and estimate context budget usage

**Workflow scan:**
- Check for CI/CD files (.github/workflows/, .gitlab-ci.yml, Jenkinsfile)
- Check for pre-commit hooks (.pre-commit-config.yaml, .husky/)
- Check for testing infrastructure (test directories, coverage config)
- Check for documentation practices (inline docs, API docs, changelogs)

### Phase 2: Analysis

Evaluate findings against best practices from the reference library. Check each category:

**CLAUDE.md Quality (reference: 02-best-practices.md, 04-context-and-memory.md)**
- [ ] Under 200 lines? (ideal: under 150, critical: under 100 for small projects)
- [ ] Contains actual build/test/lint commands? (not descriptions — exact commands)
- [ ] Architecture section covers only what requires reading multiple files to understand?
- [ ] Free of generic advice Claude already knows?
- [ ] No contradictory instructions?
- [ ] Uses emphasis (NEVER/ALWAYS/IMPORTANT) for critical rules only?
- [ ] Uses `@path/to/file` imports for detailed documentation?
- [ ] Has platform-appropriate environment rules?
- [ ] Includes MCP security warning?
- [ ] Includes Python venv rule (if Python)?

**Context Management (reference: 04-context-and-memory.md)**
- [ ] Skill descriptions concise enough to stay within budget?
- [ ] Progressive disclosure in use? (detailed docs in separate files, not CLAUDE.md)
- [ ] Path-scoped rules (`.claude/rules/`) for directory-specific conventions?
- [ ] Subdirectory CLAUDE.md files for monorepo or large projects?
- [ ] Any strategy for state persistence across sessions? (PROGRESS.md, HANDOFF.md)

**Skills Health (reference: 03-skills-and-agents.md)**
- [ ] Descriptions include trigger phrases that match how users actually talk?
- [ ] Skills with side effects have `disable-model-invocation: true`?
- [ ] Reference-only skills have `user-invocable: false`?
- [ ] Heavy skills use `context: fork` to protect main context?
- [ ] SKILL.md files under 500 lines? (under 200 ideal)
- [ ] Large reference material in supporting files, not inline?
- [ ] No skill description conflicts (two skills triggering for same task)?

**Agents Health (reference: 03-skills-and-agents.md)**
- [ ] Each agent has a focused, non-overlapping description?
- [ ] Model choices match task complexity? (haiku for research, sonnet for daily work, opus for architecture)
- [ ] Tool restrictions appropriate? (read-only agents don't have Write/Edit)
- [ ] Agents that should run in background have `background: true`?
- [ ] Not too many agents? (more descriptions = harder for Claude to pick the right one)

**Automation Opportunities (reference: 05-workflows-and-automation.md)**
- [ ] Auto-format hook for their language? (prettier, ruff, gofmt, etc.)
- [ ] Safety hooks for destructive commands?
- [ ] Pre-commit integration?
- [ ] CI/CD could benefit from Claude Code integration?
- [ ] Recurring tasks that could use `/loop`?

**Project Structure (reference: 04-context-and-memory.md, 08-cross-platform-environments.md)**
- [ ] `.gitignore` includes `.claude/settings.local.json`?
- [ ] `.gitignore` includes `.venv/`, `node_modules/`, other generated directories?
- [ ] Test files organized consistently?
- [ ] Documentation accessible and up to date?
- [ ] Environment-specific gotchas addressed? (WSL performance, shell differences)

### Phase 3: Produce Report

Organize findings into a prioritized report:

```markdown
# Project Optimization Report

## Summary
[1-2 sentences: overall health assessment]

## Critical (fix these first)
Items that actively hurt Claude Code performance or pose risks.
- [ ] Finding with specific file reference and fix

## Recommended (significant improvements)
Items that would meaningfully improve workflows.
- [ ] Finding with specific suggestion

## Nice to Have (polish)
Items that would make things cleaner.
- [ ] Finding with suggestion

## Already Good
Things the project does well (positive reinforcement).
- What's working and why

## Suggested Skills/Agents
Based on this project's tech stack and workflows:
- [Skill/agent name]: why it would help

## Suggested Hooks
- [Hook description]: what it automates and the config snippet
```

### Phase 4: Present and Offer Implementation

1. Present the report to the user
2. Offer to save it as `OPTIMIZATION-REPORT.md`
3. For each Critical and Recommended finding, offer to implement the fix
4. For CLAUDE.md rewrites, always show the diff before saving
5. For hook suggestions, provide the exact `.claude/settings.json` configuration

## Focus Modes

If the user specifies a focus area instead of "full":

| Argument | What to scan |
|---|---|
| `claude-md` | Only CLAUDE.md quality and content |
| `skills` | Only skills health and activation |
| `agents` | Only agents health and configuration |
| `context` | Only context management and progressive disclosure |
| `automation` | Only hooks, CI/CD, and automation opportunities |
| `security` | Only MCP warnings, secrets exposure, permission gaps |
| `performance` | Only context budget, skill loading, agent model choices |
| `full` | Everything (default) |

## Important Rules
- This is a READ-ONLY scan. Do not modify any files during analysis.
- Only implement changes the user explicitly approves.
- For CLAUDE.md changes, always show the diff before writing.
- Be specific: "Line 47 of CLAUDE.md says X, which should be Y" not "CLAUDE.md could be improved."
- Cite which reference guide supports each recommendation.
- Celebrate what's already done well — don't just list problems.
