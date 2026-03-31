#!/usr/bin/env python3
"""Code-to-markdown skill translator for CompileToSkill.

Takes classified operations and generates a complete Claude Code skill
directory with SKILL.md, scripts/, and references/.

Usage:
    python translate.py --source <file> --analysis <analysis.json> \
        --classifications <classifications.json> \
        [--fuzz-results <fuzz.json>] \
        --output-dir <path> [--skill-name <name>]
"""

import json
import os
import re
import sys
import textwrap


def slugify(name):
    """Convert a name to kebab-case skill name."""
    name = os.path.splitext(os.path.basename(name))[0]
    name = re.sub(r"[^a-zA-Z0-9]+", "-", name)
    name = re.sub(r"-+", "-", name).strip("-").lower()
    return name or "compiled-skill"


def read_source(file_path):
    """Read source file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


def get_function_source(source, func_class):
    """Extract function source code from line number."""
    lines = source.split("\n")
    start = func_class.get("line_number", 1) - 1
    line_count = 20  # default
    # Try to find line_count from analysis
    end = min(start + line_count, len(lines))
    return "\n".join(lines[start:end])


def determine_tools(classifications):
    """Determine which tools the skill needs based on classifications."""
    tools = {"Read"}  # Always need Read

    has_scripts = any(c.get("strategy") == "script" for c in classifications)
    has_file_io = any(
        "file" in c.get("reasoning", "").lower() or
        "File I/O" in c.get("reasoning", "")
        for c in classifications
    )

    if has_scripts:
        tools.add("Bash")
    if has_file_io:
        tools.update({"Write", "Edit"})

    tools.add("Glob")  # Generally useful

    return ", ".join(sorted(tools))


def generate_description(skill_name, analysis, classifications):
    """Generate a skill description with trigger phrases."""
    language = analysis.get("language", "unknown")
    functions = analysis.get("functions", [])
    func_names = [f["name"] for f in functions[:5]]

    # Infer purpose from function names and docstrings
    purpose_hints = []
    for f in functions:
        if f.get("docstring"):
            purpose_hints.append(f["docstring"][:100])
        else:
            readable = f["name"].replace("_", " ")
            purpose_hints.append(readable)

    purpose = purpose_hints[0] if purpose_hints else f"functionality from {skill_name}"
    readable_name = skill_name.replace("-", " ").title()

    return (
        f"{readable_name}: {purpose}. "
        f"Compiled from {language} source. "
        f"Use when user needs {', '.join(purpose_hints[:3])}."
    )


def generate_argument_hint(analysis):
    """Generate argument hint from original program's input patterns."""
    io = analysis.get("io_patterns", {})
    entry_points = analysis.get("entry_points", [])
    functions = analysis.get("functions", [])

    hints = []
    if io.get("reads_stdin"):
        hints.append("input value")

    # Check main function args
    for f in functions:
        if f["name"] in ("main", "__main__"):
            args = [a.split(":")[0].split("=")[0].strip() for a in f.get("args", []) if a != "self"]
            if args:
                hints.extend(args)

    if not hints:
        # Fallback: use first function's args
        for f in functions:
            if f["name"] != "__init__":
                args = [a.split(":")[0].split("=")[0].strip() for a in f.get("args", []) if a != "self"]
                if args:
                    hints.extend(args[:3])
                    break

    if hints:
        return " ".join(f"<{h}>" for h in hints[:3])
    return "<input>"


def generate_bake_in_section(bake_in_ops, source):
    """Generate reference data sections for baked-in operations."""
    if not bake_in_ops:
        return ""

    lines = ["## Reference Data", ""]

    for op in bake_in_ops:
        name = op.get("name", "data")
        preview = op.get("data_preview", op.get("value", ""))

        lines.append(f"### {name}")
        lines.append("")

        # Try to format as a table if it looks like a dict
        if preview.startswith("{") and ":" in preview:
            lines.append("| Key | Value |")
            lines.append("|-----|-------|")
            # Simple dict parsing
            pairs = re.findall(r"['\"]([^'\"]+)['\"]\s*:\s*([^,}]+)", preview)
            for key, val in pairs[:20]:
                lines.append(f"| {key.strip()} | {val.strip()} |")
            if len(pairs) > 20:
                lines.append(f"| ... | ({len(pairs) - 20} more entries) |")
        else:
            lines.append(f"```")
            lines.append(preview[:500])
            lines.append(f"```")

        lines.append("")

    return "\n".join(lines)


