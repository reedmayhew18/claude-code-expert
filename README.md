<div align="center">

# 🧠 Claude Code Expert

### The Ultimate Claude Code Toolkit

[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-blueviolet?style=for-the-badge&logo=anthropic)](https://claude.ai/code)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue?style=for-the-badge)](LICENSE)

[![Skills](https://img.shields.io/badge/Skills-19%20active%20·%2024%20available-0078D4?style=flat-square)](https://github.com/reedmayhew18/claude-code-expert/tree/main/.claude/skills)
[![Agents](https://img.shields.io/badge/Agents-16%20specialized-E86C00?style=flat-square)](https://github.com/reedmayhew18/claude-code-expert/tree/main/.claude/agents)
[![Voice Styles](https://img.shields.io/badge/Voice%20Styles-9%20built--in-ff69b4?style=flat-square)](#-voice-styles-9-built-in)
[![Reference](https://img.shields.io/badge/Reference%20Guides-8%20·%207%2C752%20lines-2ea44f?style=flat-square)](https://github.com/reedmayhew18/claude-code-expert/tree/main/reference)
[![Sources](https://img.shields.io/badge/Sources%20Analyzed-104-FFD700?style=flat-square)](#-how-it-was-built)
[![Size](https://img.shields.io/badge/Total%20Size-692KB-lightgrey?style=flat-square)](#)

**43 skills · 16 agents · 9 voice styles · 8 reference guides**
**Built by Claude Code after analyzing 104 resources**

Drop it into any project. Start a new one from scratch. Or just clone it and ask questions.<br>
Use Claude Code like the experts — without the hours of research, videos, and tutorials.<br>
**Just clone, launch, and go.**

</div>

---

## 🚀 Get Started in 60 Seconds

**First, install Claude Code** (if you haven't already):

```bash
# macOS / Linux / WSL
curl -fsSL https://claude.ai/install.sh | bash
```

```powershell
# Windows (PowerShell)
winget install Anthropic.ClaudeCode
```

**Then clone and launch:**

```bash
git clone https://github.com/reedmayhew18/claude-code-expert.git
cd claude-code-expert
claude
```

Then pick your path:

| You want to... | Run this |
|---|---|
| 🆕 Start a brand new project | `/new-project` |
| 📦 Add the toolkit to an existing project | `/existing-project /path/to/your/project` |
| 🧠 Just ask Claude Code questions as an expert | Start typing — the knowledge base is loaded |

That's it. `/new-project` interviews you about what you're building, then creates a fully configured project folder with a tailored CLAUDE.md, selected skills, agents, and the full reference library. `/existing-project` does the same thing non-destructively for a codebase you already have.

---

## 📦 What's Inside

### 🛠️ Skills (19 active + 24 available)

Skills are reusable workflows that Claude loads automatically when relevant, or that you trigger with `/skill-name`.

#### Project Setup & Management
| Skill | What it does |
|---|---|
| `/new-project` | Create a fully configured new project from scratch |
| `/existing-project` | Add the toolkit to a project that already exists |
| `/project-init` | Bootstrap a lean, optimized CLAUDE.md for any codebase |
| `/progress-tracker` | Save/load/update progress files that survive context resets |
| `/context-doctor` | Diagnose and fix context window issues when Claude gets confused |

#### Core Workflow
| Skill | What it does |
|---|---|
| `/wizard` | 8-phase production implementation: plan, explore, test-first, implement, verify, document, adversarial review, quality gate |
| `/plan-and-spec` | Spec-driven planning that forces multiple design iterations before coding |
| `/tdd` | Strict red-green-refactor test-driven development |
| `/code-review` | Isolated code review running in a dedicated subagent |
| `/refactor` | Safe refactoring with characterization tests as a safety net |
| `/grill-me` | Deep interview that walks every branch of the design tree until zero ambiguity remains |
| `/research` | Structured web research with source evaluation and synthesis |
| `/git-workflow` | Structured commits, branches, and PRs with safety checks |

#### Meta Skills
| Skill | What it does |
|---|---|
| `/skill-creator` | Guided skill creation with proper structure and progressive disclosure |
| `/skill-store` | Browse, install, and uninstall skills and agents from the available library |
| `/voice-style` | Switch interaction styles mid-session |
| `/voice-creator` | Create custom voice styles from examples or descriptions |

#### 📚 Available Library

Install with `/skill-store install <name>` — or auto-installed when creating new projects.

**Document Formats:** `docx` · `pdf` · `pptx` · `xlsx`
**General:** `brainstorm` · `deploy-checklist` · `doc-coauthoring` · `project-optimizer` · `python-scaffold` · `seo-content` · `web-starter`
**Creative:** `algorithmic-art` · `canvas-design` · `slack-gif-creator` · `theme-factory` · `web-artifacts-builder`
**Developer:** `mcp-builder` · `webapp-testing`
**ML/AI:** `pytorch-training-loop` · `torch-optimize` · `hf-finetune` · `unsloth-finetune` · `model-export` · `training-infra`

**`/project-optimizer`** does a deep read-only scan of your entire project — code, tests, CI/CD, documentation, Claude Code setup — and produces a prioritized report of improvements. Auto-installed in every new project.

🔄 **Check for new skills anytime:** `/skill-store update` pulls the latest from this GitHub repo. Additive only — never touches your existing files.

---

### 🎭 Voice Styles (9 built-in)

Switch how Claude talks to you. The code quality stays the same — only the delivery changes.

```
/voice-style concise          # Maximum signal, minimum words
/voice-style learning         # Teach while completing, extra comments in code
/voice-style deep-thinking    # Think out loud, show reasoning, create THINKING.md
/voice-style shakespeare      # Elizabethan drama meets software engineering
/voice-style gay-diva         # Fabulous, flamboyant, and unapologetically extra 💅✨
/voice-style pirate           # Code on the high seas, matey
/voice-style zen-master       # Calm, philosophical, minimalist wisdom
/voice-style sports-announcer # Every deployment is the championship game
/voice-style gen-z            # lowkey the best coding assistant ngl 💀
```

Want your own? `/voice-creator` builds a custom style from text examples, descriptions, or a reference person.

---

### 🤖 Agents (5 active + 11 available)

Specialized AI personas that Claude delegates to automatically. Each runs in its own context window.

#### Always Active
| Agent | Model | Role |
|---|---|---|
| `code-reviewer` | Sonnet | Reviews changes by severity: critical, warnings, suggestions |
| `debugger` | Sonnet | Root cause analysis with systematic hypothesis testing |
| `researcher` | Haiku | Fast codebase exploration and context gathering |
| `python-expert` | Sonnet | Python development with modern conventions |
| `skill-architect` | Opus | Expert on building and optimizing Claude Code skills |

#### Available Library
`brainstormer` · `brand-voice-expert` · `creative-writer` (Opus) · `fullstack-dev` · `product-designer` (Opus) · `seo-expert` · `web-designer` (Opus) · `neural-architect` (Opus) · `pytorch-dev` · `hf-ml-engineer` · `ml-trainer`

Install any with `/skill-store install <name>`.

---

### 📖 Reference Library (8 guides · 7,752 lines)

Comprehensive guides synthesized from 104 sources. Claude reads on demand — zero context cost until needed.

| Guide | Coverage |
|---|---|
| `01-official-docs.md` | Complete Anthropic documentation: skills, agents, hooks, memory, remote control, monitoring, plugins |
| `02-best-practices.md` | Production-tested patterns: prompting, planning, TDD, context management, costs |
| `03-skills-and-agents.md` | Definitive guide to building skills, agents, and agent teams |
| `04-context-and-memory.md` | CLAUDE.md optimization, compaction strategies, progressive disclosure, project memory |
| `05-workflows-and-automation.md` | Loop command, CI/CD, remote control, hooks, the Ralph Loop, refactoring at scale |
| `06-guides-and-tutorials.md` | Learning progression from first session to Level 7 autonomous pipelines |
| `07-brand-and-content-skills.md` | Content automation, brand voice architecture, shared context patterns |
| `08-cross-platform-environments.md` | macOS, Windows, WSL, Linux: shell differences, Python venv, package managers, gotchas |

Every project created with `/new-project` or `/existing-project` gets these automatically.

---

### 🔒 MCP Security Warning

This toolkit includes a built-in safety mechanism for MCP servers. If a third-party (non-local) MCP server is detected, Claude issues an explicit security warning explaining exactly what MCP servers can access — your code, files, credentials, and conversation — and requires acknowledgment before proceeding. Local servers (localhost, private IPs) pass without warning.

Too many people install dozens of third-party MCP servers based on YouTube recommendations without understanding there is no sandbox between an MCP server and your entire session. We fix that.

---

## 🏗️ How It Was Built

This project was built by Claude Code (Opus 4.6) in a single session using a Level 7 autonomous pipeline:

1. **104 reference files** were collected — official Anthropic documentation, community guides, Reddit discussions, production team reports, GitHub repositories, video tutorial transcripts, and blog posts
2. **10 broken files** were identified and removed (Cloudflare blocks, Vercel security checkpoints, paywalled content)
3. **6 parallel Sonnet agents** rewrote all 104 raw web scrapes into 7 clean, comprehensive reference guides — deduplicating content, stripping navigation cruft, merging overlapping sources, and organizing with proper structure
4. **Skills were designed** based on patterns extracted from the research: the wizard methodology, the grill-me pattern, spec-driven planning, progressive disclosure, context management strategies
5. **Agents were created** with appropriate model tiers: Opus for complex creative/architectural work, Sonnet for daily development tasks, Haiku for fast research
6. **Voice styles were built** as a modular system with a creator skill for extensibility
7. **The active/available split** keeps context lean — only 24% of the skill description budget is used, leaving room for growth
8. **Cross-platform environment guide** prevents common Claude Code mistakes (like `--break-system-packages` on Ubuntu)

The entire toolkit is **692KB**. Every project created from it inherits the full knowledge base at zero context cost.

<details>
<summary><strong>Does Claude actually believe this is the best solution?</strong></summary>

<br>

Yes. After reading 104 resources covering every aspect of Claude Code — from Anthropic's own documentation to production reports from teams running 1,000+ ML experiments per day — this toolkit implements every best practice, pattern, and optimization strategy discovered in the research. The CLAUDE.md is lean (166 lines, well under the 200-line threshold). The skill budget uses 24% of capacity. The reference library is comprehensive but loads on demand. The active/available split prevents context bloat while keeping everything accessible.

It's not perfect — nothing is. But it's built on the most thorough analysis of Claude Code's capabilities and limitations that exists in one place.

</details>

---

## 🗂️ Project Structure

```
claude-code-expert/
├── CLAUDE.md                     # Project brain (166 lines, optimized)
├── README.md                     # You are here
├── reference/                    # 8 expert guides (7,752 lines)
├── .claude/
│   ├── skills/                   # 19 active skills
│   │   └── voice-style/styles/   # 9 voice templates
│   ├── agents/                   # 5 active agents
│   └── memory/                   # Project-local memory
├── available-skills/             # 24 installable skills
└── available-agents/             # 11 installable agents
```

---

## 🤝 Contributing

The `available-skills/` and `available-agents/` directories are designed to grow. If you've built a skill or agent that would be useful to others, open a PR. Follow the patterns in the existing files — frontmatter, description with trigger phrases, progressive disclosure.

**More skills, agents, and voice styles coming soon.**

---

## 📄 License

AGPL v3 — see [LICENSE](LICENSE)

---

<div align="center">

*Built with Claude Code. Optimized by Claude Code. For Claude Code.* ✨

</div>
