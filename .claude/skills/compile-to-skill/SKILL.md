---
name: compile-to-skill
description: >
  Transpile source code into Claude Code markdown skills. Takes Python, JavaScript,
  TypeScript, C++, Rust, Go, or any terminal-based program and converts it into an
  LLM-executable markdown skill. Analyzes code structure, fuzzes runtime behavior,
  classifies operations, and generates a complete skill directory with SKILL.md,
  bundled scripts, and reference docs. Use when user says "compile to skill",
  "convert this code to a skill", "make a skill from this script", "turn this into
  a skill", "transpile to skill", or wants to translate any traditional program into
  Claude Code's markdown skill format. Also use when user pastes code and asks to
  make it work as a Claude skill.
argument-hint: "<path-to-source-file or paste code inline>"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# CompileToSkill

A transpiler that converts traditional source code into Claude Code markdown skills.

The core idea: analyze what code does, then express it as a mix of prose instructions (for Claude's reasoning), bundled scripts (for deterministic computation), baked-in data (pre-computed values), and Claude-simulated operations (things Claude handles natively).

## Input Handling

Determine the input source:

### If `$ARGUMENTS` is a file path:
1. Read the file at the given path
2. Detect language from extension (`.py`, `.js`, `.ts`, `.cpp`, `.rs`, `.go`, etc.)

### If `$ARGUMENTS` is empty or not a valid path:
1. Check if the user pasted code inline in the conversation
2. Ask what language it is if not obvious
3. Save the code to a temporary file: `/tmp/compile-to-skill-input.<ext>`

### If no code is available:
Ask: "Please provide source code — either paste it here or give me a file path."

---

## Phase 1: Parse & Analyze (Static Analysis)

Run the static analyzer:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/analyze.py <source-file>
```

This extracts:
- Language identification
- Functions, classes, entry points
- Control flow (loops, conditionals, state machines)
- I/O patterns (stdin/stdout, file I/O, network, database)
- External dependencies and imports
- Constants, enums, configuration values

Review the analysis output. Then also read the source code yourself and form your own understanding of what the program does. The script catches structure; you catch intent.

### Rejection Check
If the code involves any of these, warn the user and offer alternatives:
- **GUI frameworks** (tkinter, Qt, GTK, Electron): "This code has a graphical interface. Skills are text/terminal only. I can compile the backend logic — want me to strip the GUI layer?"
- **Real-time systems** (game loops, audio processing): "Real-time code can't translate to a skill. I can compile the logic/configuration parts."
- **Hardware access** (GPIO, USB, serial): "Hardware-dependent code needs the actual hardware. I can compile the data processing parts."

**CHECKPOINT:** Present the analysis summary to the user:
- "Here's what I found in the code: [summary]. Does this look right? Anything I'm missing about what this code does?"

Wait for user confirmation before proceeding.

---

## Phase 2: Deep Fuzz & Profile (Dynamic Analysis)

Run the deep fuzzer to understand runtime behavior:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/fuzz.py <source-file> --depth deep
```

The fuzzer will:
- Generate type-aware inputs (ints, floats, strings, edge values like 0, -1, MAX_INT, empty string, None)
- Execute the code with each input set and capture outputs
- Discover boundary conditions that trigger different code paths
- Map the full output range (all possible output formats, values, error messages)
- Find edge cases: crashes, exceptions, infinite loops (with timeout protection)
- Track approximate code path coverage

For **compiled languages** (C, C++, Rust, Go): the fuzzer attempts to compile first. If compilation fails, it reports the error and falls back to static-only analysis.

For **languages without a runtime** (or if execution is unsafe): skip fuzzing and note in the compilation report that dynamic analysis was not performed.

Review the fuzz results. Pay attention to:
- **Output patterns**: Are outputs predictable? Could they be baked into a lookup table?
- **Error conditions**: What makes the code fail? These become guard clauses in the skill.
- **Performance**: Is anything slow enough that it must stay as a script vs. being simulated?

---

## Phase 3: Classify Operations

This is the intellectual heart of the compilation. For each significant operation in the code, decide which strategy to use.

Run the classifier for initial heuristic-based classification:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/classify.py <source-file> --analysis <analysis.json> --fuzz-results <fuzz-results.json>
```

Then review and refine the classifications using your own judgment. Read `${CLAUDE_SKILL_DIR}/references/classification-guide.md` for detailed heuristics.

### The Four Strategies

**1. Bake In** — Pre-compute and embed in the skill
- Constants, lookup tables, enums, configuration
- Small output sets that are fully enumerable
- Static mappings (e.g., state abbreviations, error code meanings)
- Embed directly in SKILL.md or in `references/` files

**2. Script** — Keep as executable code in `scripts/` (USE SPARINGLY)
- Floating-point precision math that Claude would get wrong
- Cryptographic operations
- Complex regex with many edge cases that can't be taught by example
- Algorithms where correctness is critical and output space is huge (>50 variations)
- ONLY use when Prose/Simulate/Bake In genuinely can't handle it

**3. Prose** — Translate to natural language instructions
- Decision trees and business logic ("if the user is an admin, then...")
- Workflow steps ("first validate, then process, then output")
- Heuristic judgments ("choose the best match based on...")
- Conditional branching on semantic conditions
- Error handling strategies

**4. Simulate** — Let Claude handle natively (no script, minimal prose)
- Basic arithmetic (add, subtract, multiply, divide)
- String concatenation, formatting, templating
- File reading and writing (Claude has Read/Write tools)
- Simple JSON/YAML manipulation
- List operations on small collections
- Pattern matching on obvious patterns

### The Golden Rule: Minimize Scripts

The goal of CompileToSkill is to translate code into LLM-native instructions — NOT to just wrap scripts in markdown. The output skill should have the **absolute minimum** number of bundled scripts. Every operation should be pushed toward Prose, Simulate, or Bake In first. Only use Script when:
- The operation requires mathematical precision Claude can't guarantee (floating-point, crypto)
- The algorithm is too complex to express in prose without ambiguity (sorting large datasets, complex regex with many edge cases)
- The fuzzer proved the output space is too large or unpredictable for prose instructions

Ask yourself for each operation: "Can Claude reliably do this with just instructions?" If yes → Prose or Simulate. If Claude would get it wrong >20% of the time → Script.

### Classification Judgment Calls

Prefer **Prose** and **Simulate** over **Script** whenever possible. The whole point is to compile code INTO the neural network's native instruction format. A skill that's just "run these 5 scripts" hasn't really been compiled — it's just been wrapped.

The fuzzing results inform this: if the fuzzer showed that an operation produces simple, predictable outputs that follow patterns Claude could reason about, use Prose or Simulate. Only if outputs are complex, precision-sensitive, or have too many variations should it remain a Script.

**Challenge every Script classification:** Before finalizing, look at each Script and ask "Could I teach Claude to do this with clear instructions and examples?" If the answer is yes, downgrade to Prose with examples.

**CHECKPOINT:** Present the classification to the user as a table:

```
| Operation          | Strategy  | Reasoning                                    |
|--------------------|-----------|----------------------------------------------|
| calculate_tax()    | Script    | Floating-point math, needs precision          |
| is_valid_email()   | Script    | Complex regex, many edge cases                |
| get_greeting()     | Prose     | Simple conditional on time of day             |
| STATE_NAMES        | Bake In   | Static lookup table, never changes            |
| format_output()    | Simulate  | String templating, Claude handles natively    |
```

Ask: "Here's how I'd split the code. Want to adjust any of these?"

Wait for user approval before proceeding.

---

## Phase 4: Translate (Code → Markdown Skill)

Now generate the actual skill. Run the translator:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/translate.py \
  --source <source-file> \
  --analysis <analysis.json> \
  --fuzz-results <fuzz-results.json> \
  --classifications <classifications.json> \
  --output-dir <target-skill-directory>
```

The translator generates the skeleton. Then you refine it by hand — the translator handles structure, you handle prose quality.

### What to Generate

**SKILL.md** with:
- Proper frontmatter (name, description with trigger phrases, argument-hint, allowed-tools)
- `$ARGUMENTS` mapping from the original program's CLI args or function parameters
- Step-by-step instructions translating the program's logic flow
- Checkpoints where the original code had user interaction
- References to bundled scripts where operations were classified as "Script"
- Baked-in data for operations classified as "Bake In"
- Clear instructions for operations classified as "Simulate"

**scripts/** with:
- Self-contained Python scripts for each "Script" classified operation
- Each script should accept arguments and produce output to stdout
- Scripts must be runnable independently: `python scripts/operation_name.py <args>`
- Include a shebang line and docstring explaining what each script does

**references/** with:
- Lookup tables, configuration data, and baked-in values
- Any complex reference material the skill needs
- Per-domain documentation if the original code serves multiple use cases

### Translation Principles

1. **Preserve the original program's behavior** — the skill should produce equivalent outputs
2. **Make prose instructions specific** — not "process the data" but "read the CSV, extract column 3, and format as a bulleted list"
3. **Scripts should be minimal** — only the computational core, not the orchestration
4. **Baked-in data should be formatted for easy Claude consumption** — markdown tables, not raw JSON
5. **Add error handling as prose** — "If the input file doesn't exist, tell the user and ask for the correct path"

---

## Phase 5: Optimize & Validate

Review the generated skill for quality:

### Coherence Check
- Read the generated SKILL.md end-to-end. Does it flow logically?
- Are the prose instructions unambiguous? Could Claude misinterpret any step?
- Do script invocations have clear input/output contracts?
- Is the `allowed-tools` list correct for what the skill needs?

### Script Validation
- Run each bundled script with test inputs to verify they work:
  ```bash
  python <target-skill-dir>/scripts/<script_name>.py <test-input>
  ```
- Check that scripts are self-contained (no external deps beyond standard library)

### Equivalence Test
Using the inputs from Phase 2 fuzzing:
- Run the original code with those inputs
- Mentally trace (or actually test) how the skill would handle the same inputs
- Flag any discrepancies

### Size Check
- Is SKILL.md under 500 lines? If not, move details to references/
- Are reference files well-organized with clear pointers from SKILL.md?

---

## Phase 6: Package & Present

### Compilation Report
Present a summary to the user:

```
## CompileToSkill Report

**Source**: <filename> (<language>)
**Target**: <skill-directory-path>

### Compilation Strategy
- Baked In: X operations (constants, lookup tables)
- Script: Y operations (algorithms, computation)
- Prose: Z operations (decision logic, workflows)
- Simulated: W operations (Claude-native tasks)

### Generated Files
- SKILL.md (N lines)
- scripts/operation_a.py
- scripts/operation_b.py
- references/lookup_tables.md

### Coverage
- Fuzz inputs tested: N
- Code paths covered: ~M%
- Operations compiled: P/Q total

### Notes
- [Any caveats, unsupported features, or warnings]
```

**CHECKPOINT:** "Here's the compiled skill and report. Want to review the generated SKILL.md before I finalize? Any adjustments needed?"

### Finalize
Once approved:
1. Ensure all files are written to the target skill directory
2. Verify the directory structure matches the skill format:
   ```
   <skill-name>/
   ├── SKILL.md
   ├── scripts/
   │   └── *.py
   └── references/
       └── *.md
   ```
3. Tell the user: "Your skill is ready at `<path>`. You can use it with `/<skill-name>` or it will auto-trigger based on the description."

---

## Special Cases

### Pure Math/Algorithm Code
If the code is entirely computational (e.g., Fibonacci, sorting, matrix operations):
- First ask: can Claude do this math reliably? Simple formulas, basic recursion, small-input algorithms → translate to Prose with worked examples
- Only keep as Script if precision is critical or the computation is too complex for reliable prose instructions
- Bake In results for small, finite input ranges (e.g., Fibonacci(1-50) as a lookup table)
- The goal is STILL to minimize scripts — a skill that's just "run compute.py" hasn't been compiled, it's been wrapped

### Pure Decision Logic
If the code is entirely branching/conditional (e.g., rule engines, validators):
- Almost everything becomes Prose
- The skill reads like a decision tree in natural language
- Minimal or no scripts needed

### Mixed I/O Programs
If the code reads files, transforms data, and writes output:
- File I/O becomes Simulate (Claude has native tools)
- Transformation logic becomes Script if complex, Prose if simple
- Output formatting becomes Prose

### Stateful Programs
If the code maintains state across invocations:
- Translate state to file-based persistence (`.claude/workflows/<name>-state.json`)
- Add prose instructions for reading/writing state between steps
- Warn the user that stateful behavior in skills is approximate
