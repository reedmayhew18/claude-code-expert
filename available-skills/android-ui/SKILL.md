---
name: android-ui
description: Design and implement minimal, thoughtful Android UI with Material Design 3. Use when the user says "Android UI", "design a screen", "layout", "Jetpack Compose", "XML layout", "material design", "Android interface", or needs to build Android screens, components, or navigation.
argument-hint: "[screen name or UI description]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Android UI Design

## Goal
Produce clean, accessible, minimal Android UI that follows Material Design 3. Every element earns its place. Success = screens render correctly, pass accessibility checks (touch targets ≥48dp, content descriptions present, contrast ratios met), and the user approves the visual approach before implementation.

## Dependencies
- **Tools:** Read, Write, Edit, Bash (for build verification), Grep, Glob
- **Frameworks:** Jetpack Compose (preferred) or XML layouts with ConstraintLayout
- **Libraries:** Material 3 (`com.google.android.material:material`), Compose Material 3

## Context
- Read existing project to detect: Compose vs XML, existing theme, navigation pattern
- Check `themes.xml` or `Theme.kt` for current color scheme and typography
- Follow existing conventions if project has established patterns

## Process

### Step 1: Understand the Screen
Ask the user:
- What is this screen's single purpose?
- What data does it display or collect?
- What actions can the user take?
- Where does the user come from, and where do they go next?
- Compose or XML? (auto-detect from project if possible)

**CHECKPOINT:** Confirm understanding before designing. Ask: "Here's what I understand you need: [summary]. Is that right, or should I adjust scope?"

### Step 2: Design the Layout

**Minimal UI Principles:**
- Whitespace is a feature, not wasted space
- One primary action per screen (FAB or prominent button)
- Secondary actions in overflow or bottom sheet
- Content hierarchy through typography weight, not decoration
- No unnecessary borders, shadows, or dividers — let spacing do the work

**CHECKPOINT:** Present the layout plan (ASCII mockup or description) before writing code. Ask: "Here's the proposed layout. Does this match what you need?"

### Step 3: Implement

**Jetpack Compose (preferred):**
```kotlin
@Composable
fun ScreenName(
    viewModel: ScreenViewModel = hiltViewModel(),
    onNavigate: (Route) -> Unit
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    // Scaffold with TopAppBar, content, FAB as needed
}
```

**XML (if project uses it):**
- ConstraintLayout as root (flat hierarchy, no nested LinearLayouts)
- Use `MaterialToolbar`, `MaterialButton`, `TextInputLayout`
- Dimensions in dp, text in sp, margins from Material spacing scale (8dp increments)

### Step 4: Accessibility
- `contentDescription` on all non-decorative images
- Touch targets ≥ 48dp (`minHeight`/`minWidth`)
- Color contrast ≥ 4.5:1 for text, ≥ 3:1 for UI components
- Support TalkBack navigation order
- `importantForAccessibility` set appropriately

### Step 5: Responsive Design
- Test portrait and landscape
- Handle different screen sizes (compact, medium, expanded)
- Use `WindowSizeClass` in Compose or resource qualifiers in XML

### Step 6: Theme
- Support dark and light themes via Material 3 dynamic color or custom `ColorScheme`
- Typography: `MaterialTheme.typography` — body for content, title for headers, label for UI elements
- No hardcoded colors or text sizes in layouts

**CHECKPOINT:** Show the implemented UI (describe what it looks like or provide a screenshot path). Ask: "Here's the result. Any adjustments?"

## Output

**Save locations:**
- Compose: `app/src/main/java/<package>/ui/<feature>/` — one file per screen (e.g., `HomeScreen.kt`)
- XML layouts: `app/src/main/res/layout/` — `fragment_<name>.xml` or `activity_<name>.xml`
- Theme updates: `app/src/main/res/values/themes.xml` and `themes.xml (night)`, or `ui/theme/Theme.kt`
- String resources: `app/src/main/res/values/strings.xml`

**Deliverables:**
- Screen composable or layout file(s) written to project
- ViewModel stub if state management is needed
- Theme/color updates if new tokens required
- Preview composable (`@Preview`) or layout preview instructions so the user can verify visually without running the app
- No files written outside the Android project directory
