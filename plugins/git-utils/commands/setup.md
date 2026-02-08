---
name: setup
description: Interactive setup wizard for the git-utils plugin. Checks git installation, user configuration, and global settings.
argument-hint: "[--language=eng]"
allowed-tools: Bash, Read, Write, Edit, AskUserQuestion
---

# /git-utils:setup - Setup Wizard

Interactive setup wizard for the git-utils plugin.

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

## Step 2: Check Git Installation

```
Bash: which git && git --version
```

**If git is NOT found:**

Display a message based on language:
- English: "Git is not installed. Please install git first."
- Korean: "Git이 설치되어 있지 않습니다. 먼저 git을 설치해 주세요."

Provide installation guidance:
- **Linux (Debian/Ubuntu):** `sudo apt install git`
- **Linux (Fedora):** `sudo dnf install git`
- **macOS:** `xcode-select --install` or `brew install git`
- **Windows:** Download from https://git-scm.com/downloads

Then STOP setup - git must be installed before continuing.

**If git IS found:**
- Display the detected git version
- Proceed to Step 3

---

## Step 3: Check Git User Name

```
Bash: git config --global user.name
```

**If user.name is NOT configured (empty output):**

```
AskUserQuestion:
- question: "Git user.name is not configured. What name would you like to use for your git commits?"
  (Korean: "Git user.name이 설정되어 있지 않습니다. 커밋에 사용할 이름을 입력해 주세요.")
- header: "Git Name"
- options:
  - label: "Enter name"
    description: "Type your full name or display name"
```

After receiving the name from the user:

```
Bash: git config --global user.name "<user-provided-name>"
```

Confirm the name was set successfully.

**If user.name IS configured:**
- Display the current user.name
- Proceed to Step 4

---

## Step 4: Check Git User Email

```
Bash: git config --global user.email
```

**If user.email is NOT configured (empty output):**

```
AskUserQuestion:
- question: "Git user.email is not configured. What email would you like to use for your git commits?"
  (Korean: "Git user.email이 설정되어 있지 않습니다. 커밋에 사용할 이메일을 입력해 주세요.")
- header: "Git Email"
- options:
  - label: "Enter email"
    description: "Type your email address"
```

After receiving the email from the user:

```
Bash: git config --global user.email "<user-provided-email>"
```

Confirm the email was set successfully.

**If user.email IS configured:**
- Display the current user.email
- Proceed to Step 5

---

## Step 5: Show Git Global Configuration Summary

```
Bash: git config --global --list 2>/dev/null | head -20
```

Display the current global git configuration to the user in a readable format.

---

## Step 6: Summary

Display a final summary based on the resolved language:

### English Summary:

```
## git-utils Setup Complete

| Item               | Status |
|--------------------|--------|
| Git installed      | [version] |
| user.name          | [name] |
| user.email         | [email] |

### Available Commands
- `/git-utils:commit` - Analyze changes and create commits
- `/git-utils:branch` - Branch management
- `/git-utils:log` - Commit history viewer
- `/git-utils:diff` - Change analysis
- `/git-utils:status` - Repository status overview

Setup complete! You can now use the git-utils plugin.
```

### Korean Summary:

```
## git-utils 설정 완료

| 항목               | 상태   |
|--------------------|--------|
| Git 설치           | [version] |
| user.name          | [name] |
| user.email         | [email] |

### 사용 가능한 명령어
- `/git-utils:commit` - 변경사항 분석 및 커밋 생성
- `/git-utils:branch` - 브랜치 관리
- `/git-utils:log` - 커밋 히스토리 뷰어
- `/git-utils:diff` - 변경사항 분석
- `/git-utils:status` - 저장소 상태 확인

설정이 완료되었습니다! git-utils 플러그인을 사용할 수 있습니다.
```
