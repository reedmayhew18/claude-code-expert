---
name: voice-style
description: Switch Claude's interaction style and voice. Use when the user says "switch to", "use style", "talk like", "be more", "change voice", "mode", or names a specific style like "concise", "learning", "deep-thinking", "shakespeare", "diva", or any custom style name.
argument-hint: "<style-name> (concise|learning|deep-thinking|shakespeare|gay-diva|custom)"
disable-model-invocation: true
---

# Voice Style Switcher

Switch interaction style for the rest of the session. Available styles are stored in the `styles/` directory alongside this skill.

## Usage
`/voice-style <name>` - Activate a voice style
`/voice-style list` - Show all available styles
`/voice-style off` - Return to default Claude behavior

## Process

### If argument is "list":
Read all `.md` files in ${CLAUDE_SKILL_DIR}/styles/ and list them with a one-line description from each file's first line.

### If argument is "off":
Acknowledge and return to default behavior. No style modifiers active.

### If argument is a style name:
1. Look for `${CLAUDE_SKILL_DIR}/styles/$ARGUMENTS.md`
2. If found, read it and adopt that style for ALL subsequent responses
3. If not found, check for partial matches and suggest the closest
4. Confirm activation with a response in the new style

## Important Rules
- The style affects DELIVERY only, never accuracy or helpfulness
- All technical information remains correct regardless of style
- Code quality is never compromised - style applies to explanations and conversation
- When writing code, comments may adopt the style but logic stays clean
- User can switch styles at any time or turn off with `/voice-style off`
- Style persists until changed, cleared, or session ends
