---
name: plan-and-spec
description: Create a structured implementation plan with spec-driven modeling. Use when starting a new feature, complex refactor, or when the user says "plan this", "spec this out", "design this", or "how should we build this". Forces multiple design iterations before coding.
argument-hint: "[feature or task description]"
---

# Spec-Driven Planning

Create a thorough implementation plan that survives context compaction and prevents the "first idea that works" trap.

## Process

### Phase 1: Understand & Clarify
1. Read relevant code, CLAUDE.md, and any existing specs
2. State your assumptions explicitly
3. Ask the user targeted questions about:
   - Technical constraints and requirements
   - Edge cases and failure modes
   - Integration points with existing code
   - Success criteria (what does "done" look like?)
   - Non-functional requirements (performance, security, etc.)

Do NOT proceed until assumptions are validated.

### Phase 2: Initial Design
Draft a plan covering:
- **Objective**: What we're building and why (1-2 sentences)
- **Approach**: High-level strategy
- **Files to modify/create**: Specific paths
- **Dependencies**: What this touches
- **Testing strategy**: How we verify correctness
- **Risks**: What could go wrong

### Phase 3: Critique the Design
Evaluate your own plan against:
- **Simplicity**: Is there a simpler approach? Are you over-engineering?
- **Testability**: Can each piece be tested independently?
- **Hand-wavy gaps**: Any steps that say "handle edge cases" without specifics?
- **Unverified assumptions**: Did you grep to confirm methods/APIs exist?
- **Failure modes**: What happens when things go wrong?

### Phase 4: Generate Alternative
Address the specific weaknesses from Phase 3:
- If too complex → simpler architecture
- If untestable → different decomposition
- If gaps exist → fill them with specifics

### Phase 5: Iterate
Repeat Phases 3-4 at least twice more. Present the best elements from all iterations.

### Phase 6: Final Plan
Cherry-pick the best elements into a final plan. Write it to a file (PLAN.md or TECHSPEC.md) so it survives context compaction.

## Plan File Format

```markdown
# [Feature Name] Plan

## Objective
What we're building and why.

## Success Criteria
- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2

## Approach
High-level strategy.

## Implementation Steps
1. Step with specific file paths and function names
2. Each step is atomic and testable

## Testing Strategy
How each piece gets verified.

## Risks & Mitigations
Known risks and how we handle them.

## Open Questions
Anything unresolved.
```

## Key Principles
- Plans go in files, not just conversation (they survive compaction)
- Grep to verify before assuming methods/APIs exist
- Every step should be atomic enough to implement and test independently
- Include specific file paths and function names, not vague descriptions
- Define success criteria BEFORE implementation to prevent moving goalposts
