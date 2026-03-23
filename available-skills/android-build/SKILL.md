---
name: android-build
description: Build, compile, sign, install, and debug Android apps from the command line. Use when the user says "build APK", "compile Android", "install on device", "ADB", "debug Android", "sign APK", "release build", "Gradle build", or needs to get an Android app onto a device.
argument-hint: "[build|install|debug|sign|release]"
disable-model-invocation: true
allowed-tools: Bash, Read, Write
---

# Android Build & Debug

## Goal
Build, install, and debug Android apps entirely from the command line — no IDE required. Success = APK built, installed on device/emulator, and running without crashes. For release builds: signed APK ready for distribution.

## Dependencies
- **Tools:** Bash (Gradle, ADB commands), Read (config files), Write (signing configs)
- **Required CLI:** `./gradlew` (Gradle wrapper), `adb` (Android Debug Bridge), `keytool` (Java, for signing)
- **Environment:** ANDROID_HOME set, platform-tools in PATH (use `/android-setup` if not configured)

## Context
- Read `build.gradle.kts` for existing build config, signing configs, and product flavors before running any build
- Check `local.properties` for SDK path and verify `ANDROID_HOME` is set
- Detect connected devices with `adb devices` before install or debug steps
- If environment is not configured, stop and suggest: "Run `/skill-store install android-setup` then `/android-setup` first"

## Process

### Step 1: Determine Target Action
If `$ARGUMENTS` is provided, route directly to the matching command section below (build, install, debug, sign, release). If no argument is given, ask the user: "What would you like to do? Options: build, install, debug, sign, release."

### Step 2: Verify Environment
```bash
adb version
./gradlew --version
```
Confirm `ANDROID_HOME` is set and Gradle wrapper exists. If either fails, stop and guide setup.

**CHECKPOINT:** If environment checks fail, present the specific error and ask: "Your environment needs configuration. Should I walk you through fixing it, or would you like to run `/android-setup` first?"

### Step 3: Execute Command
Run the appropriate command section based on the user's target action:

#### Build
```bash
./gradlew clean assembleDebug
```
Report: APK location (`app/build/outputs/apk/debug/app-debug.apk`), file size, build time.

**CHECKPOINT:** Show build result (success or failure). If failed, display the error and ask: "Build failed. Want me to diagnose this error?"

#### Install
1. Check for connected device:
```bash
adb devices
```
2. If no device is listed, guide USB debugging setup or emulator launch before continuing.
3. Install the APK:
```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```
4. Launch the app:
```bash
adb shell am start -n com.package.name/.MainActivity
```

#### Debug
1. Start filtered logcat:
```bash
adb logcat -s "AppTag:V" "AndroidRuntime:E" "System.err:W" | head -200
```
2. Analyze common crash patterns:
   - `FATAL EXCEPTION` — read stack trace, identify the crashing line
   - `ANR` — main thread blocked; check for network or DB calls on main thread
   - `ClassNotFoundException` — ProGuard stripping; check rules
3. Collect device diagnostics:
```bash
adb shell getprop ro.build.version.sdk    # API level
adb shell dumpsys meminfo com.package.name # Memory usage
```

#### Sign
1. Read existing `build.gradle.kts` signing config to avoid duplicating keystore setup.
2. Present proposed keystore details to user.

**CHECKPOINT:** Confirm keystore details with user before generating. Ask: "I'll generate a keystore with these parameters. Confirm before I proceed — this is a security-critical operation."

3. Generate a self-signed release keystore (if none exists):
```bash
keytool -genkey -v -keystore release.keystore \
  -alias release -keyalg RSA -keysize 2048 -validity 10000
```
4. Configure signing in `build.gradle.kts` using environment variables — NEVER hardcode passwords:
```kotlin
signingConfigs {
    create("release") {
        storeFile = file("release.keystore")
        storePassword = System.getenv("KEYSTORE_PASSWORD")
        keyAlias = "release"
        keyPassword = System.getenv("KEY_PASSWORD")
    }
}
```
Note: `release.keystore` must be added to `.gitignore`.

#### Release
1. Run full test suite first:
```bash
./gradlew testReleaseUnitTest
```
2. Build signed release APK:
```bash
./gradlew assembleRelease
```
3. Verify APK signing:
```bash
apksigner verify --verbose app/build/outputs/apk/release/app-release.apk
```

**CHECKPOINT:** Present release APK path, file size, and signing verification output. Ask: "Release APK is ready. Confirm this looks correct before distribution."

### Step 4: Report Results
Summarize what was done: command run, outcome, file paths produced, and any warnings.

## Output
- **Build:** APK file path and size reported in terminal
- **Install:** Confirmation of successful installation and app launch
- **Debug:** Filtered logcat output with annotated crash analysis
- **Sign:** `release.keystore` file + updated signing config in `build.gradle.kts`
- **Release:** Signed APK at `app/build/outputs/apk/release/app-release.apk`, verified and ready for distribution

## Common Build Errors
| Error | Fix |
|---|---|
| `SDK location not found` | Set `sdk.dir` in `local.properties` or `ANDROID_HOME` env var |
| `Could not determine java version` | Set `JAVA_HOME` to JDK 17+ |
| `Dependency resolution failed` | Check internet connection; try `./gradlew --refresh-dependencies` |
| `minSdk version mismatch` | Align `minSdk` in `build.gradle.kts` with device API level |
| `Execution failed for task :app:lintDebug` | Add `lintOptions { abortOnError false }` or fix lint issues |
