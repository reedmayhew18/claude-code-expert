---
name: git-workflow
description: Structured git workflow for commits, branches, and PRs. Use when the user says "commit", "create PR", "branch", "prepare for review", or "ship this".
argument-hint: "[commit/pr/branch] [description]"
disable-model-invocation: true
---

# Git Workflow

Structured git operations with safety checks.

## Commands

### Commit: `/git-workflow commit [message]`
1. Run `git status` and `git diff --staged` to understand changes
2. Check for sensitive files (.env, credentials, secrets) - WARN if found
3. If no message provided, draft one based on changes:
   - Prefix: feat/fix/refactor/docs/test/chore
   - Focus on WHY, not WHAT (the diff shows what)
   - Under 72 chars for subject line
4. Stage specific files (never `git add -A` or `git add .`)
5. Create the commit

### Branch: `/git-workflow branch [name]`
1. Ensure clean working tree (warn if uncommitted changes)
2. Fetch latest from remote
3. Create branch from main/master with conventional name:
   - `feat/description`, `fix/description`, `refactor/description`
4. Switch to new branch

### PR: `/git-workflow pr`
1. Run `git status` and check for uncommitted changes
2. Run `git log main..HEAD` to understand all commits
3. Run `git diff main...HEAD` for complete diff
4. Push branch if not pushed
5. Create PR with:
   - Short title (under 70 chars)
   - Summary section with 1-3 bullet points
   - Test plan checklist
6. Return PR URL

## Safety Rules
- NEVER force push to main/master
- NEVER commit .env, credentials, API keys, tokens
- NEVER amend published commits without explicit request
- NEVER skip pre-commit hooks (--no-verify)
- Always stage specific files, not everything
- Always verify branch before pushing
