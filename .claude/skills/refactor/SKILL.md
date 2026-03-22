---
name: refactor
description: Safely refactor code with characterization tests and incremental changes. Use when the user says "refactor", "clean up", "extract", "rename", "restructure", or needs to modernize legacy code.
argument-hint: "[file, module, or description of what to refactor]"
---

# Safe Refactoring

Refactor code incrementally with test coverage as a safety net.

## Process

### Step 1: Characterize Current Behavior
Before changing anything:
1. Read the code to understand what it does
2. Check existing test coverage
3. If coverage is insufficient, write **characterization tests** that capture current behavior:
   - Focus on inputs → outputs for public functions
   - Include edge cases the code currently handles
   - These tests document "what the code does now", not "what it should do"
4. Run tests to confirm they pass

### Step 2: Plan the Refactoring
Break the refactoring into small, independent steps. Each step should:
- Be completable in one change
- Keep tests passing after the change
- Be easy to review in isolation

Common refactoring sequences:
- **Extract**: Identify code to extract → write test for it → extract → verify
- **Rename**: Find all references → rename → verify no breakage
- **Restructure**: Map dependencies → move in dependency order → verify each move
- **Simplify**: Identify dead code → verify it's unused → remove → verify

### Step 3: Execute Incrementally
For each step:
1. Make the change
2. Run the relevant tests
3. If tests fail: fix or revert before proceeding
4. If tests pass: move to next step

NEVER batch multiple refactoring steps. One logical change at a time.

### Step 4: Verify
After all steps:
1. Run the full test suite
2. Compare behavior: does the refactored code produce identical results?
3. Review the total diff for anything unexpected

## Hard Rules
- NEVER change behavior during refactoring (that's a feature change, not a refactor)
- NEVER skip test verification between steps
- If existing tests are insufficient, write characterization tests FIRST
- Preserve original function signatures as wrappers initially when extracting (remove wrappers in a separate step)
- When renaming across many files, use your editor's rename symbol feature or search-and-replace, not manual edits

## Legacy Code Strategy
For large legacy codebases:
1. Spend initial effort on characterization tests (not refactoring)
2. Create module-specific CLAUDE.md files documenting gotchas
3. Use handoff documents (PROGRESS.md) between sessions
4. Target 25-30k tokens per session; use `/clear` between modules
