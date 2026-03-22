---
name: skill-creator
description: Create a new Claude Code skill with proper structure, frontmatter, and progressive disclosure. Use when the user says "create a skill", "make a skill", "new skill", or "I want to automate".
argument-hint: "[skill name or workflow description]"
disable-model-invocation: true
---

# Skill Creator

Build a properly structured Claude Code skill through guided interview.

## Process

### Step 1: Interview
Ask the user about:
1. **What does this skill do?** (workflow, convention, or capability)
2. **When should it activate?** (specific trigger phrases or slash-command only)
3. **Who invokes it?** (user manually, Claude automatically, or both)
4. **Does it need isolation?** (heavy operations → `context: fork`)
5. **What tools does it need?** (read-only? needs Bash? specific tools only?)
6. **Where should it live?** (personal `~/.claude/skills/` or project `.claude/skills/`)

### Step 2: Determine Skill Type

**Reference skill** (conventions, patterns):
```yaml
user-invocable: false
# Claude loads it automatically when relevant
```

**Task skill** (deploy, commit, generate):
```yaml
disable-model-invocation: true
# User triggers with /skill-name
```

**Hybrid skill** (default):
```yaml
# Both can invoke. Good for tools like code-review, explain-code
```

### Step 3: Write the Skill

**Directory structure:**
```
.claude/skills/<name>/
├── SKILL.md              # Required, under 500 lines (under 200 ideal)
├── references/            # Optional: detailed docs loaded on-demand
│   └── detailed-guide.md
├── examples/              # Optional: example outputs
│   └── sample.md
└── scripts/               # Optional: executable helpers
    └── validate.sh
```

**Frontmatter template:**
```yaml
---
name: kebab-case-name
description: What it does. When to use it. Include trigger phrases users would say.
argument-hint: "[expected-args]"
disable-model-invocation: true|false
user-invocable: true|false
allowed-tools: Tool1, Tool2
model: sonnet|opus|haiku|inherit
context: fork
agent: Explore|Plan|general-purpose
---
```

**Description rules:**
- MUST say both what it does AND when to use it
- Include 2-3 trigger phrases users would naturally say
- Mention relevant file types if applicable
- Keep under 1024 characters
- No XML angle brackets

**Content rules:**
- Keep SKILL.md under 500 lines (200 is ideal)
- Move detailed reference material to `references/` directory
- Reference supporting files: `See [references/guide.md](references/guide.md) for details`
- Use `$ARGUMENTS` for user input, `$0`, `$1` for positional args
- Use `!`command`` for dynamic context injection (shell commands that run before Claude sees the skill)
- Include "ultrathink" if the skill needs extended thinking

### Step 4: Test
1. Verify the skill appears: ask "What skills are available?"
2. Test auto-trigger by saying something that matches the description
3. Test manual trigger with `/skill-name`
4. Check that supporting files load correctly

### Step 5: Iterate
Common issues:
- **Skill not triggering**: Description doesn't match user language. Add more trigger phrases
- **Triggers too often**: Description too broad. Make it more specific or add `disable-model-invocation: true`
- **Too much context loaded**: Move detail to reference files. Keep SKILL.md lean
- **Skills crowding each other**: Check `/context` for budget warnings. Set `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var if needed
