#!/usr/bin/env python3
"""Operation classifier for CompileToSkill.

Takes static analysis and optional fuzz results, then classifies each
operation into one of four compilation strategies:
  - bake_in:  Pre-compute and embed as data
  - script:   Keep as executable code (USE SPARINGLY)
  - prose:    Translate to natural language instructions
  - simulate: Let Claude handle natively

The guiding principle is MINIMIZE SCRIPTS. Every operation should be
pushed toward prose/simulate/bake_in first. Script is the last resort.

Usage:
    python classify.py <source-file> --analysis <analysis.json> [--fuzz-results <fuzz.json>]
"""

import json
import os
import re
import sys


# Patterns that indicate specific strategies
MATH_HEAVY_PATTERNS = re.compile(
    r"\b(math\.|numpy|scipy|pow\(|sqrt|log|sin|cos|tan|exp|"
    r"floor|ceil|round\(|decimal\.|Decimal|float\(|"
    r"cmath|statistics\.|fsum)\b"
)

CRYPTO_PATTERNS = re.compile(
    r"\b(hashlib|hmac|secrets|cryptography|bcrypt|jwt|"
    r"sha256|sha512|md5|aes|rsa|encrypt|decrypt|hash\()\b",
    re.IGNORECASE,
)

COMPLEX_REGEX_PATTERNS = re.compile(
    r"re\.(compile|match|search|findall|sub)\s*\(\s*r?['\"]"
    r"[^'\"]{30,}['\"]",  # Regex patterns longer than 30 chars
)

SIMPLE_CONDITIONAL_PATTERN = re.compile(
    r"if\s+\w+\s*(==|!=|in|not\s+in|is)\s*['\"]",
)

FILE_IO_PATTERN = re.compile(
    r"\b(open\s*\(|read\s*\(|write\s*\(|readlines|writelines|"
    r"Path\(|pathlib|os\.path|shutil)\b"
)

STRING_FORMAT_PATTERN = re.compile(
    r"(f['\"]|\.format\s*\(|%s|%d|%f|\.join\s*\(|\.strip\s*\(|"
    r"\.split\s*\(|\.replace\s*\(|\.upper\s*\(|\.lower\s*\(|"
    r"\.title\s*\(|\.startswith|\.endswith)\b"
)


