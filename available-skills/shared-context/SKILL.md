---
name: shared-context
description: Set up a centralized shared context folder for your project with brand voice, audience personas, and domain knowledge. Use when the user says "set up brand context", "create voice profile", "define our audience", "shared context", "ICP setup", or wants consistent non-generic output across skills.
argument-hint: "[brand|domain|full]"
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep
---

# Shared Context Setup

Create a centralized context folder that all skills and agents reference for consistent output.

## Modes
- **`brand`** — Voice profile, tone, banned words, audience personas, content pillars
- **`domain`** — Project conventions, terminology glossary, domain knowledge
- **`full`** (default) — Both brand and domain

## Process

### Step 1: Assess What Exists
- Check for `.claude/shared-context/`, `.claude/brand-context/`, or existing voice/persona files
- Read CLAUDE.md, README, any marketing or docs directories
- Report what's found and what's missing

### Step 2: Interview

**Brand questions** (skip in domain mode):
1. Brand personality in 3 adjectives?
2. Primary audience: job title, pain points, language they use?
3. Words/phrases to NEVER use? (AI artifacts, competitor names, off-brand jargon)
4. Platform differences? (LinkedIn vs docs vs email vs social)
5. Share 1-2 examples of content you're proud of

**Domain questions** (skip in brand mode):
1. Project domain? (fintech, healthcare, e-commerce, etc.)
2. Project-specific terminology that's often misused?
3. Non-obvious conventions from reading the code?
4. Who consumes this project's output? (engineers, end users, both)

### Step 3: Create Structure
```
.claude/shared-context/
├── README.md               # What this folder is, how to use it
├── brand/
│   ├── voice-profile.md    # Tone, banned words, platform rules, examples
│   ├── audience-personas.md # ICP with pain points and values
│   └── content-pillars.md  # Core topics (content projects only)
└── domain/
    ├── conventions.md       # Project-specific rules and gotchas
    └── glossary.md         # Domain terminology
```

**CHECKPOINT:** Show each document before writing. User confirms or edits.

### Step 4: Wire Into Skills
- Scan `.claude/skills/` for writing/content skills
- Offer to add `Read .claude/shared-context/brand/voice-profile.md before generating content` to relevant skills

### Step 5: Register in CLAUDE.md
Add:
```markdown
## Shared Context
Brand voice, audience personas, and domain conventions: `.claude/shared-context/`
Content-generating skills should read relevant files before producing output.
```
