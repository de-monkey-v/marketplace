---
name: setup
description: Interactive setup wizard for the notification plugin. Configures Slack webhooks, Discord webhooks, and desktop notifications.
argument-hint: "[--language=eng|kor]"
allowed-tools: Bash, Read, Write, Edit, AskUserQuestion
---

# /notification:setup - Setup Wizard

Interactive setup wizard for the notification plugin.

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

## Step 2: Choose Notification Channels

<instructions>
All notification channels are optional. The user can configure any combination.
</instructions>

```
AskUserQuestion:
- question: "Which notification channels do you want to configure? Select all that apply."
- header: "Channels"
- multiSelect: true
- options:
  - label: "Slack"
    description: "Send notifications via Slack Incoming Webhooks"
  - label: "Discord"
    description: "Send notifications via Discord Webhooks"
  - label: "Desktop"
    description: "OS-native desktop notifications (Linux/macOS/Windows)"
  - label: "Skip all"
    description: "I'll configure notification channels later"
```

---

## Step 3: Configure Slack (if selected)

<instructions>
Only execute this step if the user selected "Slack" in Step 2. Otherwise skip to Step 4.
</instructions>

### 3.1: Guide Webhook Creation

Display to the user:

```
To create a Slack Incoming Webhook:

1. Go to https://api.slack.com/messaging/webhooks
2. Click "Create your Slack app" (or use an existing app)
3. Choose "From scratch" and name your app (e.g., "Claude Notifications")
4. Select your workspace
5. In the app settings, go to "Incoming Webhooks" in the left sidebar
6. Toggle "Activate Incoming Webhooks" to ON
7. Click "Add New Webhook to Workspace"
8. Choose the channel where notifications should be posted
9. Click "Allow"
10. Copy the Webhook URL (starts with https://hooks.slack.com/services/...)
```

### 3.2: Get the Webhook URL

```
AskUserQuestion:
- question: "Paste your Slack Webhook URL:"
- header: "Slack URL"
- options:
  - label: "I have my webhook URL ready"
    description: "I'll paste it in the 'Other' field below"
  - label: "Skip for now"
    description: "I'll configure Slack later"
```

### 3.3: Add to Shell RC File

<instructions>
If the user provided a URL (via "Other" input), add it to the RC file.

First check if SLACK_WEBHOOK_URL already exists:
</instructions>

```
Bash: grep -c 'SLACK_WEBHOOK_URL' $RC_FILE 2>/dev/null || echo "0"
```

- If it already exists: Ask the user if they want to replace or append (multiple webhooks supported, comma-separated).
  - If replace: Use Edit to replace the existing export line.
  - If append: Use Edit to append the new URL to the existing value with a comma separator.
  - If skip: Skip.
- If it does not exist: Append the export line:

```
Bash: echo '' >> $RC_FILE && echo '# Slack Webhook URL (notification plugin)' >> $RC_FILE && echo 'export SLACK_WEBHOOK_URL="<USER_URL>"' >> $RC_FILE
```

---

## Step 4: Configure Discord (if selected)

<instructions>
Only execute this step if the user selected "Discord" in Step 2. Otherwise skip to Step 5.
</instructions>

### 4.1: Guide Webhook Creation

Display to the user:

```
To create a Discord Webhook:

1. Open Discord and go to your server
2. Right-click the channel where you want notifications
3. Select "Edit Channel"
4. Go to "Integrations" tab
5. Click "Webhooks"
6. Click "New Webhook"
7. Give it a name (e.g., "Claude Notifications")
8. Optionally set an avatar
9. Click "Copy Webhook URL"
   (URL looks like: https://discord.com/api/webhooks/...)
```

### 4.2: Get the Webhook URL

```
AskUserQuestion:
- question: "Paste your Discord Webhook URL:"
- header: "Discord URL"
- options:
  - label: "I have my webhook URL ready"
    description: "I'll paste it in the 'Other' field below"
  - label: "Skip for now"
    description: "I'll configure Discord later"
```

### 4.3: Add to Shell RC File

<instructions>
If the user provided a URL (via "Other" input), add it to the RC file.

First check if DISCORD_WEBHOOK_URL already exists:
</instructions>

```
Bash: grep -c 'DISCORD_WEBHOOK_URL' $RC_FILE 2>/dev/null || echo "0"
```

- If it already exists: Ask the user if they want to replace or append (multiple webhooks supported, comma-separated).
  - If replace: Use Edit to replace the existing export line.
  - If append: Use Edit to append the new URL to the existing value with a comma separator.
  - If skip: Skip.
- If it does not exist: Append the export line:

```
Bash: echo '' >> $RC_FILE && echo '# Discord Webhook URL (notification plugin)' >> $RC_FILE && echo 'export DISCORD_WEBHOOK_URL="<USER_URL>"' >> $RC_FILE
```

---

## Step 5: Configure Desktop Notifications (if selected)

<instructions>
Only execute this step if the user selected "Desktop" in Step 2. Otherwise skip to Step 6.
</instructions>

### 5.1: Detect OS

```
Bash: uname -s
```

### 5.2: Check Desktop Notification Requirements

<instructions>
Based on the detected OS:
</instructions>

**Linux:**

```
Bash: which notify-send 2>/dev/null && echo "found" || echo "not_found"
```

