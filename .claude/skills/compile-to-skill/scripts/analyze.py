#!/usr/bin/env python3
"""Static analysis engine for CompileToSkill.

Parses source code files and extracts structural information:
functions, classes, imports, constants, I/O patterns, control flow, etc.

Uses Python's ast module for .py files; regex-based parsing for all others.
No external dependencies required.

Usage:
    python analyze.py <source-file> [--language <lang>]
"""

import ast
import json
import os
import re
import sys

# Known stdlib modules (Python) - comprehensive but not exhaustive
PYTHON_STDLIB = {
    "abc", "aifc", "argparse", "array", "ast", "asynchat", "asyncio",
    "asyncore", "atexit", "audioop", "base64", "bdb", "binascii",
    "binhex", "bisect", "builtins", "bz2", "calendar", "cgi", "cgitb",
    "chunk", "cmath", "cmd", "code", "codecs", "codeop", "collections",
    "colorsys", "compileall", "concurrent", "configparser", "contextlib",
    "contextvars", "copy", "copyreg", "cProfile", "crypt", "csv",
    "ctypes", "curses", "dataclasses", "datetime", "dbm", "decimal",
    "difflib", "dis", "distutils", "doctest", "email", "encodings",
    "enum", "errno", "faulthandler", "fcntl", "filecmp", "fileinput",
    "fnmatch", "formatter", "fractions", "ftplib", "functools", "gc",
    "getopt", "getpass", "gettext", "glob", "grp", "gzip", "hashlib",
    "heapq", "hmac", "html", "http", "idlelib", "imaplib", "imghdr",
    "imp", "importlib", "inspect", "io", "ipaddress", "itertools",
    "json", "keyword", "lib2to3", "linecache", "locale", "logging",
    "lzma", "mailbox", "mailcap", "marshal", "math", "mimetypes",
    "mmap", "modulefinder", "multiprocessing", "netrc", "nis", "nntplib",
    "numbers", "operator", "optparse", "os", "ossaudiodev", "pathlib",
    "pdb", "pickle", "pickletools", "pipes", "pkgutil", "platform",
    "plistlib", "poplib", "posix", "posixpath", "pprint", "profile",
    "pstats", "pty", "pwd", "py_compile", "pyclbr", "pydoc",
    "queue", "quopri", "random", "re", "readline", "reprlib",
    "resource", "rlcompleter", "runpy", "sched", "secrets", "select",
    "selectors", "shelve", "shlex", "shutil", "signal", "site",
    "smtpd", "smtplib", "sndhdr", "socket", "socketserver", "sqlite3",
    "ssl", "stat", "statistics", "string", "stringprep", "struct",
    "subprocess", "sunau", "symtable", "sys", "sysconfig", "syslog",
    "tabnanny", "tarfile", "telnetlib", "tempfile", "termios", "test",
    "textwrap", "threading", "time", "timeit", "tkinter", "token",
    "tokenize", "tomllib", "trace", "traceback", "tracemalloc",
    "tty", "turtle", "turtledemo", "types", "typing", "unicodedata",
    "unittest", "urllib", "uu", "uuid", "venv", "warnings", "wave",
    "weakref", "webbrowser", "winreg", "winsound", "wsgiref",
    "xdrlib", "xml", "xmlrpc", "zipapp", "zipfile", "zipimport", "zlib",
}

# GUI-related imports that trigger warnings
GUI_IMPORTS = {
    "tkinter", "PyQt5", "PyQt6", "PySide2", "PySide6", "wx", "kivy",
    "pyglet", "pygame", "gtk", "gi", "Gtk", "electron", "Qt",
}

NETWORK_PATTERNS = re.compile(
    r"\b(requests|urllib|http\.client|aiohttp|httpx|socket|"
    r"fetch|XMLHttpRequest|axios|got|node-fetch|curl_exec|"
    r"Net::HTTP|reqwest|hyper|ureq)\b"
)

DATABASE_PATTERNS = re.compile(
    r"\b(sqlite3|psycopg2|mysql|pymongo|redis|sqlalchemy|"
    r"mongoose|sequelize|prisma|diesel|rusqlite|"
    r"SELECT\s|INSERT\s|UPDATE\s|DELETE\s|CREATE\s TABLE)\b",
    re.IGNORECASE,
)

