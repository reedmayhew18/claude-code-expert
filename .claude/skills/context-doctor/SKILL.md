---
name: context-doctor
description: Diagnose and fix context window issues. Use when Claude seems confused, forgetful, slow, or the user says "context is full", "you forgot", "you're repeating yourself", "start fresh", or "why are you ignoring my instructions".
disable-model-invocation: true
---

# Context Window Doctor

Diagnose context issues and recommend the right fix.

## Diagnosis

### Check Current State
Run `/context` to see what's consuming the context window.

### Common Symptoms & Fixes

**Symptom: Claude ignores CLAUDE.md rules**
- Cause: CLAUDE.md too long (attention diluted) or rules contradictory
- Fix: Trim CLAUDE.md under 200 lines. Use emphasis on critical rules. Move detail to `.claude/rules/` files or `@imports`

**Symptom: Claude forgets earlier instructions**
- Cause: Context filled with tool outputs, compaction dropped details
- Fix: Write critical info to files (PLAN.md, PROGRESS.md). These survive compaction. Then `/compact` with focus instructions: `/compact preserve the implementation plan and all file paths`

**Symptom: Claude repeats itself or goes in circles**
- Cause: Context polluted with failed approaches
- Fix: After 2 failed corrections, `/clear` and rewrite the prompt incorporating what you learned

**Symptom: Responses are slow or degraded**
- Cause: Context near capacity (>60% is the caution zone)
- Fix: `/clear` if switching tasks. `/compact` with focus if continuing. Use subagents for verbose operations (tests, research)

**Symptom: Unrelated context polluting current work**
- Cause: Kitchen-sink session (mixed tasks)
- Fix: `/clear` between unrelated tasks. Always.

**Symptom: Lost progress after compaction**
- Cause: Important state was only in conversation, not in files
- Fix: Before reaching capacity, dump state to files:
  - `PROGRESS.md` - what's done, what's next
  - `PLAN.md` - current plan
  - `HANDOFF.md` - full context transfer document

## Prevention Strategies

1. **Document & Clear**: Dump progress to file → `/clear` → start fresh reading that file
2. **Use subagents**: Delegate verbose ops (test runs, research, log analysis) to subagents
3. **One task per session**: `/clear` between unrelated work
4. **External state**: Plans, specs, progress in files (not just conversation)
5. **Proactive compaction**: `/compact [focus]` before auto-compact triggers (auto triggers at ~95% and is less controlled)
6. **Lean CLAUDE.md**: Under 200 lines. Progressive disclosure for the rest.

## Emergency Reset
If context is badly polluted:
1. Write current state to HANDOFF.md: progress, decisions, next steps, file paths
2. `/clear`
3. Start fresh: "Read HANDOFF.md and continue from where we left off"