def generate_script_file(op, source, analysis):
    """Generate a standalone script for a Script-classified operation."""
    name = op.get("name", "operation")
    line_num = op.get("line_number", 0)
    language = analysis.get("language", "python")

    # Extract function source
    lines = source.split("\n")
    start = max(0, line_num - 1)

    # Find function end (heuristic)
    func_lines = []
    if language == "python":
        # Capture until dedent
        base_indent = None
        for i in range(start, min(start + 200, len(lines))):
            line = lines[i]
            if i == start:
                base_indent = len(line) - len(line.lstrip())
                func_lines.append(line)
            elif line.strip() == "":
                func_lines.append(line)
            elif len(line) - len(line.lstrip()) > base_indent:
                func_lines.append(line)
            elif line.strip().startswith(("def ", "class ", "@")):
                break
            else:
                # Could be a continuation at same indent within function
                if base_indent == 0:
                    func_lines.append(line)
                else:
                    break
    else:
        # For brace languages, count braces
        depth = 0
        for i in range(start, min(start + 200, len(lines))):
            line = lines[i]
            func_lines.append(line)
            depth += line.count("{") - line.count("}")
            if depth <= 0 and i > start:
                break

    func_code = "\n".join(func_lines)

    # Find constants this function depends on
    deps = op.get("dependencies", [])
    const_code = []
    for const in analysis.get("constants", []):
        const_name = const.get("name", "")
        if const_name in func_code or const_name in deps:
            cl = max(0, const.get("line_number", 1) - 1)
            if cl < len(lines):
                const_code.append(lines[cl])

    # Build standalone script
    script_lines = [
        "#!/usr/bin/env python3",
        f'"""Extracted operation: {name}"""',
        "import sys",
        "",
    ]

    # Add constants
    if const_code:
        script_lines.extend(const_code)
        script_lines.append("")

    # Add helper functions this function calls
    # (Simple heuristic: look for called function names in the source)
    called_funcs = re.findall(r"\b(\w+)\s*\(", func_code)
    for cf in called_funcs:
        if cf in ("print", "len", "str", "int", "float", "range", "open",
                   "isinstance", "type", "sorted", "list", "dict", "set",
                   "min", "max", "sum", "abs", "round", "enumerate", "zip",
                   "map", "filter", name, "sys", "os", "re", "json",
                   "True", "False", "None", "input", "format", "super"):
            continue
        # Check if it's defined in the source
        for f in analysis.get("functions", []):
            if f["name"] == cf:
                cf_start = max(0, f.get("line_number", 1) - 1)
                cf_end = min(cf_start + f.get("line_count", 10), len(lines))
                helper_code = "\n".join(lines[cf_start:cf_end])
                script_lines.append(helper_code)
                script_lines.append("")
                break

    # Add the main function (strip leading indentation if needed)
    dedented = textwrap.dedent(func_code)
    script_lines.append(dedented)
    script_lines.append("")

    # Add CLI interface
    args_list = []
    for f in analysis.get("functions", []):
        if f["name"] == name:
            args_list = [a.split(":")[0].split("=")[0].strip()
                        for a in f.get("args", []) if a != "self"]
            break

    script_lines.append("")
    script_lines.append('if __name__ == "__main__":')

    if args_list:
        for i, arg in enumerate(args_list):
            script_lines.append(f"    {arg} = sys.argv[{i + 1}] if len(sys.argv) > {i + 1} else None")
        # Try to infer types from names
        typed_args = []
        for arg in args_list:
            if any(t in arg.lower() for t in ("num", "count", "size", "age", "id", "amount", "price", "rate", "n")):
                typed_args.append(f"float({arg})" if "rate" in arg.lower() or "price" in arg.lower() else f"int({arg})")
            else:
                typed_args.append(arg)
        script_lines.append(f"    result = {name}({', '.join(typed_args)})")
    else:
        script_lines.append(f"    result = {name}()")

    script_lines.append("    if result is not None:")
    script_lines.append("        print(result)")

    return "\n".join(script_lines)


