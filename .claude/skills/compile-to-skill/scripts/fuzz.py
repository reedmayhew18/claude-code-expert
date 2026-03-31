#!/usr/bin/env python3
"""Deep fuzzing and profiling engine for CompileToSkill.

Runs source code with generated inputs to understand runtime behavior,
output ranges, edge cases, and performance characteristics.

Usage:
    python fuzz.py <source-file> [--depth quick|moderate|deep] [--analysis <analysis.json>]
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time

# Input generation values by type
NUMERIC_INPUTS = [0, 1, -1, 2, 10, 42, 100, -100, 999, -999, 1000000, -1000000]
FLOAT_INPUTS = [0.0, 0.5, -0.5, 1.0, -1.0, 3.14159, 0.001, -0.001, 99.99]
STRING_INPUTS = [
    "", " ", "hello", "Hello World", "test", "abc", "123",
    "foo bar baz", "special!@#$%", "UPPERCASE", "MiXeD cAsE",
    "a", "ab", "a b c", "line1\nline2", "tab\there",
    "unicode café", "emoji 🎉", "path/to/file.txt",
    "true", "false", "null", "none", "None", "yes", "no",
]
EDGE_INPUTS = [
    "", "0", "-1", "999999999", "-999999999",
    " ", "\n", "\t", "null", "undefined", "NaN", "inf", "-inf",
]
BOOL_INPUTS = ["true", "false", "True", "False", "1", "0", "yes", "no"]

DEPTH_CONFIG = {
    "quick": {"max_runs": 15, "timeout_per_run": 3},
    "moderate": {"max_runs": 40, "timeout_per_run": 5},
    "deep": {"max_runs": 120, "timeout_per_run": 5},
}

LANGUAGE_RUNNERS = {
    "python": ["python3", "{file}"],
    "javascript": ["node", "{file}"],
    "typescript": ["npx", "tsx", "{file}"],
    "ruby": ["ruby", "{file}"],
    "php": ["php", "{file}"],
    "perl": ["perl", "{file}"],
    "lua": ["lua", "{file}"],
    "shell": ["bash", "{file}"],
    "r": ["Rscript", "{file}"],
}

COMPILED_LANGUAGES = {
    "c": {"compiler": "gcc", "flags": ["-o", "{output}", "{file}", "-lm"]},
    "cpp": {"compiler": "g++", "flags": ["-o", "{output}", "{file}", "-std=c++17"]},
    "rust": {"compiler": "rustc", "flags": ["-o", "{output}", "{file}"]},
    "go": {"compiler": "go", "flags": ["build", "-o", "{output}", "{file}"]},
}


def detect_language(file_path):
    """Detect language from extension."""
    ext_map = {
        ".py": "python", ".js": "javascript", ".mjs": "javascript",
        ".ts": "typescript", ".tsx": "typescript",
        ".c": "c", ".h": "c", ".cpp": "cpp", ".cc": "cpp",
        ".rs": "rust", ".go": "go", ".rb": "ruby", ".php": "php",
        ".sh": "shell", ".bash": "shell", ".pl": "perl",
        ".lua": "lua", ".r": "r", ".R": "r",
        ".java": "java", ".kt": "kotlin", ".swift": "swift",
    }
    _, ext = os.path.splitext(file_path)
    return ext_map.get(ext, "unknown")


def generate_inputs(depth, analysis=None):
    """Generate test inputs based on depth and optional analysis data."""
    config = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["moderate"])
    max_runs = config["max_runs"]

    inputs = []

    # Always include edge cases
    for val in EDGE_INPUTS:
        inputs.append({"type": "edge", "stdin": val, "args": [val]})

    # Numeric inputs
    for val in NUMERIC_INPUTS:
        inputs.append({"type": "numeric", "stdin": str(val), "args": [str(val)]})

    if depth in ("moderate", "deep"):
        for val in FLOAT_INPUTS:
            inputs.append({"type": "float", "stdin": str(val), "args": [str(val)]})

    # String inputs
    for val in STRING_INPUTS:
        inputs.append({"type": "string", "stdin": val, "args": [val]})

    # Multi-argument inputs
    for a in ["1", "10", "hello"]:
        for b in ["2", "20", "world"]:
            inputs.append({"type": "multi_arg", "stdin": f"{a} {b}", "args": [a, b]})

    # Bool inputs
    for val in BOOL_INPUTS:
        inputs.append({"type": "bool", "stdin": val, "args": [val]})

    # If we have analysis, generate smarter inputs
    if analysis:
        funcs = analysis.get("functions", [])
        for func in funcs:
            args = func.get("args", [])
            if args:
                # Generate inputs matching argument count
                arg_count = len(args)
                for combo in _generate_arg_combos(arg_count, depth):
                    inputs.append({
                        "type": "function_targeted",
                        "stdin": " ".join(combo),
                        "args": combo,
                        "target_function": func.get("name"),
                    })

    if depth == "deep":
        # Boundary pairs
        for a in ["0", "1", "-1", "2147483647", "-2147483648"]:
            for b in ["0", "1", "-1"]:
                inputs.append({"type": "boundary", "stdin": f"{a} {b}", "args": [a, b]})

        # Long strings
        inputs.append({"type": "stress", "stdin": "a" * 1000, "args": ["a" * 1000]})
        inputs.append({"type": "stress", "stdin": "x " * 500, "args": ["x" * 500]})

    # Trim to max runs
    return inputs[:max_runs]


def _generate_arg_combos(arg_count, depth):
    """Generate argument combinations for a given argument count."""
    base_values = ["1", "hello", "0", "-1", "test"]
    if depth == "deep":
        base_values += ["", "999999", "3.14", "true", " "]

    combos = []
    for val in base_values:
        combos.append([val] * arg_count)

    # Mix different types
    if arg_count >= 2:
        combos.append(["42", "hello"])
        combos.append(["0", "0"])
        combos.append(["-1", "test"])

    return combos[:10]


def compile_source(file_path, language):
    """Compile source code for compiled languages. Returns path to binary or None."""
    if language not in COMPILED_LANGUAGES:
        return None

    config = COMPILED_LANGUAGES[language]
    output_path = tempfile.mktemp(prefix="cts_compiled_")

    cmd = [config["compiler"]]
    for flag in config["flags"]:
        cmd.append(flag.replace("{output}", output_path).replace("{file}", file_path))

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and os.path.exists(output_path):
            os.chmod(output_path, 0o755)
            return output_path
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def run_single(cmd, stdin_input, timeout):
    """Run a single test case and capture results."""
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            input=stdin_input,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        elapsed = (time.time() - start) * 1000

        stdout = result.stdout[:2000] if result.stdout else ""
        stderr = result.stderr[:1000] if result.stderr else ""

        return {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "time_ms": round(elapsed, 1),
            "timeout": False,
            "crash": result.returncode != 0 and result.returncode not in (0, 1, 2),
        }
    except subprocess.TimeoutExpired:
        elapsed = (time.time() - start) * 1000
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": "TIMEOUT",
            "time_ms": round(elapsed, 1),
            "timeout": True,
            "crash": False,
        }
    except FileNotFoundError:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Runtime not found for command: {cmd[0]}",
            "time_ms": 0,
            "timeout": False,
            "crash": False,
        }
    except Exception as e:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e)[:500],
            "time_ms": 0,
            "timeout": False,
            "crash": False,
        }


def analyze_outputs(runs):
    """Analyze the collected run outputs."""
    successful_outputs = [r["result"]["stdout"].strip() for r in runs if r["result"]["success"]]
    failed_outputs = [r["result"]["stderr"].strip() for r in runs if not r["result"]["success"]]

    # Count unique outputs
    output_counts = {}
    for out in successful_outputs:
        key = out[:500]  # Truncate for counting
        output_counts[key] = output_counts.get(key, 0) + 1

    # Identify output types
    output_types = set()
    for out in successful_outputs:
        if not out:
            output_types.add("empty")
        elif re.match(r"^-?\d+$", out):
            output_types.add("integer")
        elif re.match(r"^-?\d+\.?\d*$", out):
            output_types.add("numeric")
        elif out.startswith("{") or out.startswith("["):
            output_types.add("json")
        elif "\n" in out:
            output_types.add("multiline")
        else:
            output_types.add("string")

    # Common outputs
    common = sorted(output_counts.items(), key=lambda x: -x[1])[:10]

    # Error analysis
    error_counts = {}
    error_triggers = {}
    for r in runs:
        if not r["result"]["success"] and r["result"]["stderr"]:
            err_key = r["result"]["stderr"].strip().split("\n")[-1][:200]
            error_counts[err_key] = error_counts.get(err_key, 0) + 1
            if err_key not in error_triggers:
                error_triggers[err_key] = []
            if len(error_triggers[err_key]) < 3:
                trigger = r["input"].get("stdin", str(r["input"].get("args", [])))
                error_triggers[err_key].append(trigger[:100])

    # Numeric range
    numeric_outputs = []
    for out in successful_outputs:
        try:
            numeric_outputs.append(float(out.strip()))
        except (ValueError, TypeError):
            pass

    output_range = None
    if numeric_outputs:
        output_range = {
            "min": str(min(numeric_outputs)),
            "max": str(max(numeric_outputs)),
        }

    return {
        "unique_output_patterns": len(output_counts),
        "output_types": sorted(output_types),
        "output_range": output_range,
        "common_outputs": [
            {"output": out[:200], "frequency": count}
            for out, count in common
        ],
        "error_messages": [
            {
                "message": msg[:200],
                "frequency": count,
                "trigger_inputs": error_triggers.get(msg, []),
            }
            for msg, count in sorted(error_counts.items(), key=lambda x: -x[1])[:10]
        ],
    }


def generate_recommendations(runs, output_analysis, io_patterns=None):
    """Generate compilation strategy recommendations based on fuzz results."""
    recommendations = []
    successful = [r for r in runs if r["result"]["success"]]
    failed = [r for r in runs if not r["result"]["success"]]

    # Determinism check
    input_outputs = {}
    for r in successful:
        key = str(r["input"].get("args", r["input"].get("stdin")))
        out = r["result"]["stdout"].strip()
        if key in input_outputs:
            if input_outputs[key] != out:
                recommendations.append(
                    "Non-deterministic behavior detected — same input produced different outputs. "
                    "Must keep as Script for reliability."
                )
                break
        input_outputs[key] = out

    unique_patterns = output_analysis.get("unique_output_patterns", 0)

    if unique_patterns <= 5:
        recommendations.append(
            f"Only {unique_patterns} unique output patterns — strong candidate for Prose translation "
            "or Bake In as a lookup table."
        )
    elif unique_patterns <= 15:
        recommendations.append(
            f"{unique_patterns} unique output patterns — could be Prose with worked examples, "
            "or Script if precision matters."
        )
    else:
        recommendations.append(
            f"{unique_patterns} unique output patterns — likely needs Script strategy "
            "due to complex output space."
        )

    # Error handling patterns
    if output_analysis.get("error_messages"):
        recommendations.append(
            "Predictable error patterns detected — error handling can be translated to Prose."
        )

    # Performance
    times = [r["result"]["time_ms"] for r in runs if r["result"]["time_ms"] > 0]
    if times and max(times) > 1000:
        recommendations.append(
            f"Slow execution detected (max {max(times):.0f}ms) — keep as Script to avoid "
            "Claude attempting long computation."
        )

    # Simple output
    if output_analysis.get("output_types") == ["string"] and unique_patterns <= 3:
        recommendations.append(
            "Simple string outputs — strong candidate for Simulate (Claude handles natively)."
        )

    return recommendations


def fuzz(file_path, depth="moderate", analysis_path=None):
    """Main fuzzing entry point."""
    file_path = os.path.abspath(file_path)

    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    language = detect_language(file_path)
    config = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["moderate"])

    # Load analysis if provided
    analysis = None
    if analysis_path and os.path.exists(analysis_path):
        try:
            with open(analysis_path) as f:
                analysis = json.load(f)
        except Exception:
            pass

    # Determine how to run the code
    compiled_binary = None
    runner_available = True

    if language in COMPILED_LANGUAGES:
        compiled_binary = compile_source(file_path, language)
        if not compiled_binary:
            return {
                "source_file": file_path,
                "language": language,
                "depth": depth,
                "error": f"Compilation failed for {language} file. Falling back to static-only analysis.",
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "recommendations": ["Compilation failed — classify based on static analysis only."],
            }
    elif language in LANGUAGE_RUNNERS:
        # Check if runtime is available
        test_cmd = LANGUAGE_RUNNERS[language][0]
        try:
            subprocess.run(
                [test_cmd, "--version"], capture_output=True, timeout=5
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            runner_available = False

        if not runner_available:
            return {
                "source_file": file_path,
                "language": language,
                "depth": depth,
                "error": f"Runtime '{test_cmd}' not found. Cannot fuzz {language} files.",
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "recommendations": [f"Runtime not available — classify based on static analysis only."],
            }
    else:
        return {
            "source_file": file_path,
            "language": language,
            "depth": depth,
            "error": f"No runner configured for language: {language}",
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "recommendations": ["Unsupported language for fuzzing — classify based on static analysis only."],
        }

    # Generate inputs
    inputs = generate_inputs(depth, analysis)

    # Run tests
    runs = []
    timeout_per_run = config["timeout_per_run"]

    # Detect if program reads stdin or uses args
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
    except Exception:
        source = ""

    reads_stdin = bool(re.search(r"\b(input\s*\(|sys\.stdin|scanf|readline|gets|fgets|std::io::stdin|bufio\.Scanner)\b", source))
    uses_args = bool(re.search(r"\b(sys\.argv|argparse|process\.argv|os\.Args|ARGV|args\(\)|clap::)\b", source))

    for inp in inputs:
        if compiled_binary:
            cmd = [compiled_binary] + (inp["args"] if uses_args else [])
        else:
            runner = LANGUAGE_RUNNERS[language]
            cmd = [runner[0]] + [
                part.replace("{file}", file_path) for part in runner[1:]
            ]
            if uses_args:
                cmd += inp["args"]

        stdin_data = inp["stdin"] if reads_stdin else None

        result = run_single(cmd, stdin_data, timeout_per_run)
        runs.append({
            "input": inp,
            "result": result,
        })

    # Clean up compiled binary
    if compiled_binary and os.path.exists(compiled_binary):
        try:
            os.remove(compiled_binary)
        except Exception:
            pass

    # Analyze results
    successful = sum(1 for r in runs if r["result"]["success"])
    failed = len(runs) - successful
    timeouts = sum(1 for r in runs if r["result"]["timeout"])
    crashes = sum(1 for r in runs if r["result"]["crash"])

    times = [r["result"]["time_ms"] for r in runs if r["result"]["time_ms"] > 0]

    output_analysis = analyze_outputs(runs)

    # Determine if behavior is deterministic
    is_deterministic = True
    seen = {}
    for r in runs:
        if r["result"]["success"]:
            key = json.dumps(r["input"]["args"])
            out = r["result"]["stdout"]
            if key in seen and seen[key] != out:
                is_deterministic = False
                break
            seen[key] = out

    # Check for side effects
    has_side_effects = bool(re.search(
        r"\b(write|unlink|remove|mkdir|rmdir|chmod|rename|os\.system|subprocess)\b",
        source,
    ))

    # Generate sample I/O pairs
    sample_io = []
    for r in runs[:20]:
        if r["result"]["success"] and r["result"]["stdout"].strip():
            sample_io.append({
                "input": r["input"]["args"],
                "output": r["result"]["stdout"].strip()[:200],
            })

    recommendations = generate_recommendations(runs, output_analysis)

    return {
        "source_file": file_path,
        "language": language,
        "depth": depth,
        "total_runs": len(runs),
        "successful_runs": successful,
        "failed_runs": failed,
        "execution_summary": {
            "avg_time_ms": round(sum(times) / len(times), 1) if times else 0,
            "max_time_ms": round(max(times), 1) if times else 0,
            "min_time_ms": round(min(times), 1) if times else 0,
            "timeouts": timeouts,
            "crashes": crashes,
        },
        "output_analysis": output_analysis,
        "sample_io_pairs": sample_io[:15],
        "behavior_summary": {
            "is_deterministic": is_deterministic,
            "has_side_effects": has_side_effects,
            "reads_stdin": reads_stdin,
            "uses_args": uses_args,
            "reads_files": bool(re.search(r"\bopen\s*\(", source)),
            "modifies_filesystem": has_side_effects,
            "network_calls": bool(re.search(r"\b(requests|urllib|http|fetch|socket)\b", source)),
        },
        "recommendations": recommendations,
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python fuzz.py <source-file> [--depth quick|moderate|deep] [--analysis <path>]"
        }))
        sys.exit(1)

    file_path = sys.argv[1]
    depth = "moderate"
    analysis_path = None

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--depth" and i + 1 < len(args):
            depth = args[i + 1]
            i += 2
        elif args[i] == "--analysis" and i + 1 < len(args):
            analysis_path = args[i + 1]
            i += 2
        else:
            i += 1

    result = fuzz(file_path, depth, analysis_path)
    print(json.dumps(result, indent=2))

    if "error" in result and result.get("total_runs", 0) == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
