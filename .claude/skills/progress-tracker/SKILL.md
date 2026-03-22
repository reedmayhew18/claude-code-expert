---
name: progress-tracker
description: Create and update progress/handoff documents for long-running work. Use when nearing context limits, switching tasks, ending a session, or when the user says "save progress", "handoff", "wrap up", or "I need to pick this up later".
argument-hint: "[save/load/update]"
disable-model-invocation: true
---

# Progress Tracker

Maintain external state files that survive context resets, compaction, and session changes.

## Commands

### Save: `/progress-tracker save`
Create or update PROGRESS.md with:

```markdown
# Progress - [Date]

## Completed
- [x] Specific task with file paths
- [x] Another completed task

## In Progress
- [ ] Current task and its state
- Files being modified: path/to/file.ts

## Key Decisions Made
- Decision: [what was decided]
  - Reason: [why]
  - Impact: [what this means for other work]

## Known Issues / Landmines
- Issue description with file paths
- Workarounds currently in place

## Next Steps (in order)
1. Specific next action with file paths
2. Second action
3. Third action

## Context for Next Session
- Important state not captured elsewhere
- Relevant file paths and function names
- What you still don't understand (important!)
```

### Load: `/progress-tracker load`
Read PROGRESS.md and resume work from where we left off.

### Update: `/progress-tracker update`
Update the existing PROGRESS.md with current state without starting fresh.

## When to Use
- Before `/clear` - save state first
- Before context gets near capacity (check with `/context`)
- At end of work session
- Before switching to a different task
- After completing a major milestone

## Key Principle
Anything important that only exists in conversation will be lost on compaction. If it matters, it goes in a file.