def read_source_file(file_path):
    """Read source file content."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


def get_function_source(source, func_info, language="python"):
    """Extract the source code of a function given its metadata."""
    lines = source.split("\n")
    start = func_info.get("line_number", 1) - 1
    line_count = func_info.get("line_count", 20)
    end = min(start + line_count, len(lines))
    return "\n".join(lines[start:end])


def classify_constant(const_info, source):
    """Classify a constant/variable."""
    name = const_info.get("name", "")
    value = const_info.get("value", "")

    # All constants are candidates for bake_in
    # Check if it's a small lookup table
    is_dict = value.startswith("{") or "dict(" in value
    is_list = value.startswith("[") or value.startswith("(")

    if len(value) > 5000:
        reasoning = "Very large constant — embed in references/ file"
    elif is_dict:
        reasoning = "Dictionary/mapping constant — embed as markdown table"
    elif is_list:
        reasoning = "List/tuple constant — embed inline or in references/"
    else:
        reasoning = "Static constant value — embed directly in skill"

    return {
        "name": name,
        "type": "constant",
        "line_number": const_info.get("line_number", 0),
        "strategy": "bake_in",
        "confidence": 0.95,
        "reasoning": reasoning,
        "data_preview": value[:300],
    }


def classify_function(func_info, source, fuzz_data=None, language="python"):
    """Classify a function into a compilation strategy."""
    name = func_info.get("name", "")
    args = func_info.get("args", [])
    line_count = func_info.get("line_count", 0)
    docstring = func_info.get("docstring", "")
    func_source = get_function_source(source, func_info, language)

    # Gather evidence for each strategy
    scores = {
        "bake_in": 0.0,
        "script": 0.0,
        "prose": 0.0,
        "simulate": 0.0,
    }
    evidence = []

    # ---- Check for BAKE IN ----
    # Functions that return constants or simple lookups
    if line_count <= 3 and re.search(r"return\s+[A-Z_]+\[", func_source):
        scores["bake_in"] += 0.8
        evidence.append("Simple lookup function — can be baked as a table")

    # ---- Check for SIMULATE (Claude handles natively) ----
    # Simple string operations
    if STRING_FORMAT_PATTERN.search(func_source) and not MATH_HEAVY_PATTERNS.search(func_source):
        scores["simulate"] += 0.6
        evidence.append("String formatting/manipulation — Claude handles natively")

    # Very short, simple functions
    if line_count <= 5 and not MATH_HEAVY_PATTERNS.search(func_source):
        scores["simulate"] += 0.4
        evidence.append(f"Very short function ({line_count} lines) — likely simple enough to simulate")

    # Basic arithmetic only (no precision-sensitive math)
    has_basic_math = bool(re.search(r"[+\-*/]", func_source))
    has_heavy_math = bool(MATH_HEAVY_PATTERNS.search(func_source))
    if has_basic_math and not has_heavy_math and line_count <= 10:
        scores["simulate"] += 0.3
        evidence.append("Basic arithmetic only — Claude can handle")

    # File I/O (Claude has Read/Write tools)
    if FILE_IO_PATTERN.search(func_source) and line_count <= 15:
        scores["simulate"] += 0.5
        evidence.append("File I/O — Claude has native Read/Write tools")

    # ---- Check for PROSE ----
    # Decision trees / conditionals on semantic values
    conditional_count = len(re.findall(r"\b(if|elif|else|case|when)\b", func_source))
    string_comparisons = len(SIMPLE_CONDITIONAL_PATTERN.findall(func_source))

    if conditional_count >= 2 and string_comparisons >= 1:
        scores["prose"] += 0.7
        evidence.append(f"Decision tree with {conditional_count} branches on semantic conditions")

    # Workflow-like sequential logic
    if re.search(r"(step|stage|phase|validate|check|verify)\s*[_\d(]", func_source, re.IGNORECASE):
        scores["prose"] += 0.4
        evidence.append("Workflow/validation pattern detected")

    # Error handling patterns
    if re.search(r"\b(try|except|catch|raise|throw)\b", func_source):
        scores["prose"] += 0.3
        evidence.append("Error handling — translates well to prose instructions")

    # Functions that return booleans (validators)
    if re.search(r"return\s+(True|False|true|false)\b", func_source):
        scores["prose"] += 0.4
        evidence.append("Boolean return — likely a validator, good for prose rules")

    # ---- Check for SCRIPT (last resort) ----
    # Heavy math / precision-sensitive
    if has_heavy_math:
        scores["script"] += 0.7
        evidence.append("Precision-sensitive math operations — keep as script")

    # Cryptographic operations
    if CRYPTO_PATTERNS.search(func_source):
        scores["script"] += 0.9
        evidence.append("Cryptographic operations — must be exact, keep as script")

    # Complex regex
    if COMPLEX_REGEX_PATTERNS.search(func_source):
        scores["script"] += 0.6
        evidence.append("Complex regex pattern (>30 chars) — too error-prone for prose")

    # Long, complex functions
    if line_count > 30:
        scores["script"] += 0.3
        evidence.append(f"Long function ({line_count} lines) — may be too complex for prose")

    # Deeply nested logic
    max_indent = 0
    for line in func_source.split("\n"):
        indent = len(line) - len(line.lstrip())
        max_indent = max(max_indent, indent)
    if max_indent > 16:  # 4+ levels of nesting
        scores["script"] += 0.3
        evidence.append("Deeply nested logic — may be too complex for prose")

    # Binary/byte operations
    if re.search(r"\b(bytes|bytearray|struct\.pack|struct\.unpack|b['\"])\b", func_source):
        scores["script"] += 0.7
        evidence.append("Binary/byte operations — Claude cannot handle reliably")

    # ---- Use fuzz data to refine ----
    if fuzz_data:
        unique_outputs = fuzz_data.get("output_analysis", {}).get("unique_output_patterns", 0)
        is_deterministic = fuzz_data.get("behavior_summary", {}).get("is_deterministic", True)

        if not is_deterministic:
            scores["script"] += 0.5
            evidence.append("Non-deterministic behavior detected in fuzzing")

        if unique_outputs <= 5:
            scores["prose"] += 0.4
            scores["bake_in"] += 0.2
            evidence.append(f"Only {unique_outputs} unique outputs — strong prose/bake-in candidate")
        elif unique_outputs > 50:
            scores["script"] += 0.4
            evidence.append(f"{unique_outputs} unique outputs — complex output space")

        # Check fuzz recommendations
        for rec in fuzz_data.get("recommendations", []):
            if "Prose" in rec or "prose" in rec:
                scores["prose"] += 0.2
            if "Script" in rec or "script" in rec:
                scores["script"] += 0.2
            if "Bake In" in rec or "bake" in rec.lower():
                scores["bake_in"] += 0.2
            if "Simulate" in rec or "simulate" in rec.lower():
                scores["simulate"] += 0.2

    # ---- Apply the "minimize scripts" principle ----
    # Penalize script classification — only win if significantly stronger
    # This enforces the golden rule: scripts are the last resort
    if scores["script"] > 0:
        # If prose or simulate are close, prefer them
        non_script_max = max(scores["prose"], scores["simulate"], scores["bake_in"])
        if non_script_max > 0 and scores["script"] < non_script_max + 0.3:
            scores["script"] *= 0.7  # Reduce script score
            evidence.append("Applied minimize-scripts principle: non-script strategy is viable")

    # ---- Determine winner ----
    best_strategy = max(scores, key=scores.get)
    best_score = scores[best_strategy]

    # If no strategy scored well, default to prose (not script!)
    if best_score < 0.2:
        best_strategy = "prose"
        best_score = 0.5
        evidence.append("No strong signal — defaulting to prose (LLM-native approach)")

    # Calculate confidence
    total = sum(scores.values()) or 1
    confidence = round(best_score / total, 2)
    confidence = max(0.5, min(0.99, confidence))

    result = {
        "name": name,
        "type": "function",
        "line_number": func_info.get("line_number", 0),
        "strategy": best_strategy,
        "confidence": confidence,
        "reasoning": "; ".join(evidence[:3]),  # Top 3 reasons
        "dependencies": [],
    }

    # Add strategy-specific fields
    if best_strategy == "prose":
        result["prose_draft"] = generate_prose_draft(func_info, func_source)
    elif best_strategy == "script":
        result["suggested_script_name"] = f"{name}.py"
    elif best_strategy == "bake_in":
        result["data_preview"] = func_source[:200]

    return result


def generate_prose_draft(func_info, func_source):
    """Generate a first-pass prose translation of a function."""
    name = func_info.get("name", "unknown")
    args = func_info.get("args", [])
    docstring = func_info.get("docstring", "")

    parts = []

    if docstring:
        parts.append(docstring.strip().rstrip(".") + ".")
    else:
        # Generate from function name
        readable_name = name.replace("_", " ")
        parts.append(f"Perform the '{readable_name}' operation.")

    if args:
        arg_names = [a.split(":")[0].split("=")[0].strip() for a in args if a != "self"]
        if arg_names:
            parts.append(f"Takes: {', '.join(arg_names)}.")

    # Extract conditional logic
    conditions = re.findall(r"if\s+(.+?):", func_source)
    for cond in conditions[:5]:
        cond = cond.strip()
        # Clean up the condition for readability
        cond = cond.replace("==", "is").replace("!=", "is not").replace(">=", "is at least").replace("<=", "is at most")
        parts.append(f"- If {cond}: [handle accordingly]")

    return " ".join(parts[:4])


def classify_import(imp_info, source):
    """Classify an import statement."""
    module = imp_info.get("module", "")
    is_stdlib = imp_info.get("is_stdlib", False)

    # Stdlib imports don't need classification — they're part of script dependencies
    if is_stdlib:
        return None

    # External imports indicate the code needs that package
    return {
        "name": f"import:{module}",
        "type": "import",
        "strategy": "script",  # External deps usually mean script
        "confidence": 0.6,
        "reasoning": f"External dependency '{module}' — functions using this likely need Script strategy",
        "dependencies": [module],
    }


def generate_compilation_notes(classifications):
    """Generate notes about how operations relate to each other."""
    notes = []

    # Find dependency groups
    script_ops = [c for c in classifications if c.get("strategy") == "script"]
    prose_ops = [c for c in classifications if c.get("strategy") == "prose"]
    bake_ops = [c for c in classifications if c.get("strategy") == "bake_in"]

    if script_ops:
        names = [c["name"] for c in script_ops]
        notes.append(
            f"Script operations ({', '.join(names)}) should be bundled into minimal scripts. "
            "Consider combining related operations into a single script."
        )

    if prose_ops and len(prose_ops) >= 2:
        names = [c["name"] for c in prose_ops]
        notes.append(
            f"Prose operations ({', '.join(names)}) form the main body of the skill. "
            "Order them in the skill to match the original program's flow."
        )

    if bake_ops:
        names = [c["name"] for c in bake_ops]
        notes.append(
            f"Baked-in data ({', '.join(names)}) should be embedded in SKILL.md or references/. "
            "Scripts that depend on this data should include it directly."
        )

    # Check for minimal script count
    if len(script_ops) > 3:
        notes.append(
            f"WARNING: {len(script_ops)} operations classified as Script. "
            "Review each one — can any be downgraded to Prose with examples?"
        )

    return notes


def classify(source_file, analysis_path, fuzz_path=None):
    """Main classification entry point."""
    source_file = os.path.abspath(source_file)

    # Read source
    source = read_source_file(source_file)
    if not source:
        return {"error": f"Could not read source file: {source_file}"}

    # Load analysis
    try:
        with open(analysis_path) as f:
            analysis = json.load(f)
    except Exception as e:
        return {"error": f"Could not load analysis: {e}"}

    # Load fuzz results (optional)
    fuzz_data = None
    if fuzz_path and os.path.exists(fuzz_path):
        try:
            with open(fuzz_path) as f:
                fuzz_data = json.load(f)
        except Exception:
            pass

    language = analysis.get("language", "unknown")
    classifications = []

    # Classify constants
    for const in analysis.get("constants", []):
        result = classify_constant(const, source)
        classifications.append(result)

    # Classify functions
    for func in analysis.get("functions", []):
        result = classify_function(func, source, fuzz_data, language)
        classifications.append(result)

    # Classify notable imports (external only)
    for imp in analysis.get("imports", []):
        result = classify_import(imp, source)
        if result:
            classifications.append(result)

    # Generate summary
    strategy_counts = {"bake_in": 0, "script": 0, "prose": 0, "simulate": 0}
    for c in classifications:
        strategy = c.get("strategy", "prose")
        if strategy in strategy_counts:
            strategy_counts[strategy] += 1

    notes = generate_compilation_notes(classifications)

    return {
        "source_file": source_file,
        "total_operations": len(classifications),
        "classifications": classifications,
        "strategy_summary": strategy_counts,
        "compilation_notes": notes,
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python classify.py <source-file> --analysis <path> [--fuzz-results <path>]"
        }))
        sys.exit(1)

    source_file = sys.argv[1]
    analysis_path = None
    fuzz_path = None

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--analysis" and i + 1 < len(args):
            analysis_path = args[i + 1]
            i += 2
        elif args[i] == "--fuzz-results" and i + 1 < len(args):
            fuzz_path = args[i + 1]
            i += 2
        else:
            i += 1

    if not analysis_path:
        print(json.dumps({"error": "--analysis <path> is required"}))
        sys.exit(1)

    result = classify(source_file, analysis_path, fuzz_path)
    print(json.dumps(result, indent=2))

    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
