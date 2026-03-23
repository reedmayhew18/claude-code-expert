---
name: git-workflow
description: Structured git workflow for commits, branches, and PRs. Use when the user says "commit", "create a PR", "new branch", "prepare for review", "ship this", or "push my changes". Safe, conventional git operations with checkpoints.
argument-hint: "[commit/pr/branch] [description]"
disable-model-invocation: true
allowed-tools: Bash
---

# Git Workflow

Safe, structured git operations with user checkpoints before irreversible actions.

## Goal
Ensure git operations are safe, conventional, and reviewable. Done = clean commit with proper message, correctly named branch, or PR opened with passing checks and the URL returned.

## Context
Read CLAUDE.md for branch naming conventions if documented. Check for `.github/pull_request_template.md` before drafting PR body.

## Commands

### Commit: `/git-workflow commit [message]`
1. Run `git status` and `git diff --staged` to understand changes
2. Check for sensitive files (.env, credentials, secrets) — WARN and exclude if found
3. Determine which files to stage (never `git add -A` or `git add .` — stage specific files)
4. If no message provided, draft one:
   - Prefix: feat/fix/refactor/docs/test/chore
   - Focus on WHY, not WHAT (the diff shows what)
   - Under 72 chars for subject line

**CHECKPOINT:** Present staged file list and draft commit message. Do NOT commit until user approves.

5. Create the commit

### Branch: `/git-workflow branch [name]`
1. Ensure clean working tree (warn if uncommitted changes)
2. Fetch latest from remote
3. Create branch from main/master with conventional name:
   - `feat/description`, `fix/description`, `refactor/description`
4. Switch to new branch
5. Confirm: "Created and switched to `branch-name`"

### PR: `/git-workflow pr`
1. Run `git status` — warn if uncommitted changes
2. Run `git log main..HEAD` to understand all commits on this branch
3. Run `git diff main...HEAD` for the complete diff
4. Draft PR with:
   - Short title (under 70 chars)
   - Summary section with 1-3 bullet points
   - Test plan checklist

**CHECKPOINT:** Show PR title, summary, and test plan. Do NOT push or create PR until user confirms.

5. Push branch with `-u` flag if not pushed
6. Create PR via `gh pr create`
7. Return the PR URL

## Output
- Commit: confirmation message with hash
- Branch: confirmation with branch name
- PR: the PR URL

## Safety Rules
- NEVER force push to main/master
- NEVER commit .env, credentials, API keys, tokens
- NEVER amend published commits without explicit request
- NEVER skip pre-commit hooks (--no-verify)
- Always stage specific files, not everything
- Always verify branch before pushing
