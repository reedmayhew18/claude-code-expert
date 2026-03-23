---
name: skill-catalog
description: Browse, install, and uninstall skills and agents from the available library. Check for new ones online. Use when the user says "what skills are available", "install skill", "add skill", "remove skill", "skill catalog", "list available", "check for updates", or wants to set up a project with specific capabilities.
argument-hint: "[list|install|uninstall|restore|update] [skill-or-agent-name]"
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Grep, Glob, WebFetch
---

# Skill & Agent Catalog

Browse and manage the available skills and agents library. Check GitHub for new additions.

## Commands

### `/skill-catalog list`
Read and display both index files:
- `available-skills/INDEX.md` - Skills not currently loaded
- `available-agents/INDEX.md` - Agents not currently loaded

Also show what's currently active:
- `.claude/skills/` - Currently loaded skills
- `.claude/agents/` - Currently loaded agents

### `/skill-catalog install <name>`
1. Check if `<name>` exists in `available-skills/` (folder) or `available-agents/` (file)
2. If not found locally, check GitHub (see Update section below) — it may be a newly added skill
3. Copy to `.claude/skills/<name>/` or `.claude/agents/<name>.md`
4. Confirm installation

To install into a DIFFERENT project:
1. Ask for the target project path
2. Copy to `<target>/.claude/skills/<name>/` or `<target>/.claude/agents/<name>.md`
3. Create `<target>/.claude/` directories if needed

### `/skill-catalog uninstall <name>`
1. Check if `<name>` is in active `.claude/skills/` or `.claude/agents/`
2. Confirm with user before removing
3. Move back to `available-skills/` or `available-agents/`
4. Do NOT uninstall core skills (project-init, wizard, tdd, code-review, refactor, context-doctor, skill-creator, grill-me, git-workflow, plan-and-spec, progress-tracker, voice-style, voice-creator, skill-catalog, research, existing-project, new-project)

### `/skill-catalog restore <name>`
Restore a customized skill or agent back to its original version.

1. Check if the skill/agent's `description:` field ends with `(Customized)`
2. If not customized, report: "This skill hasn't been customized — nothing to restore."
3. If customized, fetch the original from GitHub:
   - Skills: `WebFetch https://raw.githubusercontent.com/reedmayhew18/claude-code-expert/main/.claude/skills/<name>/SKILL.md`
   - If not found there, try: `WebFetch https://raw.githubusercontent.com/reedmayhew18/claude-code-expert/main/available-skills/<name>/SKILL.md`
   - Agents: `WebFetch https://raw.githubusercontent.com/reedmayhew18/claude-code-expert/main/.claude/agents/<name>.md`
   - If not found there, try: `WebFetch https://raw.githubusercontent.com/reedmayhew18/claude-code-expert/main/available-agents/<name>.md`
4. Show the user a diff between their customized version and the original
5. If they confirm, replace with the original
6. If the fetch fails, report: "Couldn't reach GitHub to get the original. Check your connection."

### `/skill-catalog restore all`
Scan all skills and agents for descriptions ending in `(Customized)`. List them and offer to restore each one individually or all at once.

### `/skill-catalog customize <name>`
Customize a specific skill or agent for the current project.

1. Read the skill's SKILL.md or agent's .md file
2. Read the project's CLAUDE.md, package.json/pyproject.toml, and README to understand the tech stack and conventions
3. Rewrite the skill's description and instructions to reference the project's specific:
   - Test runner and test commands
   - Build system and commands
   - Linter/formatter
   - Framework conventions
   - Branch naming and PR conventions
4. Add project-specific examples where applicable
5. Append ` (Customized)` to the `description:` field if not already present
6. Show the user the changes before saving
7. Save on confirmation

### `/skill-catalog customize`
No name specified — interactive mode:

1. List ALL installed skills and agents with numbers:
   ```
   Installed Skills:
     1. wizard - 8-phase production implementation
     2. tdd - Strict red-green-refactor TDD
     3. code-review - Isolated code review (Customized)
     ...

   Installed Agents:
     14. code-reviewer - Reviews changes by severity
     15. debugger - Root cause analysis
     ...
   ```
2. Skills already marked `(Customized)` show that tag so the user knows
3. Ask: "Enter the numbers of skills/agents to customize (e.g. `1, 2, 5` or `all`):"
4. For each selected, run the customize process above
5. Read the project context ONCE at the start, then apply to all selected — don't re-read for each

### `/skill-catalog customize all`
Customize every installed skill and agent for the current project. Same as selecting all numbers above.

### `/skill-catalog update`
Check GitHub for new or updated skills and agents.

**Process:**
1. Fetch the latest INDEX files from GitHub:
   ```
   WebFetch https://raw.githubusercontent.com/reedmayhew18/claude-code-expert/main/available-skills/INDEX.md
   WebFetch https://raw.githubusercontent.com/reedmayhew18/claude-code-expert/main/available-agents/INDEX.md
   ```

2. Compare with local INDEX files — identify:
   - **New entries**: skills/agents on GitHub that don't exist locally
   - **Updated entries**: descriptions that differ (indicates the skill was improved)

3. For each new/updated item, show the user:
   - Name and description
   - Whether it's new or updated
   - Ask if they want to download it

4. For items the user wants:
   - **Skills**: Fetch the SKILL.md:
     ```
     WebFetch https://raw.githubusercontent.com/reedmayhew18/claude-code-expert/main/available-skills/<name>/SKILL.md
     ```
     Save to `available-skills/<name>/SKILL.md`
     Also check for supporting files (references/, scripts/) by fetching:
     ```
     WebFetch https://api.github.com/repos/reedmayhew18/claude-code-expert/contents/available-skills/<name>
     ```
     This returns a directory listing. Download any files found.

   - **Agents**: Fetch the agent file:
     ```
     WebFetch https://raw.githubusercontent.com/reedmayhew18/claude-code-expert/main/available-agents/<name>.md
     ```
     Save to `available-agents/<name>.md`

5. Update local INDEX.md files with any new entries

6. Also check for new reference guides:
   ```
   WebFetch https://api.github.com/repos/reedmayhew18/claude-code-expert/contents/reference
   ```
   Compare with local `reference/` — offer to download any new guides.

7. Report what was found and what was downloaded.

**If the fetch fails** (no internet, repo not found, etc.):
- Don't error out — just report "Couldn't reach GitHub. Your local library is still available."
- Show the local catalog as normal.

### `/skill-catalog setup`
Interactive project setup:
1. Ask what kind of project (web, Python, API, content, etc.)
2. Recommend relevant skills and agents from the library
3. Install selected ones to the target project
4. Optionally run `/project-init` to create CLAUDE.md

## GitHub Repository
- **Repo**: `https://github.com/reedmayhew18/claude-code-expert`
- **Raw content base**: `https://raw.githubusercontent.com/reedmayhew18/claude-code-expert/main/`
- **API base**: `https://api.github.com/repos/reedmayhew18/claude-code-expert/contents/`

New skills and agents are added to the GitHub repo regularly. Run `/skill-catalog update` to check for additions.

## Notes
- Installing a skill/agent here makes it active for the current project
- For other projects, specify the target path
- Core skills cannot be uninstalled (they're the Claude Code expertise foundation)
- Available libraries are at project root: `available-skills/` and `available-agents/`
- GitHub updates are additive only — they never modify or remove your existing local files
