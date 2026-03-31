# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

A Claude Code expertise toolkit: knowledge base, portable skills, specialized agents, and voice styles. Usable as a standalone expert system or as a foundation for any new project.

## Project Structure

```
reference/                          # Claude Code expertise library
├── 01-official-docs.md             # Anthropic documentation
├── 02-best-practices.md            # Production-tested patterns
├── 03-skills-and-agents.md         # Skill/agent creation guide
├── 04-context-and-memory.md        # Context management mastery
├── 05-workflows-and-automation.md  # Hooks, CI/CD, loops
├── 06-guides-and-tutorials.md      # Beginner to expert progression
├── 07-brand-and-content-skills.md  # Content automation
└── 08-cross-platform-environments.md  # macOS/Windows/WSL/Linux setup

.claude/
├── skills/                         # Active skills (always loaded)
│   ├── project-init/               # Bootstrap Claude Code for any project
│   ├── plan-and-spec/              # Spec-driven planning with iteration
│   ├── tdd/                        # Red-green-refactor TDD
│   ├── code-review/                # Isolated review via Explore agent
│   ├── refactor/                   # Safe refactoring with char tests
│   ├── context-doctor/             # Fix context window issues
│   ├── compile-to-skill/           # Transpile code into markdown skills
│   ├── lat-md-setup/               # Set up lat.md knowledge graph
│   ├── skill-creator/              # Guided skill creation
│   ├── skill-store/              # Browse/install available skills+agents
│   ├── grill-me/                   # Deep interview before building
│   ├── git-workflow/               # Structured commits, branches, PRs
│   ├── wizard/                     # 8-phase production implementation
│   ├── progress-tracker/           # State persistence across sessions
│   ├── voice-style/                # Switch interaction styles (9 voices)
│   ├── voice-creator/              # Create custom voice templates
│   ├── research/                   # Structured web research
│   ├── new-project/                # Create & configure a new project
│   └── existing-project/           # Add toolkit to existing project
├── agents/                         # Active agents
│   ├── code-reviewer.md            # Code review (sonnet)
│   ├── debugger.md                 # Root cause analysis (sonnet)
│   ├── researcher.md               # Codebase exploration (haiku)
│   ├── python-expert.md            # Python development (sonnet)
│   └── skill-architect.md          # Skill creation expert (opus)
└── memory/                         # Project-local persistent memory

available-skills/                   # Skill library (install with /skill-store)
├── INDEX.md                        # One-line descriptions
├── brainstorm/                     # Structured ideation
├── deploy-checklist/               # Pre-deployment verification
├── python-scaffold/                # Scaffold Python projects
├── seo-content/                    # SEO-optimized content
└── web-scaffold/                   # Scaffold web projects

available-agents/                   # Agent library (install with /skill-store)
├── INDEX.md                        # One-line descriptions
├── brainstormer.md                 # Creative ideation (sonnet)
├── brand-voice-expert.md           # Brand voice (sonnet)
├── creative-writer.md              # Content/copy (opus)
├── fullstack-dev.md                # JS/TS full-stack (sonnet)
├── product-designer.md             # PRDs/specs (opus)
├── seo-expert.md                   # Search optimization (sonnet)
└── web-designer.md                 # Frontend/UI/UX (opus)
```

## How to Use

### Quick Start
- `/skill-store list` - See all available skills and agents
- `/skill-store install <name>` - Install a skill or agent
- `/project-init` - Bootstrap Claude Code in a new project
- `/wizard` - 8-phase production implementation
- `/voice-style gay-diva` - Switch voice (9 styles available)

### As a Knowledge Base
Ask about Claude Code features, patterns, or best practices. Start with `reference/`.

### Setting Up a New Project
1. `/skill-store setup` - Interactive: recommends skills/agents for your project type
2. `/project-init [path]` - Creates tailored CLAUDE.md
3. Skills and agents copy directly into the target project's `.claude/` folder

### Voice Styles
`/voice-style <name>` to switch. Available: concise, learning, deep-thinking, shakespeare, gay-diva, pirate, zen-master, sports-announcer. `/voice-creator` to make custom ones.

## Claude Code Quick Reference

### Key Commands
| Command | Action |
|---------|--------|
| `Shift+Tab` | Cycle: default > acceptEdits > plan mode |
| `/compact [focus]` | Compress context with optional focus |
| `/context` | See what's consuming context |
| `/clear` | Fresh context (use between unrelated tasks) |
| `Ctrl+B` | Background a running task |
| `Esc Esc` | Undo last change |

### Context Management
1. Context window is the fundamental constraint - everything competes for space
2. Auto-compaction at ~95% - CLAUDE.md survives, conversation doesn't
3. Subagents isolate verbose ops from main context
4. `/clear` between unrelated tasks
5. Persist state in files (PLAN.md, PROGRESS.md) - they survive compaction
6. Active skills load descriptions only (~100 tokens each)

### Skill Format
```yaml
---
name: kebab-case-name
description: What + when. Include trigger phrases.
disable-model-invocation: true    # Manual /name only
context: fork                     # Isolated subagent
allowed-tools: Read, Grep         # Tool restrictions
---
Instructions. $ARGUMENTS for input. !`cmd` for dynamic injection.
```

### Agent Format (.claude/agents/name.md)
```yaml
---
name: agent-name
description: When to delegate
tools: Read, Grep, Glob, Bash
model: sonnet|opus|haiku
skills: [preloaded-skill-names]
memory: project
---
System prompt here.
```

## Project Rules

### MCP Server Security Warning (IMPORTANT)
If the user has MCP servers configured, or asks to add one, you MUST check whether the server URL is a **local address** (localhost, 127.0.0.1, 0.0.0.0, 192.168.x.x, 10.x.x.x, or a unix socket). Local MCP servers built by the user are acceptable without warning.

For ANY non-local/third-party MCP server, you MUST issue this warning and get explicit acknowledgment before proceeding:

> **SECURITY WARNING: Third-Party MCP Server Detected**
>
> MCP servers have FULL ACCESS to your conversation, code, files, and tool outputs. A third-party MCP server can:
> - Read every file Claude accesses in your project (source code, secrets, configs)
> - Intercept and modify tool inputs/outputs (inject code, alter commands)
> - Exfiltrate data to external servers without your knowledge
> - Inject malicious instructions into Claude's context (prompt injection)
> - Access any credentials or API keys visible in your environment
>
> This is not theoretical. There is no sandbox between MCP servers and your session. Everything Claude sees, the MCP server sees.
>
> **Do NOT install MCP servers because a YouTuber or blog post recommended them unless you have personally reviewed the server's source code and understand exactly what it does.**
>
> To proceed, you must confirm: "I understand the risks and accept responsibility for this MCP server."

If the user confirms, note in CLAUDE.md or project memory: `MCP risk acknowledged by user on [date] for server: [name]`. Do not ask again for the same server.

If the user has NOT confirmed, do NOT configure, suggest, or help set up the MCP server. Offer to help them build their own local alternative instead.

### File Boundaries
Only edit files within this project directory. Exception: `/new-project` creates folders in the parent directory - this is intentional.

### Model Usage
Sonnet for subagents by default. Haiku for simple file ops. Opus for complex creative/architectural work.

### Python Environments
NEVER use `--break-system-packages`. Always use virtual environments (venv, uv, conda). See `reference/08-cross-platform-environments.md`.
