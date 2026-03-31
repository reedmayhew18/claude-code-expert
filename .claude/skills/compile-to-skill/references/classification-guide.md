# Classification Guide

Detailed heuristics for classifying code operations into the four compilation strategies. The overriding principle: **minimize scripts, maximize prose/simulate/bake-in**.

## Decision Flowchart

For each operation, walk through these questions in order:

### 1. Is it static data?
**→ Bake In**

Signs:
- ALL_CAPS variable names
- `const`, `final`, `#define`, `static readonly`
- Dictionary/map with hardcoded keys and values
- Enum definitions
- Configuration that doesn't change at runtime
- Lookup tables (state names, error codes, unit conversions)

Format: Embed as markdown tables in SKILL.md or `references/*.md`

### 2. Can Claude do it with zero ambiguity?
**→ Simulate**

Claude reliably handles:
- Basic arithmetic: `a + b`, `a * b`, `total / count`
- String concatenation and formatting: `f"Hello, {name}!"`
- File reading and writing (via Read/Write tools)
- JSON/YAML parsing and creation
- Simple list operations: append, filter, map on <20 items
- Dictionary lookups by key
- Boolean logic: `if a and b`, `not c`
- Counting and summing small collections
- Date formatting (not computation)
- URL construction from parts

### 3. Can it be taught with instructions and examples?
**→ Prose**

Convert to prose when:
- The logic is a decision tree with <10 branches
- Each branch depends on semantic/categorical conditions (not numerical precision)
- The behavior can be fully described with 3-5 worked examples
- It's validation logic (checking formats, ranges, required fields)
- It's a workflow (step 1, then step 2, then...)
- It's error handling (if X goes wrong, do Y)
- It's a state machine with <6 states

**Prose quality test**: Write the instructions, then ask "Would a smart intern follow these correctly 95% of the time?" If yes → Prose works.

### 4. Does it REQUIRE computational precision?
**→ Script (last resort)**

Only use Script when ALL of these are true:
- The operation involves math that must be exact (floating-point, large numbers)
- OR the algorithm has too many edge cases to teach by example (>20 paths)
- OR the fuzzer showed unpredictable outputs that can't be pattern-matched
- AND you tried Prose/Simulate/Bake-In first and they genuinely don't work

## Per-Pattern Classification

### Conditionals (if/else)

```python
# PROSE — semantic branching
if user.role == "admin":
    grant_all_access()
elif user.role == "editor":
    grant_edit_access()
else:
    grant_read_only()
```
→ Prose: "If the user is an admin, grant full access. If editor, grant edit access. Otherwise, read-only."

```python
# SIMULATE — simple numeric check
if age >= 18:
    return "adult"
return "minor"
```
→ Simulate: Claude can check if a number is >= 18.

```python
# SCRIPT — complex numeric boundary
if 0 < x < 0.001 and not math.isnan(x) and x != float('inf'):
    return math.log(1 + x)  # Taylor approximation region
```
→ Script: Floating-point edge cases require real computation.

### Loops

```python
# PROSE — iterating over a workflow
for item in shopping_cart:
    validate(item)
    calculate_tax(item)
    apply_discount(item)
```
→ Prose: "For each item in the cart: 1) Validate it, 2) Calculate tax, 3) Apply discounts"

```python
# BAKE IN — iterating to build a lookup
result = {}
for state in STATES:
    result[state.abbr] = state.name
```
→ Bake In: Pre-compute the mapping and embed it.

```python
# SCRIPT — computational loop
total = 0
for i in range(1, n+1):
    total += 1 / (i ** 2)  # Basel problem approximation
```
→ Script: Precision-dependent mathematical series.

### String Operations

```python
# SIMULATE — simple formatting
output = f"Total: ${amount:,.2f}"
```
→ Simulate: Claude handles string formatting.

```python
# PROSE — pattern-based validation
if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
    return True
```
→ Prose (usually): "Check if the input looks like a valid email: must have text, then @, then a domain with a dot extension." Claude's judgment handles most email validation.

```python
# SCRIPT — complex regex extraction
matches = re.findall(r'(?:(?:\+|00)(\d{1,3})[-.\s]?)?(?:\((\d{1,4})\)[-.\s]?)?(\d{1,4})[-.\s]?(\d{1,4})[-.\s]?(\d{1,9})', text)
```
→ Script: Complex regex with capture groups — too error-prone for prose.

### Data Transformations

```python
# SIMULATE — simple key mapping
output = {"name": data["first_name"] + " " + data["last_name"]}
```
→ Simulate: Simple field mapping.

```python
# PROSE — format conversion with clear rules
csv_rows = []
for record in json_data:
    csv_rows.append(f"{record['id']},{record['name']},{record['value']}")
```
→ Prose: "Convert the JSON records to CSV format with columns: id, name, value"

```python
# SCRIPT — complex transformation
df = pd.DataFrame(data)
result = df.pivot_table(index='category', values='amount', aggfunc='sum')
```
→ Script: Pivot tables involve aggregation that must be precise.

### Error Handling

```python
# ALWAYS PROSE
try:
    result = process(data)
except FileNotFoundError:
    print("File not found. Please check the path.")
except ValueError:
    print("Invalid value. Expected a number.")
except Exception as e:
    print(f"Unexpected error: {e}")
```
→ Prose: "If the file doesn't exist, tell the user to check the path. If the value is invalid, ask for a number. For any other error, report what went wrong."

## Confidence Scoring

| Scenario | Confidence |
|----------|-----------|
| ALL_CAPS constant → Bake In | 0.95-0.99 |
| Simple string format → Simulate | 0.85-0.95 |
| If/elif on categories → Prose | 0.80-0.90 |
| Complex regex → Script | 0.85-0.95 |
| Floating-point math → Script | 0.90-0.98 |
| Ambiguous: could be Prose or Script | 0.60-0.75 |

When confidence is below 0.75, present the operation to the user at the checkpoint and ask them to decide.
