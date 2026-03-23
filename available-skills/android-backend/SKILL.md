---
name: android-backend
description: Write complete, tested Android backend logic with MVVM architecture. Use when the user says "Android backend", "ViewModel", "Room database", "API call", "repository pattern", "Android data layer", "write Android logic", or needs business logic, data persistence, or network calls in an Android app.
argument-hint: "[feature or data layer description]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Android Backend Logic

## Goal
Produce complete, tested backend code following MVVM architecture with Repository pattern. Success = all unit tests pass, integration tests pass, no runtime crashes on happy path and error paths, and the code compiles cleanly with `./gradlew assembleDebug`.

## Dependencies
- **Tools:** Read, Write, Edit, Bash (run tests, build), Grep, Glob
- **Libraries:** Kotlin Coroutines, Room (local DB), Retrofit + OkHttp (network), Hilt (DI), JUnit + Mockito (testing)
- **Build:** Gradle with Kotlin DSL preferred

## Context
- Read existing project architecture before adding code (check for existing ViewModels, Repositories, data sources)
- Follow established patterns — don't introduce a new architecture if one exists
- Check `build.gradle.kts` for existing dependencies before adding new ones

## Process

### Step 1: Define the Data Layer
Identify what data this feature needs:
- **Local:** Room entities, DAOs, database migrations
- **Remote:** API endpoints, request/response DTOs, Retrofit service interface
- **Repository:** Single source of truth combining local + remote

### Step 2: Write Tests First (TDD)
```kotlin
@Test
fun `when fetching users succeeds, state updates with user list`() = runTest {
    val fakeRepo = FakeUserRepository(Result.success(testUsers))
    val viewModel = UserViewModel(fakeRepo)
    viewModel.loadUsers()
    assertEquals(UiState.Success(testUsers), viewModel.state.value)
}

@Test
fun `when fetching users fails, state updates with error`() = runTest {
    val fakeRepo = FakeUserRepository(Result.failure(IOException("Network error")))
    val viewModel = UserViewModel(fakeRepo)
    viewModel.loadUsers()
    assertTrue(viewModel.state.value is UiState.Error)
}
```

Run tests — they MUST fail first.

**CHECKPOINT:** Show failing tests to user. Ask: "These tests define the expected behavior. Look correct before I implement?"

### Step 3: Implement

**Architecture layers:**
```
UI (Composable/Fragment) → ViewModel → Repository → DataSource (Room/Retrofit)
```

**ViewModel pattern:**
```kotlin
@HiltViewModel
class FeatureViewModel @Inject constructor(
    private val repository: FeatureRepository
) : ViewModel() {
    private val _state = MutableStateFlow<UiState<Data>>(UiState.Loading)
    val state: StateFlow<UiState<Data>> = _state.asStateFlow()

    fun loadData() {
        viewModelScope.launch {
            _state.value = repository.getData()
                .fold(
                    onSuccess = { UiState.Success(it) },
                    onFailure = { UiState.Error(it.message ?: "Unknown error") }
                )
        }
    }
}
```

**Error handling with sealed classes:**
```kotlin
sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
}
```

### Step 4: Run Tests
```bash
./gradlew testDebugUnitTest
```
All tests must pass. If any fail, fix implementation (not tests).

### Step 5: Integration Verification
```bash
./gradlew assembleDebug
```
Must compile cleanly. Check logcat for runtime errors if installed on device.

**CHECKPOINT:** Present test results and build status. Ask: "All tests pass and build succeeds. Ready to move on, or want me to add more test coverage?"

## Output
- Kotlin source files: ViewModel, Repository, DataSource, Entity/DTO classes
- Test files: unit tests for ViewModel and Repository
- Dependencies added to `build.gradle.kts` if needed
- All written to standard Android project structure (`src/main/java/`, `src/test/java/`)

## Patterns to Follow
- **One ViewModel per screen** — not per feature
- **Repository returns `Result<T>`** — never throws
- **Coroutines for async** — never callbacks or raw threads
- **Hilt for DI** — `@Inject constructor`, `@HiltViewModel`
- **StateFlow over LiveData** — for Compose compatibility
- **No business logic in UI layer** — if it's more than displaying data, it goes in ViewModel or Repository
