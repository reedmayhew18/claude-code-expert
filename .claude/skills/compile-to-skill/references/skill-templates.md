# Skill Templates

Template fragments for generating compiled skills. The translate.py script and Claude use these as building blocks.

## Frontmatter Template

```yaml
---
name: {skill_name}
description: >
  {what_it_does}. Use when user says "{trigger_phrase_1}",
  "{trigger_phrase_2}", or "{trigger_phrase_3}".
argument-hint: "{argument_description}"
allowed-tools: {tool_list}
---
```

### Tool Selection Guide

| Skill Needs | Tools |
|-------------|-------|
| Read-only analysis | Read, Grep, Glob |
| File generation | Read, Write, Edit, Glob |
| Runs bundled scripts | Read, Write, Edit, Bash, Glob |
| Web access needed | Read, Write, Bash, WebSearch, WebFetch |
| Full capability | Read, Write, Edit, Bash, Grep, Glob |

## Body Templates

### Template: Mostly Prose (Decision Logic Skill)

```markdown
# {Skill Name}

{One paragraph: what this skill does and when to use it.}

## Input

$ARGUMENTS should be: {description of expected input}.

If no arguments provided, ask: "{prompt for user input}"

## Process

### Step 1: {First Decision Point}

{Translated decision logic as natural language}

**If {condition A}:**
1. {action}
2. {action}

**If {condition B}:**
1. {action}
2. {action}

**Otherwise:**
{default action}

### Step 2: {Next Step}

{More translated logic}

### Step 3: Present Results

{Output formatting instructions}

## Reference Data

{Baked-in tables, constants, lookup data — or pointer to references/ file}

## Error Handling

- If {error condition}: {what to tell the user}
- If {error condition}: {what to tell the user}
```

### Template: Thin Orchestrator (Script-Heavy Skill)

Use this ONLY when scripts are truly unavoidable (precision math, crypto, complex algorithms).

```markdown
# {Skill Name}

{One paragraph: what this skill does.}

## Input

$ARGUMENTS: {description}

## Process

### Step 1: Validate Input

{Prose instructions for input validation — this should NOT be a script}

### Step 2: Compute

Run the computation:
```bash
python ${CLAUDE_SKILL_DIR}/scripts/{script_name}.py {args}
```

The script outputs: {description of output format}

### Step 3: Present Results

{Prose instructions for formatting and presenting the script's output to the user}

## Error Handling

- If the script exits with an error: {what to tell the user}
```

### Template: Data Transformer

```markdown
# {Skill Name}

Transforms {input format} into {output format}.

## Input

$ARGUMENTS: path to the input file, or paste {format} data directly.

### If file path provided:
Read the file using the Read tool.

### If data pasted inline:
Use the pasted data directly.

## Transformation Rules

{Translated transformation logic as numbered rules:}

1. For each {record/row/item}:
   - Extract {field} from {location}
   - Transform: {rule in plain English}
   - Map {source value} → {target value} using this table:

| Source | Target |
|--------|--------|
| {val}  | {val}  |
| {val}  | {val}  |

2. {Additional transformation rules}

## Output

Write the result to {output location} in {format}.

Present a summary: "{X} records transformed, {Y} warnings."
```

### Template: Validator/Checker

```markdown
# {Skill Name}

Validates {what} against {rules/standards}.

## Input

$ARGUMENTS: {what to validate — file path, data, URL, etc.}

## Validation Rules

Check each of the following. Report all failures, don't stop at the first one.

### Rule 1: {Rule Name}
{Plain English description of what to check}
- **Pass**: {what passing looks like}
- **Fail**: {what failing looks like and what to tell the user}

### Rule 2: {Rule Name}
{Same structure}

### Rule 3: {Rule Name}
{Same structure}

## Output

Present results as a checklist:
- [x] {Rule Name} — passed
- [ ] {Rule Name} — FAILED: {specific issue}

If all rules pass: "{Congratulations message}"
If any fail: "Found {N} issues. {Summary of what to fix}"
```

### Template: Interactive Workflow

```markdown
# {Skill Name}

Guides the user through {process}.

## Input

$ARGUMENTS: {optional starting context}

## Workflow

### Step 1: Gather Information

Ask the user:
1. "{Question 1}"
2. "{Question 2}"
3. "{Question 3}"

### Step 2: {Process Step}

Based on the user's answers:
{Translated decision logic}

**CHECKPOINT:** Present the plan to the user before proceeding.
"Here's what I'll do: {summary}. Does this look right?"

### Step 3: Execute

{Action steps}

### Step 4: Verify

{Verification instructions}

Present the result and ask: "Does this look correct? Any adjustments?"
```

## Prose Translation Patterns

### Pattern: If/Elif/Else Chain → Bulleted Conditions

**Code:**
```python
if status == "active":
    return process_active(data)
elif status == "pending":
    return queue_for_review(data)
elif status == "expired":
    return archive(data)
else:
    return flag_unknown(data)
```

**Prose:**
```markdown
Based on the status:
- **Active**: Process the data immediately
- **Pending**: Queue it for review — tell the user it will be reviewed
- **Expired**: Archive it — move to the completed section
- **Unknown status**: Flag it and ask the user what to do
```

### Pattern: Loop → "For Each" Instruction

**Code:**
```python
results = []
for item in items:
    if item.is_valid():
        results.append(transform(item))
```

**Prose:**
```markdown
Go through each item:
1. Check if it's valid (has all required fields, values within range)
2. If valid: transform it by {transformation description}
3. If invalid: skip it and note it in the warnings
Collect all transformed items.
```

### Pattern: Try/Except → "If Something Goes Wrong"

**Code:**
```python
try:
    result = risky_operation()
except FileNotFoundError:
    print("File not found")
except PermissionError:
    print("No permission")
```

**Prose:**
```markdown
Attempt {the operation}. If it fails:
- **File not found**: Tell the user the file doesn't exist and ask for the correct path
- **Permission denied**: Tell the user they don't have access and suggest checking permissions
```

### Pattern: State Machine → Numbered Phases

**Code:**
```python
state = "init"
while state != "done":
    if state == "init":
        state = "collecting"
    elif state == "collecting":
        if has_enough:
            state = "processing"
    elif state == "processing":
        state = "done"
```

**Prose:**
```markdown
This is a multi-phase process:

**Phase 1 — Initialize**: Set up the workspace and gather requirements.

**Phase 2 — Collect**: Gather data until sufficient. 
Check: "Do we have enough data?" If not, continue collecting.

**Phase 3 — Process**: Transform the collected data.

When processing is complete, present the results.
```
