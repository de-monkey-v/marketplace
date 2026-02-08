---
name: setup
description: Interactive setup wizard for the hyper-team plugin. Checks tmux installation, configures Agent Teams environment variable, and sets teammate display mode.
argument-hint: "[--language=eng]"
allowed-tools: Bash, Read, Write, Edit, Glob, AskUserQuestion
---

# /hyper-team:setup - Setup Wizard

Interactive setup wizard for the hyper-team plugin.

## Arguments

`$ARGUMENTS` may contain:
- `--language=eng` (default) - English output
- `--language=kor` - Korean output

Parse the language from arguments. Default to English.

---

## Language Resolution

1. Check `$ARGUMENTS` for `--language=eng` or `--language=kor` → use if present
2. Read `.hyper-team/metadata.json` → use `language` field if file exists
3. Default: `eng`

Produce all user-facing output in the resolved language.

---

## Step 1: Detect Shell Environment

```
Bash: echo $SHELL
```

Determine if the user uses bash or zsh:
- If contains "zsh": RC_FILE=~/.zshrc
- If contains "bash": RC_FILE=~/.bashrc
- Otherwise: Ask the user which shell config file they use.

---

## Step 2: Language Preference

Ask the user for their preferred language:

<AskUserQuestion>
- question: "Which language do you prefer for plugin outputs?"
- header: "Language"
- options:
  - label: "English (default)"
    description: "All plugin outputs will be in English"
  - label: "Korean (한국어)"
    description: "All plugin outputs will be in Korean (한국어로 출력)"
</AskUserQuestion>

Based on the user's choice:
1. Create `.hyper-team` directory: `mkdir -p .hyper-team`
2. Write `.hyper-team/metadata.json`:
   - If "English" selected: `{ "language": "eng" }`
   - If "Korean" selected: `{ "language": "kor" }`

---

## Step 3: Check tmux Installation

Run the following command to check if tmux is installed:

```
Bash: which tmux
```

<instructions>
**If tmux is NOT found:**

Detect the user's OS:

```
Bash: uname -s
```

Then show the appropriate install command based on OS:
- **Linux (Debian/Ubuntu)**: `sudo apt install tmux`
- **Linux (RHEL/Fedora)**: `sudo dnf install tmux`
- **Linux (Arch)**: `sudo pacman -S tmux`
- **macOS**: `brew install tmux`

```
AskUserQuestion:
- question: "tmux is not installed. Would you like to install it now?"
- header: "tmux"
- options:
  - label: "Yes, install now (Recommended)"
    description: "Run the install command for your OS"
  - label: "No, I'll install it later"
    description: "Skip tmux installation - in-process mode will be used instead"
```

If user chooses to install, run the appropriate install command for their OS.

**If tmux IS found:**

Report the tmux version:

```
Bash: tmux -V
```
</instructions>

---

## Step 4: Configure CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS

Check the current settings files:

```
Read: ~/.claude/settings.json
```

```
Read: .claude/settings.json
```

<instructions>
Check if `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` is already set to `"1"` in either settings file.

**If already set:**

Report that Agent Teams is already enabled and continue to the next step.

**If NOT set:**

```
AskUserQuestion:
- question: "Where should Agent Teams be enabled?"
- header: "Scope"
- options:
  - label: "User-level (Recommended)"
    description: "Enables for all projects in ~/.claude/settings.json"
  - label: "Project-level"
    description: "Enables only for this project in .claude/settings.json"
```

Then add the configuration using Edit or Write tool.

The required setting is:
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

**If the file already has an `env` key**, merge the new variable into it. Do NOT overwrite existing env vars.

**If the file does not exist**, create it with the full structure.
</instructions>

---

## Step 5: Configure Teammate Mode

```
AskUserQuestion:
- question: "Which display mode do you prefer for teammates?"
- header: "Mode"
- options:
  - label: "tmux (Recommended)"
    description: "Each teammate gets its own tmux pane - see all at once"
  - label: "in-process"
    description: "All teammates run within the main terminal"
  - label: "auto"
    description: "Use tmux if available, otherwise in-process"
```

<instructions>
Add `"teammateMode"` to the same settings file chosen in Step 4.

The value should be the selected mode: `"tmux"`, `"in-process"`, or `"auto"`.

Merge this into the existing settings - do NOT overwrite other settings.
</instructions>

---

## Step 6: Verification & Summary

<instructions>
Display a summary based on language setting:

**English (default):**

```markdown
## hyper-team Setup Complete!

| Component          | Status                              |
|--------------------|-------------------------------------|
| Language           | {eng/kor}                           |
| tmux               | {installed version or "Not installed"} |
| Agent Teams        | {Enabled in user-level/project-level} |
| Teammate Mode      | {tmux/in-process/auto}              |

### Next Steps
1. Restart Claude Code for settings to take effect
2. Use `/hyper-team:make-prompt` to create your first team task
3. Or simply ask Claude: "Create a team to work on..."
```

**Korean (--language=kor):**

```markdown
## hyper-team 설정 완료!

| 구성 요소            | 상태                                  |
|--------------------|-------------------------------------|
| Language           | {eng/kor}                           |
| tmux               | {설치된 버전 또는 "미설치"}              |
| Agent Teams        | {사용자 수준/프로젝트 수준에서 활성화}     |
| Teammate Mode      | {tmux/in-process/auto}              |

### 다음 단계
1. 설정이 적용되려면 Claude Code를 재시작하세요
2. `/hyper-team:make-prompt`로 첫 번째 팀 작업을 생성하세요
3. 또는 Claude에게 "팀을 만들어서 작업해줘"라고 요청하세요
```
</instructions>
