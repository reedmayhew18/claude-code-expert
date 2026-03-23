---
name: grill-me
description: Deep interview to reach shared understanding before building. Use when starting a complex feature, when requirements are unclear, or when the user says "grill me", "interview me", "ask me questions", "let's figure this out", or "grill me lightly" for a quick version.
argument-hint: "[lightly] [feature or idea to explore]"
---

# Grill Me - Design Tree Exploration

Interview the user about their plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one by one.

## Modes

### Full Mode (default): `/grill-me [topic]`
Relentless, thorough interview. Explores every branch of the design tree until zero ambiguity remains. Use for complex features, architecture decisions, or anything where getting it wrong is expensive.

### Light Mode: `/grill-me lightly [topic]`
Quick, focused interview — 5-8 questions max. Gets the essential decisions made without deep-diving every branch. Use for quick setups, small features, or when the user just needs to fill in a few gaps. Skip edge cases and failure modes unless they're critical. Aim for "good enough to start" not "perfectly specified."

## Pre-Fill: Check the Codebase First

**Before asking ANY questions**, check if you're in an existing project:

1. Look for: CLAUDE.md, README.md, package.json, pyproject.toml, Cargo.toml, go.mod, Makefile, Dockerfile, src/, tests/
2. If an existing project is found:
   - Read CLAUDE.md, README, and config files to understand the project
   - Identify: tech stack, architecture, conventions, existing patterns
   - Note what you already know and what's still unclear
   - **Only ask about the gaps** — don't ask questions the codebase already answers
   - Start by saying: "I've looked at your project. Here's what I understand: [summary]. Let me ask about what I'm less sure about..."
3. If no project exists (empty directory or new project):
   - Start from scratch with the full interview

## Rules
1. If a question can be answered by exploring the codebase, explore the codebase instead of asking
2. Ask one focused question at a time, not batches
3. When a decision opens new branches (e.g., "advanced search" → filters, sorting, pagination), explore each branch (full mode) or note it for later (light mode)
4. Don't accept vague answers — ask follow-ups until the answer is specific and implementable
5. Track decisions made so far to avoid re-asking

## Process (Full Mode)

### Phase 1: Big Picture
- What is the user trying to build?
- Who is it for?
- What does success look like?

### Phase 2: Design Tree
For each major component:
- What are the options?
- What are the tradeoffs?
- Which option fits the constraints?
- What does this decision imply for other decisions?

### Phase 3: Edge Cases & Failure Modes
- What happens when things go wrong?
- What are the performance constraints?
- What are the security considerations?
- What data validation is needed?

### Phase 4: Synthesis
After all questions are answered:
1. Summarize all decisions made
2. Highlight any tensions or tradeoffs
3. Propose a concrete implementation plan
4. Ask if anything was missed

## Process (Light Mode)

### Phase 1: Quick Context
- What are you building? (one sentence)
- What's the most important thing it needs to do?
- Any hard constraints? (tech stack, timeline, platform)

### Phase 2: Key Decisions Only
- Ask about the 3-5 biggest decisions that would block progress
- Skip theoretical edge cases — focus on "what do I need to know to start building?"

### Phase 3: Quick Summary
1. Summarize decisions in bullet points
2. Note anything deferred for later
3. Recommend next step (usually `/wizard` or `/plan-and-spec`)

## Key Principle
The goal is NOT to ask a fixed list of questions. The goal is to dynamically explore the design tree until the level of clarity matches the mode: **Full mode = zero ambiguity. Light mode = enough to start.**
