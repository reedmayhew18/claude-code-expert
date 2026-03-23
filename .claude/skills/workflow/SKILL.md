---
name: workflow
description: Define and run multi-step workflows that chain skills, agents, and tasks together with state tracking. Use when the user says "workflow", "pipeline", "chain these steps", "run my pipeline", "define a workflow", "automate these steps", or has a task with more than 3 sequential steps.
argument-hint: "[define|run|list|status|resume] [workflow-name] [variables]"
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Workflow — Multi-Step Pipeline Orchestration

## Goal
Define, persist, and execute multi-step pipelines that survive context compaction and session restarts. Success = workflow runs to completion with each step's output saved to a file, checkpoints honored, and a final log written.

## Dependencies
- Tools: Read, Write, Edit, Glob, Grep, Bash
- No external services required; sub-skills and agents are invoked by name

## Context
Workflow definitions and state live in `.claude/workflows/`. Each run reads the definition file and an optional state file to enable resumption.

Define, run, and resume multi-step workflows that chain skills and agents together.

## Commands

### `/workflow define <name>`
1. Ask the user to describe the workflow in plain English
2. Break into numbered steps — each step is one of:
   - **Skill**: `/research`, `/wizard`, `/tdd`, etc.
   - **Agent**: `@code-reviewer`, `@debugger`, etc.
   - **Instruction**: plain text task for Claude
   - **Command**: bash command to execute
3. For each step, define: input source, output file, and whether it's a checkpoint
4. Save to `.claude/workflows/<name>.md`

### `/workflow run <name> [VAR=value ...]`
1. Read `.claude/workflows/<name>.md`
2. If `.claude/workflows/<name>-state.md` exists, ask: resume or start fresh?
3. For each step:
   - Announce: "**Step N: [name]** — [description]"
   - Execute with appropriate context (pass prior step output as file reference)
   - At **checkpoint** steps: present output, ask "Proceed, modify, or abort?"
   - On failure: save state, report clearly, stop
   - On success: mark step done in state file
4. On completion: write summary to `.claude/workflows/<name>-log.md`

### `/workflow list`
Show all workflows in `.claude/workflows/` with step count and last run date.

### `/workflow status <name>`
Show current state: which steps completed, which failed, what output was produced.

### `/workflow resume <name>`
Read state file, pick up from last incomplete step.

## Workflow Definition Format
```markdown
# Workflow: content-pipeline

## Description
Research a topic, plan content, write it, review, optimize for SEO.

## Steps
1. **research** — /research $TOPIC
   - Output: RESEARCH-$TOPIC.md
   - Checkpoint: false

2. **plan** — /plan-and-spec based on research
   - Input: RESEARCH-$TOPIC.md
   - Output: PLAN.md
   - Checkpoint: true

3. **write** — Write the article following PLAN.md
   - Input: PLAN.md, RESEARCH-$TOPIC.md
   - Output: drafts/$TOPIC.md
   - Checkpoint: true

4. **review** — @code-reviewer on the draft
   - Input: drafts/$TOPIC.md
   - Output: REVIEW.md
   - Checkpoint: false

5. **finalize** — Apply review feedback and optimize
   - Input: drafts/$TOPIC.md, REVIEW.md
   - Output: final/$TOPIC.md
   - Checkpoint: true

## Variables
- $TOPIC: Subject of the article

## On Failure
Pause and report: step name, input used, error. Do not skip.
```

## State File Format
```markdown
# State: content-pipeline (run 2026-03-23)
## Variables
TOPIC=Claude Code best practices

## Steps
- Step 1 research: COMPLETED — output: RESEARCH-claude-code.md
- Step 2 plan: COMPLETED — output: PLAN.md
- Step 3 write: IN_PROGRESS
- Step 4 review: PENDING
- Step 5 finalize: PENDING
```

## Design Principles
- **State in files**: Workflow state survives compaction and session restarts
- **Output as files**: Each step writes to a file path, not inline content (protects context)
- **Checkpoints are sacred**: Never skip a checkpoint without explicit user approval
- **Heavy steps fork**: For steps that produce large output, delegate to a subagent to protect main context