FILE_READ_PATTERNS = re.compile(
    r"\b(open\s*\(|fopen|File\.open|fs\.readFile|readFileSync|"
    r"std::fs::read|io::BufReader|os\.Open|ioutil\.ReadFile)\b"
)

FILE_WRITE_PATTERNS = re.compile(
    r"\b(\.write\s*\(|fwrite|File\.write|fs\.writeFile|writeFileSync|"
    r"std::fs::write|io::BufWriter|os\.Create|ioutil\.WriteFile)\b"
)

STDIN_PATTERNS = re.compile(
    r"\b(input\s*\(|sys\.stdin|raw_input|scanf|fgets.*stdin|"
    r"readline|process\.stdin|std::io::stdin|bufio\.NewReader.*os\.Stdin|"
    r"io::stdin)\b"
)

STDOUT_PATTERNS = re.compile(
    r"\b(print\s*\(|sys\.stdout|printf|puts|cout|"
    r"console\.log|process\.stdout|println!|fmt\.Print)\b"
)

LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".rb": "ruby",
    ".php": "php",
    ".sh": "shell",
    ".bash": "shell",
    ".pl": "perl",
    ".r": "r",
    ".R": "r",
    ".lua": "lua",
    ".swift": "swift",
    ".kt": "kotlin",
    ".cs": "csharp",
    ".scala": "scala",
}


def detect_language(file_path):
    """Detect programming language from file extension."""
    _, ext = os.path.splitext(file_path)
    return LANGUAGE_MAP.get(ext, "unknown")


def analyze_python(source, file_path):
    """Deep analysis of Python files using the ast module."""
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return {"error": f"Python syntax error: {e}", "fallback": "regex"}

    functions = []
    classes = []
    imports = []
    constants = []
    entry_points = []

    for node in ast.walk(tree):
        # Functions
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = []
            for arg in node.args.args:
                arg_name = arg.arg
                if arg.annotation:
                    try:
                        arg_name += f": {ast.unparse(arg.annotation)}"
                    except Exception:
                        pass
                args.append(arg_name)

            has_return = any(
                isinstance(n, ast.Return) and n.value is not None
                for n in ast.walk(node)
            )

            docstring = ast.get_docstring(node) or ""

            functions.append({
                "name": node.name,
                "args": args,
                "line_number": node.lineno,
                "line_count": node.end_lineno - node.lineno + 1 if node.end_lineno else 0,
                "has_return": has_return,
                "docstring": docstring[:200],
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            })

        # Classes
        elif isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(item.name)
            bases = []
            for base in node.bases:
                try:
                    bases.append(ast.unparse(base))
                except Exception:
                    bases.append("?")
            classes.append({
                "name": node.name,
                "methods": methods,
                "line_number": node.lineno,
                "bases": bases,
            })

        # Imports
        elif isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split(".")[0]
                imports.append({
                    "module": alias.name,
                    "alias": alias.asname,
                    "is_stdlib": mod in PYTHON_STDLIB,
                })
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mod = node.module.split(".")[0]
                imports.append({
                    "module": node.module,
                    "alias": None,
                    "is_stdlib": mod in PYTHON_STDLIB,
                })

    # Constants (top-level ALL_CAPS assignments)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    try:
                        val = ast.unparse(node.value)[:200]
                    except Exception:
                        val = "?"
                    constants.append({
                        "name": target.id,
                        "value": val,
                        "line_number": node.lineno,
                    })

    # Entry points
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.If):
            try:
                test_str = ast.unparse(node.test)
                if "__name__" in test_str and "__main__" in test_str:
                    entry_points.append("__name__ == '__main__'")
            except Exception:
                pass

    for f in functions:
        if f["name"] == "main":
            entry_points.append("main()")

    return {
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "constants": constants,
        "entry_points": entry_points,
    }


