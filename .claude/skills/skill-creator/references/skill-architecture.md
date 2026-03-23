# Skill Architecture Reference

When creating or improving a skill, ensure ALL of these architectural components are considered. Prompt the user about each one — don't assume they aren't needed.

## Full Skill Architecture

```
skill/
├── SKILL.md
│   ├── Name & Trigger
│   │   ├── skill-name
│   │   └── trigger-description (when should this activate?)
│   │
│   ├── Goal
│   │   └── desired-outcome (what does success look like?)
│   │
│   ├── Dependencies
│   │   ├── tools/ (what tools does this skill need?)
│   │   │   ├── allowed-tools in frontmatter
│   │   │   └── any CLI tools, libraries, or binaries required
│   │   └── connectors/ (what external connections?)
│   │       ├── MCP servers needed
│   │       ├── APIs called
│   │       └── services accessed
│   │
│   ├── Context (what background knowledge does the skill need?)
│   │   ├── brand-voice (if content/writing skill)
│   │   ├── icp-definition (if audience-targeted)
│   │   ├── codebase conventions (if code skill)
│   │   └── domain expertise (reference files)
│   │
│   ├── Process
│   │   ├── step-1
│   │   ├── step-2
│   │   ├── 🔴 human-checkpoint (user reviews/approves before continuing)
│   │   ├── step-3
│   │   ├── step-4
│   │   └── 🔴 human-checkpoint (user confirms final output)
│   │
│   └── Output
│       ├── save-location/ (where do results go?)
│       └── final-deliverable (what format? what file?)
│
├── references/ (progressive disclosure — loaded on demand)
├── scripts/ (executable helpers)
└── assets/ (templates, fonts, icons)
```

## Interview Checklist

When helping a user create a skill, walk through each of these:

### 1. Name & Trigger
- What should the skill be called? (kebab-case)
- What would a user say to trigger it? (list 3-5 natural phrases)
- Should Claude auto-trigger it, or manual `/name` only?
- Are there situations where it should NOT trigger? (negative triggers)

### 2. Goal
- What is the desired outcome when this skill runs?
- What does "done" look like? (specific deliverable, not vague)
- How would you know if it worked well vs poorly?

### 3. Dependencies
**Tools:**
- What Claude Code tools does it need? (Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch)
- Should tools be restricted? (e.g., read-only skill → `allowed-tools: Read, Grep, Glob`)
- Any CLI tools or binaries required? (e.g., `python`, `node`, `ffmpeg`, `pandoc`)
- Any Python packages needed? (e.g., `reportlab`, `openpyxl`, `peft`)

**Connectors:**
- Does it need MCP server access?
- Does it call external APIs?
- Does it interact with external services (GitHub, databases, etc.)?

### 4. Context
- Does it need brand voice or tone guidelines? → Reference a shared context folder
- Does it need audience/ICP information? → Reference persona documents
- Does it need codebase conventions? → Reference CLAUDE.md or rules files
- Does it need domain expertise? → Create reference files in `references/`
- How much context does it need loaded at once? (keep SKILL.md lean, heavy docs in references/)

### 5. Process
- What are the specific steps? (number them)
- **Where should human checkpoints go?** This is critical:
  - After planning/design decisions (before implementation)
  - After generating output (before saving/sending)
  - After any destructive or irreversible action
  - After any action visible to others (commits, messages, deployments)
- Mark checkpoints clearly: "**CHECKPOINT: Present to user for review before proceeding.**"
- Can any steps run in parallel? (subagent candidates)
- Should it run in a forked context? (`context: fork`)

### 6. Output
- What is the final deliverable? (file, message, PR, report, etc.)
- What format? (markdown, JSON, HTML, code file, document, etc.)
- Where should it be saved? (specific path pattern or ask user)
- Should it be presented to the user before saving?
- Does it need to be logged or tracked?

## Human Checkpoint Patterns

```markdown
## Step 2: Design the approach

[... skill designs something ...]

**CHECKPOINT:** Present the design to the user. Do NOT proceed until they approve.
Ask: "Here's the proposed approach. Want me to proceed, modify anything, or try a different direction?"
```

```markdown
## Step 4: Generate output

[... skill generates deliverable ...]

**CHECKPOINT:** Show the output to the user before saving.
Ask: "Here's what I've created. Should I save this, or would you like changes?"
```

## When to Use Each Frontmatter Field

| User's Answer | Frontmatter |
|---|---|
| "Only I should trigger this" | `disable-model-invocation: true` |
| "Claude should use it automatically" | (default, or `user-invocable: false` for background knowledge) |
| "It needs to run in isolation" | `context: fork` + `agent: Explore` or `general-purpose` |
| "It only needs to read, not write" | `allowed-tools: Read, Grep, Glob` |
| "It should use a specific model" | `model: opus` or `model: haiku` |
| "It needs maximum thinking" | Include "ultrathink" in content, or `effort: max` |

## Context Loading Strategy

Ask the user: "How much context does this skill need?"

| Amount | Strategy |
|---|---|
| Light (conventions, short rules) | Inline in SKILL.md |
| Medium (API docs, style guides) | Reference files in `references/` with pointers from SKILL.md |
| Heavy (full documentation, datasets) | Reference files + `context: fork` to isolate from main context |
| Dynamic (live data, current state) | Use `!`command`` injection to fetch at runtime |
