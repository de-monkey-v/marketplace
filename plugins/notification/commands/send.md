---
name: notification:send
description: Send a message to configured channels (Slack, Discord, Desktop). 메시지 전송, 알림 보내기
argument-hint: "<message> | <file-path>"
allowed-tools: Bash, Read
---

# /notification:send

Send a message to all configured notification channels.

## Language Resolution

1. Check `$ARGUMENTS` for `--language=eng` or `--language=kor` → use if present
2. Read `.hyper-team/metadata.json` → use `language` field if file exists
3. Default: `eng`

Produce all user-facing output in the resolved language.

## Usage

```
/notification:send Hello, this is a test message
/notification:send ~/path/to/file.txt
/notification:send Deployment complete!
```

## Execution Steps

### 1. Parse Arguments

Check `$ARGUMENTS` value:
- If it's a file path (`.txt`, `.md`, `.conf`, `.json`, `.log`, etc.): Read the file contents
- If it's plain text: Use it directly as the message

### 2. Send Message

Use a Python script to send to all active channels:

```bash
python3 -c "
import os, json, urllib.request

message = '''$MESSAGE'''

# Slack
slack_url = os.environ.get('SLACK_WEBHOOK_URL')
if slack_url:
    for url in slack_url.split(','):
        url = url.strip()
        if url:
            try:
                data = json.dumps({'text': message}).encode('utf-8')
                req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                urllib.request.urlopen(req, timeout=10)
                print(f'[Slack] ✓')
            except Exception as e:
                print(f'[Slack] ✗ {e}')

# Discord
discord_url = os.environ.get('DISCORD_WEBHOOK_URL')
if discord_url:
    for url in discord_url.split(','):
        url = url.strip()
        if url:
            try:
                lines = message.strip().split('\n')
                title = lines[0][:256] if lines else 'Message'
                desc = '\n'.join(lines[1:])[:4096] if len(lines) > 1 else ''
                data = json.dumps({'embeds': [{'title': title, 'description': desc, 'color': 3447003}]}).encode('utf-8')
                req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                urllib.request.urlopen(req, timeout=10)
                print(f'[Discord] ✓')
            except Exception as e:
                print(f'[Discord] ✗ {e}')

if not slack_url and not discord_url:
    print('No channels configured. Set SLACK_WEBHOOK_URL or DISCORD_WEBHOOK_URL')
"
```

### 3. Report Results

Report the send results to the user:
- List of channels that succeeded
- Error messages for any failures

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL (comma-separated for multiple) |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL (comma-separated for multiple) |

## Examples

```
# Simple message
/notification:send Deployment complete!

# Multi-line message
/notification:send 🚀 *Deploy Notification*\n- Version: v1.2.3\n- Environment: production

# Send file contents
/notification:send ~/.tmux.conf
```