def analyze_with_regex(source, language):
    """Regex-based analysis for non-Python languages."""
    functions = []
    classes = []
    imports = []
    constants = []
    entry_points = []

    lines = source.split("\n")

    # Language-specific patterns
    if language in ("javascript", "typescript"):
        # Functions
        func_patterns = [
            re.compile(r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)"),
            re.compile(r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>"),
            re.compile(r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function\s*\(([^)]*)\)"),
        ]
        # Imports
        import_patterns = [
            re.compile(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]"),
            re.compile(r"(?:const|let|var)\s+.*?=\s*require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"),
        ]
        # Constants
        const_pattern = re.compile(r"(?:const|export\s+const)\s+([A-Z][A-Z_0-9]+)\s*=\s*(.+)")
        # Entry point
        entry_checks = [r"process\.argv", r"\.listen\s*\(", r"app\.use\s*\("]

    elif language in ("c", "cpp"):
        func_patterns = [
            re.compile(r"(?:[\w:*&]+\s+)+(\w+)\s*\(([^)]*)\)\s*\{"),
        ]
        import_patterns = [
            re.compile(r"#include\s*[<\"]([^>\"]+)[>\"]"),
        ]
        const_pattern = re.compile(r"#define\s+([A-Z][A-Z_0-9]+)\s+(.+)")
        entry_checks = [r"int\s+main\s*\("]

    elif language == "rust":
        func_patterns = [
            re.compile(r"(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*(?:<[^>]*>)?\s*\(([^)]*)\)"),
        ]
        import_patterns = [
            re.compile(r"use\s+([\w:]+)"),
        ]
        const_pattern = re.compile(r"(?:pub\s+)?const\s+([A-Z][A-Z_0-9]+)\s*:\s*[^=]+=\s*(.+?);")
        entry_checks = [r"fn\s+main\s*\("]

    elif language == "go":
        func_patterns = [
            re.compile(r"func\s+(?:\([^)]*\)\s+)?(\w+)\s*\(([^)]*)\)"),
        ]
        import_patterns = [
            re.compile(r'"([\w./]+)"'),
        ]
        const_pattern = re.compile(r"(\w+)\s*=\s*(.+)")
        entry_checks = [r"func\s+main\s*\("]

    elif language == "shell":
        func_patterns = [
            re.compile(r"(?:function\s+)?(\w+)\s*\(\s*\)\s*\{"),
        ]
        import_patterns = [
            re.compile(r"(?:source|\.\s+)\s+(.+)"),
        ]
        const_pattern = re.compile(r"(?:readonly\s+)?([A-Z][A-Z_0-9]+)=(.+)")
        entry_checks = []

    elif language == "java":
        func_patterns = [
            re.compile(r"(?:public|private|protected)?\s*(?:static\s+)?[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)"),
        ]
        import_patterns = [
            re.compile(r"import\s+([\w.]+);"),
        ]
        const_pattern = re.compile(r"(?:static\s+)?final\s+\w+\s+([A-Z][A-Z_0-9]+)\s*=\s*(.+?);")
        entry_checks = [r"public\s+static\s+void\s+main"]

    elif language == "ruby":
        func_patterns = [
            re.compile(r"def\s+(\w+[!?]?)\s*(?:\(([^)]*)\))?"),
        ]
        import_patterns = [
            re.compile(r"require\s+['\"]([^'\"]+)['\"]"),
        ]
        const_pattern = re.compile(r"([A-Z][A-Z_0-9]+)\s*=\s*(.+)")
        entry_checks = [r"if\s+__FILE__\s*==\s*\$0", r"if\s+\$PROGRAM_NAME"]

    else:
        # Generic fallback
        func_patterns = [
            re.compile(r"(?:def|func|function|fn|sub|proc)\s+(\w+)\s*\(([^)]*)\)"),
        ]
        import_patterns = [
            re.compile(r"(?:import|require|include|use)\s+['\"]?([^'\";\s]+)"),
        ]
        const_pattern = re.compile(r"([A-Z][A-Z_0-9]{2,})\s*=\s*(.+)")
        entry_checks = [r"(?:def|func|function|fn)\s+main"]

    # Extract functions
    for i, line in enumerate(lines, 1):
        for pat in func_patterns:
            m = pat.search(line)
            if m:
                name = m.group(1)
                args_str = m.group(2) if m.lastindex >= 2 else ""
                args = [a.strip() for a in args_str.split(",") if a.strip()] if args_str else []

                # Estimate function length
                line_count = 1
                if i < len(lines):
                    brace_depth = line.count("{") - line.count("}")
                    for j in range(i, min(i + 500, len(lines))):
                        line_count += 1
                        brace_depth += lines[j].count("{") - lines[j].count("}")
                        if brace_depth <= 0 and "{" in source:
                            break
                        # For Python-style (indentation)
                        if language in ("python", "ruby") and j > i:
                            if lines[j].strip() and not lines[j].startswith((" ", "\t")):
                                line_count = j - i
                                break

                functions.append({
                    "name": name,
                    "args": args,
                    "line_number": i,
                    "line_count": line_count,
                    "has_return": bool(re.search(r"\breturn\b", "\n".join(lines[i-1:i-1+line_count]))),
                    "docstring": "",
                })

    # Extract imports
    for line in lines:
        for pat in import_patterns:
            m = pat.search(line)
            if m:
                mod = m.group(1)
                imports.append({
                    "module": mod,
                    "alias": None,
                    "is_stdlib": False,  # Can't reliably determine for non-Python
                })

    # Extract constants
    for i, line in enumerate(lines, 1):
        if const_pattern:
            m = const_pattern.search(line)
            if m:
                constants.append({
                    "name": m.group(1),
                    "value": m.group(2).strip()[:200],
                    "line_number": i,
                })

    # Check entry points
    for check in entry_checks:
        if re.search(check, source):
            entry_points.append(re.sub(r"\\[sb]", "", check).replace("\\s+", " "))

    # Classes (generic)
    class_pat = re.compile(r"(?:class|struct|type)\s+(\w+)")
    for i, line in enumerate(lines, 1):
        m = class_pat.search(line)
        if m:
            classes.append({
                "name": m.group(1),
                "methods": [],
                "line_number": i,
                "bases": [],
            })

    return {
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "constants": constants,
        "entry_points": entry_points,
    }


def detect_io_patterns(source):
    """Detect I/O patterns in source code."""
    return {
        "reads_stdin": bool(STDIN_PATTERNS.search(source)),
        "writes_stdout": bool(STDOUT_PATTERNS.search(source)),
        "reads_files": bool(FILE_READ_PATTERNS.search(source)),
        "writes_files": bool(FILE_WRITE_PATTERNS.search(source)),
        "network": bool(NETWORK_PATTERNS.search(source)),
        "database": bool(DATABASE_PATTERNS.search(source)),
    }


def detect_control_flow(source):
    """Analyze control flow patterns."""
    has_loops = bool(re.search(r"\b(for|while|loop|each|do)\b", source))
    has_recursion = False

    # Simple recursion detection: function calls its own name
    func_names = re.findall(r"(?:def|function|fn|func)\s+(\w+)", source)
    for name in func_names:
        # Check if name appears in a call context after its definition
        pattern = re.compile(rf"\b{re.escape(name)}\s*\(", re.MULTILINE)
        matches = pattern.findall(source)
        if len(matches) > 1:  # More than just the definition
            has_recursion = True
            break

    # State machine detection
    has_state_machine = bool(
        re.search(r'\bstate\s*=\s*["\']', source)
        or re.search(r"\bState\.", source)
        or re.search(r"while.*state", source, re.IGNORECASE)
    )

    # Nesting depth estimation
    max_depth = 0
    current_depth = 0
    for line in source.split("\n"):
        stripped = line.strip()
        # Count indentation-based nesting (Python, Ruby)
        indent = len(line) - len(line.lstrip())
        indent_depth = indent // 4
        if indent_depth > max_depth:
            max_depth = indent_depth
        # Count brace-based nesting
        current_depth += stripped.count("{") - stripped.count("}")
        if current_depth > max_depth:
            max_depth = current_depth

    return {
        "has_loops": has_loops,
        "has_recursion": has_recursion,
        "has_state_machine": has_state_machine,
        "max_nesting_depth": min(max_depth, 20),
    }


def detect_dependencies(source, imports_list):
    """Identify external packages and system calls."""
    external = []
    for imp in imports_list:
        if not imp.get("is_stdlib", False):
            mod = imp["module"].split(".")[0]
            if mod not in external:
                external.append(mod)

    system_calls = []
    if re.search(r"\b(subprocess|os\.system|os\.popen|exec\(|execvp|system\()\b", source):
        system_calls.append("subprocess/system calls")
    if re.search(r"\b(os\.remove|os\.unlink|shutil\.rmtree|unlink)\b", source):
        system_calls.append("file deletion")
    if re.search(r"\b(os\.environ|getenv|process\.env)\b", source):
        system_calls.append("environment variables")

    return {
        "external_packages": external,
        "system_calls": system_calls,
    }


def estimate_complexity(functions, control_flow, source):
    """Estimate overall code complexity."""
    num_functions = len(functions)
    total_lines = len(source.split("\n"))
    max_depth = control_flow.get("max_nesting_depth", 0)

    if total_lines < 50 and num_functions <= 3 and max_depth <= 2:
        return "simple"
    elif total_lines < 200 and num_functions <= 10 and max_depth <= 4:
        return "moderate"
    else:
        return "complex"


def detect_warnings(source, imports_list, io_patterns):
    """Generate warnings about potential issues."""
    warnings = []

    # GUI detection
    for imp in imports_list:
        mod = imp["module"].split(".")[0]
        if mod in GUI_IMPORTS:
            warnings.append(f"Uses GUI library '{mod}' — skills are terminal-only")

    # Network
    if io_patterns["network"]:
        ext_mods = [imp["module"] for imp in imports_list if not imp.get("is_stdlib")]
        net_mods = [m for m in ext_mods if any(n in m.lower() for n in ["request", "http", "aiohttp", "axios", "fetch"])]
        if net_mods:
            warnings.append(f"Network operations detected via {', '.join(net_mods)}")

    # Database
    if io_patterns["database"]:
        warnings.append("Database operations detected — may need special handling")

    # Large file
    line_count = len(source.split("\n"))
    if line_count > 500:
        warnings.append(f"Large file ({line_count} lines) — consider compiling in parts")

    # Threading/multiprocessing
    if re.search(r"\b(threading|multiprocessing|asyncio|tokio|goroutine|Thread|pthread)\b", source):
        warnings.append("Concurrent/async code detected — will be serialized in skill")

    return warnings


def analyze(file_path, language_override=None):
    """Main analysis entry point."""
    file_path = os.path.abspath(file_path)

    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
    except Exception as e:
        return {"error": f"Could not read file: {e}"}

    language = language_override or detect_language(file_path)

    # Structural analysis
    if language == "python":
        structure = analyze_python(source, file_path)
        if structure.get("fallback") == "regex":
            structure = analyze_with_regex(source, language)
    else:
        structure = analyze_with_regex(source, language)

    # Pattern detection
    io_patterns = detect_io_patterns(source)
    control_flow = detect_control_flow(source)
    dependencies = detect_dependencies(source, structure.get("imports", []))
    complexity = estimate_complexity(
        structure.get("functions", []), control_flow, source
    )
    warnings = detect_warnings(source, structure.get("imports", []), io_patterns)

    return {
        "language": language,
        "file_path": file_path,
        "total_lines": len(source.split("\n")),
        "functions": structure.get("functions", []),
        "classes": structure.get("classes", []),
        "imports": structure.get("imports", []),
        "constants": structure.get("constants", []),
        "entry_points": structure.get("entry_points", []),
        "io_patterns": io_patterns,
        "control_flow": control_flow,
        "dependencies": dependencies,
        "complexity_estimate": complexity,
        "warnings": warnings,
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python analyze.py <source-file> [--language <lang>]"}))
        sys.exit(1)

    file_path = sys.argv[1]
    language_override = None

    if "--language" in sys.argv:
        idx = sys.argv.index("--language")
        if idx + 1 < len(sys.argv):
            language_override = sys.argv[idx + 1]

    result = analyze(file_path, language_override)
    print(json.dumps(result, indent=2))

    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
