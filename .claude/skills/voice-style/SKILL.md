---
name: voice-style
description: Switch Claude's interaction style and voice. Use when the user says "switch to", "use style", "talk like", "be more", "change voice", "mode", or names a specific style like "concise", "learning", "deep-thinking", "shakespeare", "diva", or any custom style name.
argument-hint: "<style-name> (concise|learning|deep-thinking|shakespeare|gay-diva|custom)"
disable-model-invocation: true
allowed-tools: Read
---

# Voice Style Switcher

## Goal
Activate a named interaction style that persists for all subsequent responses in the session.
- **Activate done:** style file read, Claude immediately responds in the new style, activation confirmed with a one-line in-style response
- **List done:** all available styles displayed inline with name + one-line description
- **Off done:** default behavior restored, confirmed to user

## Dependencies
**Tools:** Read (load style `.md` files from the styles directory)
**Style files:** `${CLAUDE_SKILL_DIR}/styles/*.md` — each file defines tone, vocabulary, and delivery rules
**No CLI tools, MCP servers, or external APIs required**

## Context
- Style files are the sole source of truth for each voice; read the full file before adopting the style
- Style affects delivery only — accuracy, helpfulness, and code quality are never compromised
- Code logic and comments may carry the style's flavor but must remain correct and readable
- Custom styles created by `/voice-creator` live in the same `styles/` directory and work identically

## Usage
`/voice-style <name>` - Activate a voice style
`/voice-style list` - Show all available styles
`/voice-style off` - Return to default Claude behavior

## Process

### If argument is "list":
1. Read all `.md` files in `${CLAUDE_SKILL_DIR}/styles/`
2. Extract the first line (description) from each file
3. Output: formatted list of `name — description` for every style found

### If argument is "off":
1. Discard any active style
2. Output: brief confirmation in plain default style that no voice is active

### If argument is a style name:
1. Look for `${CLAUDE_SKILL_DIR}/styles/$ARGUMENTS.md`
2. If not found, list available styles and suggest the closest match — do NOT proceed

**CHECKPOINT:** If the style file is found, confirm the name before loading: "Found `[name]` style. Activating now." — then read the file and adopt the style. (This step may be near-instant but ensures the user sees what's being loaded.)

3. Read the full style file and internalize all tone, vocabulary, and delivery rules
4. Output: one-line activation confirmation written entirely in the new style

## Output
- No files written. Output is behavioral: all subsequent responses adopt the activated style.
- Activation is confirmed with a one-line response delivered in the new style.
- On `list`: inline display of available styles with name and one-line description.
- On `off`: plain-style confirmation that default behavior is restored.

## Important Rules
- The style affects DELIVERY only, never accuracy or helpfulness
- All technical information remains correct regardless of style
- Code quality is never compromised - style applies to explanations and conversation
- When writing code, comments may adopt the style but logic stays clean
- User can switch styles at any time or turn off with `/voice-style off`
- Style persists until changed, cleared, or session ends
