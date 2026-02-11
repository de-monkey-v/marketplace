---
name: setup
description: Install Gemini CLI and Codex CLI for the ai-cli-tools plugin.
argument-hint: "[--language=eng]"
allowed-tools: Bash, Read, AskUserQuestion
---

# /ai-cli-tools:setup - Setup Wizard

Install the AI CLI tools required by this plugin.

## Language Resolution

1. Check `$ARGUMENTS` for `--language=eng` or `--language=kor` → use if present
2. Read `.hyper-team/metadata.json` → use `language` field if file exists
3. Default: `eng`

Produce all user-facing output in the resolved language.

---

## Step 1: Check Current Status

Check which tools are already installed:

```
Bash: echo "=== Gemini CLI ===" && (which gemini && gemini --version 2>/dev/null || echo "NOT INSTALLED") && echo "=== Codex CLI ===" && (which codex && codex --version 2>/dev/null || echo "NOT INSTALLED") && echo "=== Node.js ===" && (node --version 2>/dev/null || echo "NOT INSTALLED") && echo "=== npm ===" && (npm --version 2>/dev/null || echo "NOT INSTALLED")
```

<instructions>
If both Gemini CLI and Codex CLI are already installed, skip to the Summary step and report that everything is ready.

If Node.js/npm is not installed, inform the user that it is required and suggest:
- **nvm (recommended)**: `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash && nvm install --lts`
- **Homebrew (macOS)**: `brew install node`
- **apt (Debian/Ubuntu)**: `sudo apt install nodejs npm`

Then STOP - Node.js must be installed first before proceeding.

Minimum requirement: Node.js v20 or higher.
</instructions>

---

## Step 2: Install Gemini CLI

<instructions>
Skip this step if Gemini CLI is already installed.
</instructions>

```
AskUserQuestion:
- question: "Gemini CLI is not installed. How would you like to install it?"
- header: "Gemini"
- options:
  - label: "npm (Recommended)"
    description: "npm install -g @google/gemini-cli"
  - label: "Homebrew"
    description: "brew install gemini-cli"
  - label: "Skip"
    description: "I'll install it later"
```

Based on user choice:

**npm:**
```
Bash: npm install -g @google/gemini-cli
```

**Homebrew:**
```
Bash: brew install gemini-cli
```

Verify after install:
```
Bash: which gemini && gemini --version 2>/dev/null || echo "Installation failed"
```

If installation fails via npm, suggest: `sudo npm install -g @google/gemini-cli`

Reference: https://github.com/google-gemini/gemini-cli

---

## Step 3: Install Codex CLI

<instructions>
Skip this step if Codex CLI is already installed.
</instructions>

```
AskUserQuestion:
- question: "Codex CLI is not installed. How would you like to install it?"
- header: "Codex"
- options:
  - label: "npm (Recommended)"
    description: "npm install -g @openai/codex"
  - label: "Homebrew"
    description: "brew install --cask codex"
  - label: "Skip"
    description: "I'll install it later"
```

Based on user choice:

**npm:**
```
Bash: npm install -g @openai/codex
```

**Homebrew:**
```
Bash: brew install --cask codex
```

Verify after install:
```
Bash: which codex && codex --version 2>/dev/null || echo "Installation failed"
```

If installation fails via npm, suggest: `sudo npm install -g @openai/codex`

Reference: https://github.com/openai/codex

---

## Step 4: Summary

<instructions>
Re-check installation status and display summary based on resolved language:

```
Bash: echo "gemini: $(which gemini 2>/dev/null && gemini --version 2>/dev/null || echo 'not installed')" && echo "codex: $(which codex 2>/dev/null && codex --version 2>/dev/null || echo 'not installed')"
```

**English (default):**

```markdown
## ai-cli-tools Setup Complete

| Tool        | Status                              |
|-------------|-------------------------------------|
| Gemini CLI  | {installed version or "Not installed"} |
| Codex CLI   | {installed version or "Not installed"} |

### First Run
- **Gemini**: Run `gemini` in your terminal to authenticate with your Google account
- **Codex**: Run `codex` in your terminal to authenticate with your OpenAI account

### How to Use in Claude Code
- `@llms` - Gemini/Codex에게 코드 리뷰/분석 위임

### Links
- Gemini CLI: https://github.com/google-gemini/gemini-cli
- Codex CLI: https://github.com/openai/codex
```

**Korean (--language=kor):**

```markdown
## ai-cli-tools 설정 완료

| 도구        | 상태                                  |
|-------------|-------------------------------------|
| Gemini CLI  | {설치된 버전 또는 "미설치"}              |
| Codex CLI   | {설치된 버전 또는 "미설치"}              |

### 처음 실행
- **Gemini**: 터미널에서 `gemini` 실행하여 Google 계정 인증
- **Codex**: 터미널에서 `codex` 실행하여 OpenAI 계정 인증

### Claude Code에서 사용법
- `@llms` - Gemini/Codex에게 코드 리뷰/분석 위임

### 링크
- Gemini CLI: https://github.com/google-gemini/gemini-cli
- Codex CLI: https://github.com/openai/codex
```
</instructions>
