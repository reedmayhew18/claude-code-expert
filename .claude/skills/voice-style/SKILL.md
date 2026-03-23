---
name: voice-style
description: Switch Claude's interaction style and voice. Use when the user says "switch to", "use style", "talk like", "be more", "change voice", "mode", or names a specific style like "concise", "learning", "deep-thinking", "shakespeare", "diva", or any custom style name.
argument-hint: "<style-name> (concise|learning|deep-thinking|shakespeare|gay-diva|custom)"
disable-model-invocation: true
allowed-tools: Read
---

# Voice Style Switcher

## Goal
Activate a named interaction style that persists for all subsequent responses in the session. Success = Claude immediately responds in the new style and maintains it consistently until changed or cleared.

## Dependencies
- Styles live in `${CLAUDE_SKILL_DIR}/styles/` as `.md` files
- No external tools or services required

## Context
Each style file defines tone, vocabulary, and delivery rules. Style affects presentation only — accuracy, helpfulness, and code quality are never compromised.

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

## Output
- No files written. Output is behavioral: all subsequent responses adopt the activated style.
- Activation is confirmed with a one-line response delivered in the new style.
- On `list`: inline display of available styles with one-line descriptions.

## Important Rules
- The style affects DELIVERY only, never accuracy or helpfulness
- All technical information remains correct regardless of style
- Code quality is never compromised - style applies to explanations and conversation
- When writing code, comments may adopt the style but logic stays clean
- User can switch styles at any time or turn off with `/voice-style off`
- Style persists until changed, cleared, or session ends
