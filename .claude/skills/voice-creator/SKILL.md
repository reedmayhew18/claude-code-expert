---
name: voice-creator
description: Create a custom voice/interaction style template. Use when the user says "create a voice", "make a style", "new personality", "custom voice", "I want Claude to talk like", or provides examples of a writing style they want to replicate.
argument-hint: "[style name or description]"
disable-model-invocation: true
allowed-tools: Read, Write, Glob
---

# Voice Style Creator

## Goal

Produce a saved voice style file at `.claude/skills/voice-style/styles/<name>.md` that captures a distinct personality with enough specificity (rules + examples) that Claude reliably adopts it when `/voice-style <name>` is invoked.

## Dependencies

- **Tools:** Read, Write, Glob
- **Existing styles:** Check `.claude/skills/voice-style/styles/` to avoid naming collisions and to use as format reference

## Context

- Review one existing style file in `.claude/skills/voice-style/styles/` before writing to match the established format
- No external APIs or MCP servers required

## Process

### Step 1: Gather Input
Ask the user for ONE of the following (in order of preference):

**Option A - Text Examples (best results):**
"Paste 2-3 examples of the style you want. These can be your own writing, excerpts from someone you admire, chat messages, tweets, anything that captures the vibe."

**Option B - Description:**
"Describe the personality, tone, and energy you want. Think about: How formal? How much personality? Any specific words/phrases? Who does this voice sound like?"

**Option C - Reference Person/Character:**
"Name a person, character, or archetype and I'll build a style based on their communication patterns."

### Step 2: Analyze the Style
From the input, extract:
- **Tone**: Formal/casual/playful/serious/warm/sharp
- **Energy level**: Calm/moderate/high/chaotic
- **Vocabulary patterns**: Specific words, slang, jargon, phrases
- **Sentence structure**: Short and punchy? Long and flowing? Questions? Fragments?
- **Emoji usage**: None/minimal/moderate/generous
- **Humor style**: None/dry/sarcastic/goofy/witty
- **Signature moves**: Catchphrases, opening patterns, closing patterns
- **What they NEVER do**: Equally important as what they do

**CHECKPOINT:** Present the style analysis to the user before writing the template. Ask: "Here's what I've extracted from your input. Does this capture the voice correctly, or should I adjust any of these attributes before writing the template?"

### Step 3: Write the Template
Create a style file following this structure:

```markdown
[Style Name] Mode - [One-line description of the vibe]

## Rules
1. **[Core trait]:** [Detailed description with examples]
2. **[Language pattern]:** [Specific vocabulary, phrases, structures]
3. **[Energy/tone]:** [How to modulate intensity]
4. **[Emoji/formatting]:** [Visual style rules]
5. **[Supportive behavior]:** [How to respond to user emotions]
6. **[Boundaries]:** [What this style NEVER does]
7. **Still helpful:** [Reminder that accuracy isn't compromised]

## Examples

**[Common scenario 1]:**
"[Example response in this style]"

**[Common scenario 2]:**
"[Example response in this style]"

**[Common scenario 3]:**
"[Example response in this style]"
```

**CHECKPOINT:** Show the completed template to the user before saving. Ask: "Here's the full voice template. Should I save this as-is, or would you like to tweak anything first?"

### Step 4: Save and Test
1. Save to `.claude/skills/voice-style/styles/<name>.md`
2. Demonstrate the style with a sample response
3. Ask user for feedback and iterate

### Key Principles
- **6-8 rules maximum.** More than that and the style gets diluted.
- **Specific over vague.** "Use words like X, Y, Z" beats "be casual."
- **Include examples.** The model learns more from examples than rules.
- **Include anti-examples.** What does this voice NEVER sound like?
- **Test with technical content.** Make sure the style works for code explanations, not just conversation.

## Output

- **Save location:** `.claude/skills/voice-style/styles/<name>.md`
- **Format:** Markdown with a Rules section (6-8 numbered rules) and an Examples section (3+ scenarios)
- **Activation:** User can invoke with `/voice-style <name>` after saving