def generate_skill_md(skill_name, analysis, classifications_data, fuzz_data=None):
    """Generate the SKILL.md content."""
    classifications = classifications_data.get("classifications", [])
    summary = classifications_data.get("strategy_summary", {})

    description = generate_description(skill_name, analysis, classifications)
    arg_hint = generate_argument_hint(analysis)
    tools = determine_tools(classifications)

    bake_ops = [c for c in classifications if c.get("strategy") == "bake_in" and c.get("type") != "import"]
    script_ops = [c for c in classifications if c.get("strategy") == "script" and c.get("type") != "import"]
    prose_ops = [c for c in classifications if c.get("strategy") == "prose"]
    sim_ops = [c for c in classifications if c.get("strategy") == "simulate"]

    lines = []

    # Frontmatter
    lines.append("---")
    lines.append(f"name: {skill_name}")
    lines.append(f"description: >")
    # Wrap description
    for desc_line in textwrap.wrap(description, 76):
        lines.append(f"  {desc_line}")
    lines.append(f'argument-hint: "{arg_hint}"')
    lines.append(f"allowed-tools: {tools}")
    lines.append("---")
    lines.append("")

    # Title
    readable = skill_name.replace("-", " ").title()
    lines.append(f"# {readable}")
    lines.append("")

    # Overview
    language = analysis.get("language", "unknown")
    func_count = len(analysis.get("functions", []))
    lines.append(
        f"Compiled from {language} source ({func_count} functions). "
        f"Strategy: {summary.get('prose', 0)} prose, "
        f"{summary.get('simulate', 0)} simulated, "
        f"{summary.get('bake_in', 0)} baked-in, "
        f"{summary.get('script', 0)} scripted."
    )
    lines.append("")

    # Input handling
    lines.append("## Input")
    lines.append("")
    lines.append(f"$ARGUMENTS: {arg_hint}")
    lines.append("")

    io = analysis.get("io_patterns", {})
    if io.get("reads_stdin"):
        lines.append("If no arguments provided, ask the user for input.")
    lines.append("")

    # Process section
    lines.append("## Process")
    lines.append("")

    step_num = 1

    # Prose operations (main body of the skill)
    for op in prose_ops:
        lines.append(f"### Step {step_num}: {op['name'].replace('_', ' ').title()}")
        lines.append("")
        if op.get("prose_draft"):
            lines.append(op["prose_draft"])
        else:
            lines.append(f"Perform the '{op['name']}' operation.")
            lines.append(f"_(Reasoning: {op.get('reasoning', 'decision logic')})_")
        lines.append("")
        step_num += 1

    # Script operations
    for op in script_ops:
        if op.get("type") == "import":
            continue
        script_name = op.get("suggested_script_name", f"{op['name']}.py")
        lines.append(f"### Step {step_num}: {op['name'].replace('_', ' ').title()}")
        lines.append("")
        lines.append(f"Run the computation:")
        lines.append("")
        lines.append("```bash")
        lines.append(f"python ${{CLAUDE_SKILL_DIR}}/scripts/{script_name} $ARGUMENTS")
        lines.append("```")
        lines.append("")
        lines.append(f"The script handles: {op.get('reasoning', 'deterministic computation')}.")
        lines.append("Present the output to the user.")
        lines.append("")
        step_num += 1

    # Simulate operations
    for op in sim_ops:
        lines.append(f"### Step {step_num}: {op['name'].replace('_', ' ').title()}")
        lines.append("")
        lines.append(f"Handle this directly — {op.get('reasoning', 'simple operation Claude handles natively')}.")
        lines.append("")
        step_num += 1

    # Reference data section (baked-in)
    if bake_ops:
        bake_section = generate_bake_in_section(bake_ops, "")
        lines.append(bake_section)

    # Error handling
    lines.append("## Error Handling")
    lines.append("")

    if fuzz_data and fuzz_data.get("output_analysis", {}).get("error_messages"):
        for err in fuzz_data["output_analysis"]["error_messages"][:5]:
            msg = err.get("message", "Unknown error")
            triggers = err.get("trigger_inputs", [])
            lines.append(f"- **{msg}**: Triggered by inputs like {', '.join(triggers[:2]) if triggers else 'edge cases'}. "
                        f"Tell the user what went wrong and suggest valid input.")
    else:
        lines.append("- If input is missing or invalid: ask the user to provide valid input")
        lines.append("- If a script fails: report the error and suggest alternatives")

    lines.append("")

    # Output section
    lines.append("## Output")
    lines.append("")
    if fuzz_data:
        output_types = fuzz_data.get("output_analysis", {}).get("output_types", [])
        if output_types:
            lines.append(f"Expected output types: {', '.join(output_types)}")
        common = fuzz_data.get("output_analysis", {}).get("common_outputs", [])
        if common:
            lines.append("")
            lines.append("Common outputs:")
            for c in common[:5]:
                out = c.get("output", "")[:80]
                lines.append(f"- `{out}`")
    else:
        lines.append("Present the result to the user in a clear, readable format.")

    lines.append("")

    return "\n".join(lines)


