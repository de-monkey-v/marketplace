---
description: Send messages via Slack webhook. Used for requests like "send to Slack", "슬랙 알림", "slack message", etc.
---

# Slack Message Sending

Send messages using Slack Incoming Webhooks.

## Prerequisites

The environment variable `SLACK_WEBHOOK_URL` must be set.

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/xxx/yyy/zzz"
```

To send to multiple channels, separate with commas:
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/xxx,https://hooks.slack.com/yyy"
```

## How to Send

Use Python's urllib to make an HTTP POST request:

```python
import json
import os
import urllib.request
import urllib.error

def send_slack(message: str, webhook_url: str = None) -> bool:
    """Send a message to Slack

    Args:
        message: Message to send (supports mrkdwn format)
        webhook_url: Webhook URL (uses environment variable if not provided)

    Returns:
        Success status
    """
    url = webhook_url or os.environ.get("SLACK_WEBHOOK_URL")
    if not url:
        print("SLACK_WEBHOOK_URL environment variable is not set.")
        return False

    try:
        payload = {"text": message}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except urllib.error.URLError as e:
        print(f"Slack send failed: {e}")
        return False
```

## Message Formatting

You can use Slack mrkdwn syntax:

| Format | Example | Result |
|--------|---------|--------|
| Bold | `*text*` | **text** |
| Italic | `_text_` | _text_ |
| Strikethrough | `~text~` | ~~text~~ |
| Code | `` `code` `` | `code` |
| Code block | ` ```code``` ` | code block |
| Link | `<URL\|text>` | hyperlink |

## Execution Examples

### Simple Message

```bash
python3 -c "
import json, os, urllib.request

message = 'Deployment complete!'
url = os.environ.get('SLACK_WEBHOOK_URL')
if url:
    data = json.dumps({'text': message}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req, timeout=10)
    print('Send complete')
else:
    print('SLACK_WEBHOOK_URL not set')
"
```

### Send to Multiple Webhooks

```bash
python3 -c "
import json, os, urllib.request

message = '''🚀 *Deploy Notification*
- Version: v1.2.3
- Environment: production'''

slack_urls = os.environ.get('SLACK_WEBHOOK_URL', '').split(',')
for url in slack_urls:
    url = url.strip()
    if url:
        try:
            data = json.dumps({'text': message}).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            urllib.request.urlopen(req, timeout=10)
            print(f'✓ Send complete')
        except Exception as e:
            print(f'✗ Send failed: {e}')
"
```

## Environment Variable Check

Check if the environment variable is set before sending:

```bash
if [ -z "$SLACK_WEBHOOK_URL" ]; then
    echo "SLACK_WEBHOOK_URL is not set."
else
    echo "Slack webhook configured"
fi
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `urlopen error` | Network issue or invalid URL | Verify URL and check network connection |
| `HTTP 404` | Webhook URL has been deactivated | Regenerate webhook in Slack |
| `HTTP 400` | Invalid payload format | Verify JSON format |
| Timeout | Network latency | Increase timeout value |
