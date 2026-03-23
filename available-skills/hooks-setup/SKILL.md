---
name: hooks-setup
description: Configure Claude Code hooks for automatic formatting, safety guards, compaction recovery, and session management. Use when the user says "set up hooks", "auto-format", "block dangerous commands", "configure automation", "safety rules", or wants deterministic automation.
argument-hint: "[auto-format|safety|compaction-recovery|session|all]"
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob
---

# Hooks Configuration

Interactive setup of Claude Code hooks — deterministic automation that runs without AI reasoning tokens.

## Categories

### `auto-format` — Format code after every edit
PostToolUse on Edit/Write. Detects language from file extension, runs appropriate formatter.
- Python: `ruff format`
- JS/TS: `prettier --write`
- Go: `gofmt -w`

### `safety` — Block destructive commands
PreToolUse on Bash. Blocks: `rm -rf /`, `rm -rf ~`, `git push --force main`, `DROP TABLE`, `DROP DATABASE`, `--break-system-packages`.

### `compaction-recovery` — Re-inject context after compaction
SessionStart on compact. Creates `.claude/context-essentials.md` with critical project context, echoes it after compaction so Claude stays oriented.

### `session` — Session start/end management
- SessionStart: loads recent git log + PROGRESS.md head
- Stop: reminds to run `/wrap-up`

## Process

### Step 1: Detect Current State
- Read `.claude/settings.json` (if exists)
- Report what hooks are currently configured
- Ask: which categories to configure?

### Step 2: Configure Selected Categories
For each category, generate the hook JSON. Show the user exactly what will be added.

### Step 3: Merge Carefully
- Read existing `.claude/settings.json`
- Merge new hooks WITHOUT destroying existing configuration
- **CHECKPOINT:** Show full resulting settings.json before writing
- Never overwrite hooks the user already has

### Step 4: Context Essentials (if compaction-recovery selected)
Walk user through creating `.claude/context-essentials.md`:
- Project description (1 line)
- 3-5 hard rules
- Current focus/task
- Key file paths

This file gets echoed into context after every compaction, keeping Claude oriented.
