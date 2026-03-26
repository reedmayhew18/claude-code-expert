---
name: sudo
description: Run commands requiring sudo in a visible terminal window where the user can enter their password interactively. Use when a command needs root privileges, elevated permissions, "sudo", "install system package", "apt install", "dnf install", "pacman -S", or any operation requiring admin access.
argument-hint: "command -- description of what it does"
disable-model-invocation: true
allowed-tools: Bash, Read
---

# Sudo — Interactive Elevated Command Runner

## Goal
Execute a privileged command in a separate terminal window where the user can authenticate with their password, then capture and report the results back to the Claude Code session. Success = command runs with sudo, exit code and output are captured, and the user never has to leave their Claude session to check results.

## Dependencies
- **Tools:** Bash (launch terminal, poll log), Read (read log file)
- **Terminal emulator** (auto-detected, checked in this order):
  1. `gnome-terminal` (GNOME/Ubuntu default)
  2. `xfce4-terminal` (XFCE)
  3. `konsole` (KDE)
  4. `xterm` (X11 fallback)
  5. `cmd.exe` via WSL interop (Windows/WSL)
  6. `osascript` + Terminal.app (macOS)
- **No external packages required** — uses system terminal

## Context
- NEVER run `sudo` directly in a Bash tool call — it cannot handle interactive password prompts
- This skill exists specifically to bridge that gap safely
- The terminal window is visible to the user so they can see exactly what's happening

## Process

### Step 1: Parse Arguments
Arguments arrive as `$ARGUMENTS`. Parse as:
```
COMMAND -- DESCRIPTION
```
If no `--` separator, treat entire argument as the command and generate a brief description.

**CHECKPOINT:** Show the user the command and description BEFORE launching. Ask: "I'll run `sudo COMMAND` in a terminal window. Proceed?"

### Step 2: Detect Terminal Emulator
```bash
detect_terminal() {
  if command -v gnome-terminal &>/dev/null; then echo "gnome-terminal"
  elif command -v xfce4-terminal &>/dev/null; then echo "xfce4-terminal"
  elif command -v konsole &>/dev/null; then echo "konsole"
  elif command -v xterm &>/dev/null; then echo "xterm"
  elif grep -qi microsoft /proc/version 2>/dev/null; then echo "wsl"
  elif [[ "$(uname)" == "Darwin" ]]; then echo "macos"
  else echo "none"
  fi
}
```

### Step 3: Generate Runner Script
Write to `/tmp/claude_sudo_runner_TIMESTAMP.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail

LOGFILE="/tmp/claude_sudo_TIMESTAMP.log"
COMMAND="THE_COMMAND"
DESCRIPTION="THE_DESCRIPTION"

echo "========================================" | tee "$LOGFILE"
echo " Claude Code — Sudo Runner" | tee -a "$LOGFILE"
echo "========================================" | tee -a "$LOGFILE"
echo "" | tee -a "$LOGFILE"
echo " Purpose: $DESCRIPTION" | tee -a "$LOGFILE"
echo " Command: sudo $COMMAND" | tee -a "$LOGFILE"
echo " Log:     $LOGFILE" | tee -a "$LOGFILE"
echo "" | tee -a "$LOGFILE"
echo "========================================" | tee -a "$LOGFILE"
echo "" | tee -a "$LOGFILE"

sudo $COMMAND 2>&1 | tee -a "$LOGFILE"
EXIT_CODE=${PIPESTATUS[0]}

echo "" | tee -a "$LOGFILE"
echo "========================================" | tee -a "$LOGFILE"
if [ $EXIT_CODE -eq 0 ]; then
  echo " DONE (exit code 0)" | tee -a "$LOGFILE"
else
  echo " FAILED (exit code $EXIT_CODE)" | tee -a "$LOGFILE"
fi
echo "========================================" | tee -a "$LOGFILE"
echo "EXIT_CODE=$EXIT_CODE" >> "$LOGFILE"

echo ""
echo "Press Enter to close this window..."
read -r
```
Make executable: `chmod +x /tmp/claude_sudo_runner_*.sh`

### Step 4: Launch in Detected Terminal
```bash
TERM_TYPE=$(detect_terminal)
SCRIPT="/tmp/claude_sudo_runner_XXXXX.sh"

case "$TERM_TYPE" in
  gnome-terminal) gnome-terminal -- bash -c "$SCRIPT" ;;
  xfce4-terminal) xfce4-terminal -e "bash -c '$SCRIPT'" ;;
  konsole)        konsole -e bash -c "$SCRIPT" ;;
  xterm)          xterm -e bash -c "$SCRIPT" ;;
  wsl)            cmd.exe /c start bash -c "$SCRIPT" ;;
  macos)          osascript -e "tell application \"Terminal\" to do script \"$SCRIPT\"" ;;
  none)           echo "No supported terminal found" && exit 1 ;;
esac
```

### Step 5: Poll for Completion
Wait for the log file to contain `EXIT_CODE=` (up to 120 seconds):
```bash
for i in $(seq 1 60); do
  if grep -q '^EXIT_CODE=' "$LOGFILE" 2>/dev/null; then break; fi
  sleep 2
done
```

### Step 6: Read and Report Results
Read the log file with the Read tool. Report:
- The command that was run
- Exit code (0 = success, non-zero = failure)
- Relevant output
- If timeout: tell user the command may still be running and point to the log file

**CHECKPOINT:** Present the results to the user. Ask: "The command completed with exit code X. Does everything look correct, or do you need to investigate further?"

### Step 7: Clean Up
```bash
rm -f /tmp/claude_sudo_runner_*.sh
```
Keep the log file for reference.

## Output
- Results reported inline in the conversation (exit code + command output)
- Log file persists at `/tmp/claude_sudo_TIMESTAMP.log` for reference
- Runner script cleaned up automatically

## Important Rules
- ALWAYS show the command BEFORE launching — no surprise sudo operations
- NEVER run sudo directly in a Bash tool call
- Quote all variables in the generated script (handle paths with spaces)
- The terminal launch must NOT block — fire-and-forget so polling can begin
- If no terminal is detected, report the error clearly and suggest the user run the command manually