- If `notify-send` is not found:
  - Inform the user: `notify-send` is required for desktop notifications on Linux.
  - Suggest: `sudo apt install libnotify-bin` (Debian/Ubuntu) or `sudo dnf install libnotify` (Fedora/RHEL) or `sudo pacman -S libnotify` (Arch)
  - Ask the user if they want to install it now or skip.

**macOS:**
- Desktop notifications use `osascript` which is built-in. No additional setup needed.

**Windows (WSL):**
- Desktop notifications use PowerShell which is available via WSL interop. No additional setup needed.

### 5.3: Add ENABLE_DESKTOP_NOTIFICATION to RC File

<instructions>
First check if ENABLE_DESKTOP_NOTIFICATION already exists:
</instructions>

```
Bash: grep -c 'ENABLE_DESKTOP_NOTIFICATION' $RC_FILE 2>/dev/null || echo "0"
```

- If it already exists: Inform the user it's already configured and ask if they want to update it.
- If it does not exist: Append:

```
Bash: echo '' >> $RC_FILE && echo '# Desktop Notifications (notification plugin)' >> $RC_FILE && echo 'export ENABLE_DESKTOP_NOTIFICATION="true"' >> $RC_FILE
```

---

## Step 6: Verify Configuration

### 6.1: Source RC File and Check Environment Variables

```
Bash: source $RC_FILE 2>/dev/null; echo "SLACK=$([ -n \"$SLACK_WEBHOOK_URL\" ] && echo 'configured' || echo 'not set')"; echo "DISCORD=$([ -n \"$DISCORD_WEBHOOK_URL\" ] && echo 'configured' || echo 'not set')"; echo "DESKTOP=$([ \"$ENABLE_DESKTOP_NOTIFICATION\" = 'true' ] && echo 'enabled' || echo 'not set')"
```

### 6.2: Test Notifications (optional)

```
AskUserQuestion:
- question: "Do you want to send a test notification to verify the configured channels?"
- header: "Test"
- options:
  - label: "Yes, test all configured channels"
    description: "Send a test message to verify everything works"
  - label: "Skip testing"
    description: "I'll test later with /notification:send"
```

<instructions>
If the user wants to test:

**Test Slack** (if configured):
```
Bash: source $RC_FILE && python3 -c "
import os, json, urllib.request
url = os.environ.get('SLACK_WEBHOOK_URL', '').split(',')[0].strip()
if url:
    data = json.dumps({'text': 'Test notification from Claude Code notification plugin'}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req, timeout=10)
    print('Slack: OK')
"
```

**Test Discord** (if configured):
```
Bash: source $RC_FILE && python3 -c "
import os, json, urllib.request
url = os.environ.get('DISCORD_WEBHOOK_URL', '').split(',')[0].strip()
if url:
    data = json.dumps({'embeds': [{'title': 'Test Notification', 'description': 'From Claude Code notification plugin', 'color': 3447003}]}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req, timeout=10)
    print('Discord: OK')
"
```

**Test Desktop** (if enabled):

- Linux: `Bash: notify-send "Claude Code" "Test notification from notification plugin"`
- macOS: `Bash: osascript -e 'display notification "Test notification from notification plugin" with title "Claude Code"'`

Report the test results for each channel.
</instructions>

---

## Step 7: Summary

Display a formatted summary based on the resolved language:

### English Summary:

```markdown
## Notification Plugin Setup Complete

| Channel   | Status       | Details                          |
|-----------|--------------|----------------------------------|
| Slack     | {status}     | {configured/skipped/error}       |
| Discord   | {status}     | {configured/skipped/error}       |
| Desktop   | {status}     | {enabled/skipped/not available}  |

### Configured Environment Variables
- SLACK_WEBHOOK_URL: {set in RC_FILE / not configured}
- DISCORD_WEBHOOK_URL: {set in RC_FILE / not configured}
- ENABLE_DESKTOP_NOTIFICATION: {set in RC_FILE / not configured}

### Next Steps
1. Run `source {RC_FILE}` or restart your terminal to load new environment variables
2. Use `/notification:send Hello!` to send a test notification
3. Notifications can be used in hooks for automated alerts (e.g., on task completion)
```

### Korean Summary:

```markdown
## Notification 플러그인 설정 완료

| 채널      | 상태         | 세부사항                         |
|-----------|--------------|----------------------------------|
| Slack     | {상태}       | {설정 완료/건너뜀/오류}            |
| Discord   | {상태}       | {설정 완료/건너뜀/오류}            |
| Desktop   | {상태}       | {활성화/건너뜀/사용 불가}           |

### 설정된 환경변수
- SLACK_WEBHOOK_URL: {RC_FILE에 설정됨 / 미설정}
- DISCORD_WEBHOOK_URL: {RC_FILE에 설정됨 / 미설정}
- ENABLE_DESKTOP_NOTIFICATION: {RC_FILE에 설정됨 / 미설정}

### 다음 단계
1. `source {RC_FILE}` 실행 또는 터미널 재시작으로 환경변수 로드
2. `/notification:send 안녕하세요!`로 테스트 알림 전송
3. 훅(hooks)에서 알림을 사용하여 자동 알림 설정 가능 (예: 작업 완료 시)
```
