---
name: code-review
description: Review code changes for quality, security, and correctness. Use when the user says "review", "check my code", "look at these changes", or after implementing a feature.
argument-hint: "[file path, branch, or PR number]"
context: fork
agent: Explore
allowed-tools: Read, Grep, Glob, Bash(git *)
---

# Code Review

Review code changes systematically, organized by severity.

## Process

### Step 1: Identify Changes
- Run `git diff` (or `git diff main...HEAD` for branch review)
- Identify all modified files and understand the scope

### Step 2: Understand Context
- Read the modified files fully (not just the diff)
- Understand what the code is supposed to do
- Check for related test files

### Step 3: Review Checklist

**Critical (must fix before merge):**
- Security vulnerabilities (injection, XSS, exposed secrets, missing auth checks)
- Data loss risks (destructive operations without confirmation, missing transactions)
- Race conditions or concurrency issues
- Breaking changes to public APIs without migration path

**Warnings (should fix):**
- Missing error handling for external calls (network, file I/O, DB)
- Missing input validation at system boundaries
- Duplicated logic that should be shared
- Performance issues (N+1 queries, unnecessary allocations in loops)
- Missing or inadequate test coverage for new behavior

**Suggestions (nice to have):**
- Naming improvements for clarity
- Simplification opportunities
- Better patterns available in the framework

### Step 4: Report
For each finding:
1. **File and line reference**: `path/to/file.ts:42`
2. **What's wrong**: One sentence
3. **Why it matters**: Impact if not fixed
4. **How to fix**: Specific suggestion with code example

Organize findings by severity: Critical first, then Warnings, then Suggestions.

## What NOT to Flag
- Style issues handled by linters/formatters
- Opinions about code organization without concrete benefit
- "I would have done it differently" without a clear improvement
- Missing documentation on self-explanatory code
