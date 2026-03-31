# Language Profiles

Per-language analysis strategies and quirks for the CompileToSkill transpiler.

## Tier 1: Full Support (Run + Fuzz + Profile)

### Python (.py)
- **Parser**: Use `ast` module for accurate structural analysis
- **Runner**: `python3 <file>` or import and call functions directly
- **Fuzzer**: Can introspect function signatures via `inspect` module
- **Stdlib detection**: Check against `sys.stdlib_module_names` (3.10+) or known list
- **Common patterns**:
  - `if __name__ == "__main__"` → entry point
  - `argparse` / `sys.argv` → CLI arguments map to `$ARGUMENTS`
  - `input()` → reads stdin, skill should ask user for input
  - `print()` → stdout output, skill presents to user
  - Decorators: often indicate frameworks (Flask `@app.route`, etc.)
- **Watch for**: virtual env dependencies, `__init__.py` imports, relative imports

### JavaScript (.js, .mjs)
- **Parser**: Regex-based (no native AST in Python)
- **Runner**: `node <file>`
- **Fuzzer**: Run with `process.argv` inputs or pipe to stdin
- **Common patterns**:
  - `function name()` or `const name = () =>` → functions
  - `require()` / `import` → dependencies
  - `process.argv` → CLI args
  - `console.log()` → stdout
  - `readline` → stdin
  - `module.exports` / `export` → library (may need wrapper to run)
- **Watch for**: Node.js version requirements, ESM vs CommonJS

### TypeScript (.ts, .tsx)
- **Parser**: Same regex as JS plus type annotations
- **Runner**: Try `npx tsx <file>`, `npx ts-node <file>`, or `node --loader ts-node/esm <file>`
- **Fuzzer**: Same as JS after compilation
- **Watch for**: May need `tsconfig.json`, type-only imports

## Tier 2: Compile + Run

### C (.c, .h)
- **Parser**: Regex for `#include`, `#define`, function declarations
- **Compiler**: `gcc -o /tmp/compile_target <file> -lm` (link math library)
- **Runner**: `/tmp/compile_target <args>`
- **Fuzzer**: Feed args via argv and stdin
- **Common patterns**:
  - `int main(` → entry point
  - `#define NAME value` → constants (Bake In)
  - `scanf` / `fgets` → stdin
  - `printf` → stdout
  - `FILE*` operations → file I/O
- **Watch for**: Multiple source files, header dependencies, platform-specific code

### C++ (.cpp, .hpp, .cc)
- **Parser**: Regex (similar to C plus classes, templates)
- **Compiler**: `g++ -o /tmp/compile_target <file> -std=c++17`
- **Common patterns**:
  - `class Name {` → classes
  - `std::cin` / `std::cout` → I/O
  - `#include <vector>` etc. → STL usage
  - Templates → likely complex, lean toward Script

### Rust (.rs)
- **Parser**: Regex for `fn`, `struct`, `impl`, `use`, `mod`
- **Compiler**: `rustc -o /tmp/compile_target <file>` (single file) or detect Cargo project
- **Common patterns**:
  - `fn main()` → entry point
  - `use std::io` → stdin/stdout
  - `std::env::args()` → CLI args
  - `match` expressions → decision trees (often → Prose)
  - `Result<T, E>` → error handling (→ Prose)
  - `const` / `static` → constants (→ Bake In)
- **Watch for**: Cargo dependencies, lifetime annotations, async code

### Go (.go)
- **Parser**: Regex for `func`, `type`, `import`, `package`
- **Compiler**: `go build -o /tmp/compile_target <file>`
- **Common patterns**:
  - `func main()` → entry point
  - `fmt.Scan` / `fmt.Print` → I/O
  - `os.Args` → CLI args
  - `switch` statements → decision trees (→ Prose)
  - `const ( ... )` blocks → constants (→ Bake In)
  - `error` returns → error handling (→ Prose)

## Tier 3: Static Analysis Only

### Java (.java)
- **Regex patterns**: `public class`, `public static void main`, `import`
- **No runtime**: Would need JDK, too heavy for fuzzing
- **Lean toward**: Prose translation of business logic, Script for computation

### Ruby (.rb)
- **Regex patterns**: `def`, `class`, `require`, `ARGV`
- **Runner**: `ruby <file>` if available
- **Similar to Python** in patterns

### PHP (.php)
- **Regex patterns**: `function`, `class`, `$_GET`, `echo`
- **Runner**: `php <file>` if available
- **Watch for**: Web-specific code (HTML mixing, `$_POST`)

### Shell/Bash (.sh, .bash)
- **Regex patterns**: function definitions, variable assignments, conditionals
- **Runner**: `bash <file>`
- **Almost everything → Prose**: Shell scripts are already close to natural language instructions
- **Watch for**: System-specific commands, pipes, redirects

### Any Other Language
- **Approach**: Basic regex for function-like patterns (`def`, `func`, `function`, `fn`, `sub`, `proc`)
- **Extract**: Imports, constants (ALL_CAPS), entry points
- **Default strategy**: Lean heavily toward Prose since we can't fuzz

## Language-Agnostic Signals

These patterns suggest classification regardless of language:

| Pattern | Signal | Likely Strategy |
|---------|--------|-----------------|
| ALL_CAPS variable | Constant | Bake In |
| `if/else` chain on strings | Decision tree | Prose |
| Math with `/`, `%`, `**`, `pow` | Computation | Simulate (simple) or Script (complex) |
| `regex`, `re.`, `Regex::` | Pattern matching | Prose (simple) or Script (complex) |
| `sort`, `sorted`, `.sort()` | Sorting | Simulate (<20 items) or Script (large) |
| `random`, `rand`, `Math.random` | Non-deterministic | Prose ("generate a random...") |
| `sleep`, `time.sleep`, `setTimeout` | Timing | Skip/warn |
| `open(`, `fopen`, `File.open` | File I/O | Simulate (Claude has file tools) |
| `http`, `fetch`, `requests`, `curl` | Network | Prose (instruct Claude to use WebFetch) |
| `SELECT`, `INSERT`, `query(` | Database | Prose or Script depending on complexity |
