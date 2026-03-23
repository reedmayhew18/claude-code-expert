---
name: wrap-up
description: End-of-session retrospective that captures accomplishments, learnings, and decisions to project memory. Use when the user says "wrap up", "end session", "what did we do", "save what we learned", "session summary", "I'm done for now", or when context is approaching capacity.
argument-hint: "[quick|full|decisions-only]"
disable-model-invocation: true
---

# Session Wrap-Up

Capture what happened this session so future sessions start smarter.

## Modes
- **`/wrap-up quick`** — What was done, what's next. 2 minutes.
- **`/wrap-up`** (full, default) — Accomplishments, what worked, what didn't, decisions, next steps.
- **`/wrap-up decisions-only`** — Just extract and record key decisions made.

## Process

### Step 1: Reconstruct the Session
- Check `git diff` and `git log` for what changed
- Look for PLAN.md, PROGRESS.md, or HANDOFF.md created/modified this session
- Scan which files were touched

### Step 2: Quick Interview
Ask the user (skip Q2-Q4 in quick mode):
1. "What's the most important thing we accomplished?"
2. "What worked really well?" (a tool, pattern, or approach)
3. "What was frustrating or took longer than it should?"
4. "Any decisions made that future-you needs to remember?"
5. "What's the single most important next step?"

### Step 3: Generate Files

**PROGRESS.md** (upsert — merge with existing):
```markdown
# Progress

## Session [date]
### Accomplished
- [x] Specific task with file paths

### Next Steps
1. Most important next action
2. Second action
```

**`.claude/memory/LEARNINGS.md`** (append-only, never overwrite previous entries):
```markdown
## Session [date]
### Patterns That Work
- [approach] — context: [when this applies]
### Anti-Patterns Found
- [thing to avoid] — because: [why]
### Domain Knowledge
- [fact discovered] — source: [where from]
```

**`.claude/memory/DECISIONS.md`** (append-only):
```markdown
## [date] — [decision title]
- **Decision**: What was decided
- **Reason**: Why
- **Alternatives rejected**: What else was considered
- **Impact**: What this affects
```

Skip LEARNINGS.md and DECISIONS.md in quick mode. Always write PROGRESS.md.

### Step 4: Checkpoint
**Show all files to user before writing.** They confirm, edit, or skip any.

### Step 5: Context Hygiene
After writing:
- If context near capacity: "Session captured. `/clear` for a fresh start?"
- If open plan exists: "Should I update PLAN.md with today's progress?"
- If decisions affect CLAUDE.md: "You decided [X] — should this go in CLAUDE.md as a rule?"
