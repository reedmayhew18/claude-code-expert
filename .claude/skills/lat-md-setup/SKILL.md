---
name: lat-md-setup
description: >
  Set up lat.md knowledge graph for a project. lat.md replaces flat AGENTS.md/CLAUDE.md
  with an interconnected, validated graph of markdown docs linked to source code.
  Use when user says "set up lat.md", "install lat.md", "add knowledge graph",
  "lat md", "agent lattice", or wants structured, validated project documentation
  that stays in sync with code. Also triggered via "lat-md-setup checklist" to
  return just the recommendation checklist.
argument-hint: "[project path] or 'checklist'"
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# lat.md Setup

Set up [lat.md](https://github.com/1st1/lat.md) — a knowledge graph that structures codebase knowledge into interlinked, validated markdown documents. Created by Yury Selivanov (Python core developer, async/await author, Gel/EdgeDB co-founder, Vercel Director of Engineering).

## What lat.md Does

Instead of one flat CLAUDE.md or AGENTS.md, lat.md creates a `lat.md/` directory of interconnected markdown files where:
- Sections link to each other with `[[wiki-link]]` syntax
- Markdown links into source code symbols: `[[src/auth.ts#validateToken]]`
- Source code links back with `// @lat: [[auth#OAuth Flow]]` comments
- `lat check` validates all links stay in sync (runs in CI, pre-commit, or by agents)
- `lat search` does semantic search across all sections
- `lat expand` injects referenced content inline into prompts

It complements Claude Code skills — skills provide general capabilities, lat.md provides project-specific domain knowledge.

---

## Input Handling

### If `$ARGUMENTS` is "checklist":
Read and present `${CLAUDE_SKILL_DIR}/references/recommendation-checklist.md` to the user. This is used by other skills (new-project, existing-project) to quickly determine if lat.md is recommended. Return just the checklist — do not proceed with setup.

### If `$ARGUMENTS` is a project path:
Use that as the target project directory.

### If `$ARGUMENTS` is empty:
Ask: "Which project should I set up lat.md for? Give me a path, or say 'here' for the current directory."

---

## Phase 1: Check Prerequisites

1. Check if Node.js is available:
   ```bash
   node --version
   ```
   If not installed, tell the user: "lat.md requires Node.js. Install it first, then re-run this skill."

2. Check if lat.md is already set up:
   ```bash
   ls <target>/lat.md/ 2>/dev/null
   ```
   If `lat.md/` already exists, ask: "This project already has a lat.md directory. Want me to check its health with `lat check`, or start fresh?"

3. Check if the `lat.md` npm package is available:
   ```bash
   npx lat.md@latest --help 2>/dev/null
   ```
   If this fails, we'll install it during setup.

---

## Phase 2: Analyze the Project

Read the project to understand its structure, similar to what existing-project does:
- Languages and frameworks used
- Source directory structure
- Existing CLAUDE.md, AGENTS.md, or .cursorrules
- Key architectural patterns
- Test structure
- Number of source files and approximate LOC

This informs what lat.md documents to create.

---

## Phase 3: Design the Knowledge Graph

Based on the project analysis, propose an initial set of lat.md documents. Common patterns:

**For most projects:**
```
lat.md/
├── architecture.md     # System design, key decisions, data flow
├── conventions.md      # Coding standards, naming, patterns
└── testing.md          # Test strategy, specs (require-code-mention: true)
```

**For web applications, add:**
```
├── api.md              # API endpoints, auth, error handling
├── frontend.md         # Component patterns, state management
└── deployment.md       # Infrastructure, CI/CD, environments
```

**For ML/data projects, add:**
```
├── models.md           # Model architecture, training, evaluation
├── data-pipeline.md    # Data flow, transformations, schemas
└── experiments.md      # Experiment tracking, hyperparameters
```

**For libraries/packages, add:**
```
├── public-api.md       # Public interface, versioning, deprecation
└── internals.md        # Internal architecture, extension points
```

**CHECKPOINT:** Present the proposed graph structure to the user:
"Based on your project, here's the knowledge graph I'd create: [structure]. Want to add, remove, or rename any documents?"

Wait for approval before proceeding.

---

## Phase 4: Initialize lat.md

Run the initialization:

```bash
cd <target-project> && npx lat.md@latest init
```

This creates the `lat.md/` directory and configures the user's coding agent (Claude Code, Codex, Cursor, etc.) with hooks and instructions.

If `lat init` configures agent hooks automatically, review what it added and explain to the user what changed.

---

## Phase 5: Create the Knowledge Documents

For each document in the approved graph structure:

1. **Read the relevant source code** to understand what should be documented
2. **Write the lat.md document** with:
   - Clear section headings (these become wiki-link targets)
   - `[[wiki-links]]` between related sections across documents
   - `[[src/path/to/file.ts#symbolName]]` links to key source code symbols
   - `require-code-mention: true` frontmatter on test spec sections
3. **Add `@lat:` backlink comments** in source code files that reference the specs:
   - Python: `# @lat: [[testing#Unit Test Strategy]]`
   - JavaScript/TypeScript: `// @lat: [[architecture#Request Pipeline]]`
   - Rust/Go/C: appropriate comment syntax

### Writing Quality Guidelines

Each lat.md document should capture:
- **Design decisions and WHY** — not just what the code does, but why it was built this way
- **Constraints and invariants** — things that must always be true
- **Domain knowledge** — business logic that isn't obvious from code alone
- **Cross-cutting concerns** — how different parts of the system interact

Keep sections focused. A section should cover one concept. Link to related concepts in other files rather than duplicating.

**CHECKPOINT:** After writing the first 1-2 documents, show them to the user:
"Here's what the architecture document looks like. Does this capture the right level of detail? Too much? Too little?"

---

## Phase 6: Validate

Run validation to ensure everything links correctly:

```bash
cd <target-project> && npx lat.md@latest check
```

Fix any broken links, missing references, or unlinked `require-code-mention` sections.

---

## Phase 7: Configure CI Integration (Optional)

Offer: "Want me to add `lat check` to your CI pipeline so links stay validated on every PR?"

If yes, detect the CI system and add appropriately:

**GitHub Actions** — add to `.github/workflows/`:
```yaml
- name: Validate lat.md knowledge graph
  run: npx lat.md@latest check
```

**Pre-commit hook** — add to `.claude/settings.json` or `.pre-commit-config.yaml`:
```bash
npx lat.md@latest check
```

---

## Phase 8: Update CLAUDE.md

Add a section to the project's CLAUDE.md noting that lat.md is in use:

```markdown
## Knowledge Graph (lat.md)

This project uses [lat.md](https://github.com/1st1/lat.md) for structured documentation.
- Browse: `lat.md/` directory
- Search: `lat search "query"` or `lat locate "section name"`
- Validate: `lat check` (also runs in CI)
- When modifying code, update the corresponding lat.md sections
- Add `@lat:` backlink comments when implementing spec sections
```

Ask before modifying CLAUDE.md.

---

## Phase 9: Present Summary

Show the user what was created:

```
## lat.md Setup Complete

**Knowledge Graph:**
- [N] documents created in lat.md/
- [N] wiki-links connecting sections
- [N] source code references
- [N] backlink annotations added to source

**Documents:**
- architecture.md — [brief description]
- conventions.md — [brief description]
- testing.md — [brief description, note require-code-mention sections]

**Validation:** `lat check` passes ✓
**CI:** [configured / not configured]

**Next steps:**
- Run `lat search "topic"` to navigate the graph
- When you modify code, update the relevant lat.md sections
- Add `@lat:` comments in source files that implement specs
- Run `lat check` periodically to catch drift
```
