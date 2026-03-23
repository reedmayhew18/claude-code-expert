---
name: android-setup
description: Set up Android development environment with SDK, ADB, and build tools. Use when the user says "set up Android", "install Android SDK", "configure ADB", "Android development environment", "I want to build an Android app", or needs to compile/debug Android apps from the command line.
argument-hint: "[full|verify|emulator]"
disable-model-invocation: true
allowed-tools: Bash, Read, Write
---

# Android Environment Setup

## Goal
Produce a working Android development environment where the user can compile, install, and debug Android apps entirely from the command line. Success = `adb version` works, `sdkmanager --list` works, and `./gradlew assembleDebug` compiles a project.

## Dependencies
- **Tools:** Bash (installation commands, PATH config), Read (check existing configs), Write (update shell profiles)
- **System requirements:** Java 17+ (OpenJDK), ~5GB disk space for SDK
- **Python projects (Buildozer/Kivy):** Will create a venv — NEVER use --break-system-packages

## Context
- Detect OS first (Linux, macOS, Windows/WSL) — installation commands differ significantly
- Check for existing installations before installing anything
- Read user's shell profile (~/.bashrc, ~/.zshrc) to set environment variables

## Process

### Step 1: Detect Environment
```bash
uname -s                    # OS detection
java --version 2>/dev/null  # Java check
adb version 2>/dev/null     # Existing ADB check
echo $ANDROID_HOME          # Existing SDK check
```
Report what's found and what's missing.

### Step 2: Install Java (if missing)
| OS | Command |
|---|---|
| Ubuntu/Debian | `sudo apt install openjdk-17-jdk` |
| Fedora | `sudo dnf install java-17-openjdk-devel` |
| macOS | `brew install openjdk@17` |
| Arch | `sudo pacman -S jdk17-openjdk` |

Set `JAVA_HOME` in shell profile.

### Step 3: Install Android SDK Command-Line Tools
```bash
# Download latest cmdline-tools
mkdir -p $HOME/android-sdk/cmdline-tools
# Download from https://developer.android.com/studio#command-line-tools-only
# Unzip to $HOME/android-sdk/cmdline-tools/latest/
```

Set environment variables in shell profile:
```bash
export ANDROID_HOME=$HOME/android-sdk
export PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH
```

### Step 4: Install Required SDK Packages
```bash
sdkmanager --install "platform-tools" "build-tools;34.0.0" "platforms;android-34"
yes | sdkmanager --licenses  # Accept all licenses
```

**CHECKPOINT:** Show the user what was installed and the environment variables set. Ask: "SDK installed. Want me to also set up an emulator, or will you use a physical device via USB?"

### Step 5: Emulator Setup (if requested)
```bash
sdkmanager --install "system-images;android-34;google_apis;x86_64" "emulator"
avdmanager create avd -n dev_phone -k "system-images;android-34;google_apis;x86_64"
```

### Step 6: Python/Buildozer Setup (if requested)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install buildozer kivy
buildozer init
```
NEVER use `--break-system-packages`. Always venv.

### Step 7: Verify
Run verification checks:
```bash
java --version
adb version
sdkmanager --list | head -20
./gradlew --version  # if in a project
```

**CHECKPOINT:** Present verification results. Confirm everything works before finishing.

## Output
- Environment variables set in shell profile (persists across sessions)
- SDK installed at `$ANDROID_HOME`
- Verification report printed to user
- No files written to the project itself (system-level setup only)

## Common Issues
| Problem | Fix |
|---|---|
| `sdkmanager: command not found` | PATH not set — re-source shell profile |
| License not accepted | Run `yes \| sdkmanager --licenses` |
| JAVA_HOME not set | Add `export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))` |
| WSL: no USB access for ADB | Use `adb` from Windows side, or set up usbipd-win |
| Low disk space | Minimum 5GB needed for SDK + build tools |