def translate(source_path, analysis_path, classifications_path,
              fuzz_path=None, output_dir=None, skill_name=None):
    """Main translation entry point."""
    source_path = os.path.abspath(source_path)

    # Read all inputs
    source = read_source(source_path)
    if not source:
        return {"error": f"Could not read source: {source_path}"}

    try:
        with open(analysis_path) as f:
            analysis = json.load(f)
    except Exception as e:
        return {"error": f"Could not load analysis: {e}"}

    try:
        with open(classifications_path) as f:
            classifications_data = json.load(f)
    except Exception as e:
        return {"error": f"Could not load classifications: {e}"}

    fuzz_data = None
    if fuzz_path and os.path.exists(fuzz_path):
        try:
            with open(fuzz_path) as f:
                fuzz_data = json.load(f)
        except Exception:
            pass

    # Determine skill name and output directory
    if not skill_name:
        skill_name = slugify(source_path)

    if not output_dir:
        output_dir = os.path.join(os.getcwd(), skill_name)

    output_dir = os.path.abspath(output_dir)

    # Create directory structure
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "references"), exist_ok=True)

    files_generated = []

    # Generate SKILL.md
    skill_md = generate_skill_md(skill_name, analysis, classifications_data, fuzz_data)
    skill_path = os.path.join(output_dir, "SKILL.md")
    with open(skill_path, "w") as f:
        f.write(skill_md)
    skill_lines = len(skill_md.split("\n"))
    files_generated.append({
        "path": "SKILL.md",
        "lines": skill_lines,
        "type": "skill",
    })

    # Generate scripts
    classifications = classifications_data.get("classifications", [])
    script_ops = [c for c in classifications if c.get("strategy") == "script" and c.get("type") != "import"]

    for op in script_ops:
        script_name = op.get("suggested_script_name", f"{op['name']}.py")
        script_content = generate_script_file(op, source, analysis)
        script_path = os.path.join(output_dir, "scripts", script_name)
        with open(script_path, "w") as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        files_generated.append({
            "path": f"scripts/{script_name}",
            "lines": len(script_content.split("\n")),
            "type": "script",
        })

    # Generate reference data
    bake_ops = [c for c in classifications if c.get("strategy") == "bake_in"]
    if bake_ops:
        ref_content = generate_bake_in_section(bake_ops, source)
        if ref_content.strip():
            ref_path = os.path.join(output_dir, "references", "data.md")
            with open(ref_path, "w") as f:
                f.write(ref_content)
            files_generated.append({
                "path": "references/data.md",
                "lines": len(ref_content.split("\n")),
                "type": "reference",
            })

    # Generate source mapping (for debugging)
    mapping_lines = [
        "# Source Mapping",
        "",
        f"Original source: `{source_path}`",
        f"Language: {analysis.get('language', 'unknown')}",
        "",
        "## Operation Mapping",
        "",
        "| Operation | Strategy | Original Line | Skill Location |",
        "|-----------|----------|---------------|----------------|",
    ]
    for c in classifications:
        if c.get("type") == "import":
            continue
        mapping_lines.append(
            f"| {c.get('name', '?')} | {c.get('strategy', '?')} | "
            f"L{c.get('line_number', '?')} | "
            f"{'scripts/' + c.get('suggested_script_name', '') if c.get('strategy') == 'script' else 'SKILL.md'} |"
        )
    mapping_lines.append("")

    mapping_path = os.path.join(output_dir, "references", "source-mapping.md")
    with open(mapping_path, "w") as f:
        f.write("\n".join(mapping_lines))
    files_generated.append({
        "path": "references/source-mapping.md",
        "lines": len(mapping_lines),
        "type": "reference",
    })

    # Build report
    strategy_summary = classifications_data.get("strategy_summary", {})

    # Determine argument mapping
    arg_hint = generate_argument_hint(analysis)
    original_cmd = f"{analysis.get('language', 'python')} {os.path.basename(source_path)}"

    warnings = []
    if len(script_ops) > 3:
        warnings.append(
            f"{len(script_ops)} operations kept as scripts — "
            "consider reviewing if any can be converted to prose"
        )
    if skill_lines > 500:
        warnings.append(
            f"SKILL.md is {skill_lines} lines — consider moving details to references/"
        )

    # Check for external deps in scripts
    ext_deps = analysis.get("dependencies", {}).get("external_packages", [])
    if ext_deps:
        warnings.append(
            f"External dependencies detected: {', '.join(ext_deps)}. "
            "Scripts may need these packages installed."
        )

    report = {
        "skill_name": skill_name,
        "output_dir": output_dir,
        "files_generated": files_generated,
        "strategy_breakdown": strategy_summary,
        "argument_mapping": {
            "original": f"{original_cmd} {arg_hint}",
            "skill": f"/{skill_name} {arg_hint}",
        },
        "warnings": warnings,
    }

    return report


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python translate.py --source <file> --analysis <path> "
                     "--classifications <path> [--fuzz-results <path>] "
                     "--output-dir <path> [--skill-name <name>]"
        }))
        sys.exit(1)

    source = None
    analysis = None
    classifications = None
    fuzz = None
    output_dir = None
    skill_name = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--source" and i + 1 < len(args):
            source = args[i + 1]
            i += 2
        elif args[i] == "--analysis" and i + 1 < len(args):
            analysis = args[i + 1]
            i += 2
        elif args[i] == "--classifications" and i + 1 < len(args):
            classifications = args[i + 1]
            i += 2
        elif args[i] == "--fuzz-results" and i + 1 < len(args):
            fuzz = args[i + 1]
            i += 2
        elif args[i] == "--output-dir" and i + 1 < len(args):
            output_dir = args[i + 1]
            i += 2
        elif args[i] == "--skill-name" and i + 1 < len(args):
            skill_name = args[i + 1]
            i += 2
        else:
            i += 1

    if not all([source, analysis, classifications]):
        print(json.dumps({
            "error": "--source, --analysis, and --classifications are all required"
        }))
        sys.exit(1)

    result = translate(source, analysis, classifications, fuzz, output_dir, skill_name)
    print(json.dumps(result, indent=2))

    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
