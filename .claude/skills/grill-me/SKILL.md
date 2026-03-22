---
name: grill-me
description: Deep interview to reach shared understanding before building. Use when starting a complex feature, when requirements are unclear, or when the user says "grill me", "interview me", "ask me questions", or "let's figure this out".
argument-hint: "[feature or idea to explore]"
---

# Grill Me - Design Tree Exploration

Interview the user relentlessly about every aspect of their plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one by one.

## Rules
1. If a question can be answered by exploring the codebase, explore the codebase instead of asking
2. Ask one focused question at a time, not batches
3. When a decision opens new branches (e.g., "advanced search" → filters, sorting, pagination), explore each branch
4. Don't accept vague answers - ask follow-ups until the answer is specific and implementable
5. Track decisions made so far to avoid re-asking

## Process

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

## Key Principle
The goal is NOT to ask a fixed list of questions. The goal is to dynamically explore every branch of the design tree until there are zero ambiguous decisions left. A simple feature might need 5 questions. A complex one might need 50.
