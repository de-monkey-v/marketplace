# Notification Plugin

A hooks-only plugin that automatically sends notifications when Claude Code events occur.

## Features

- **Multi-channel support**: Slack, Discord, Desktop (Linux/Windows/Mac)
- **Multiple URL support**: Send to multiple channels simultaneously using comma-separated URLs
- **Automatic notifications**: Auto-send on Stop, Notification, and SessionEnd events
- **Experience summary**: Auto-extract completed work and usage/testing instructions
- **Work statistics**: Auto-summarize tools used, files modified, and commands executed
- **Next step suggestions**: Heuristic-based workflow recommendations
- **Extensible**: Easy to add new channels
- **No external dependencies**: Uses only Python standard library

## Installation

```bash
/plugin install notification@de-monkey-v/marketplace
```

## Usage

After configuring environment variables in the Setup section, notifications are automatically sent when the following events occur:
- **Stop**: When a task completes
- **Notification**: When waiting for a response
- **SessionEnd**: When a session ends

For manual sending, use the `/notification:send` command.

## Setup

Configure environment variables to enable automatic notifications for each channel.

### Slack

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T.../B.../..."

# To send to multiple channels, separate with commas
export SLACK_WEBHOOK_URL="https://hooks.slack.com/xxx,https://hooks.slack.com/yyy"
```

### Discord

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/{id}/{token}"

# To send to multiple servers, separate with commas
export DISCORD_WEBHOOK_URL="https://discord.com/xxx,https://discord.com/yyy"
```

### Desktop (Linux/Windows/Mac)

```bash
export ENABLE_DESKTOP_NOTIFICATION="true"
```

- **Linux**: Uses `notify-send` (libnotify)
- **Windows**: PowerShell Toast Notification
- **macOS**: Uses `osascript`

### Experience Summary (enabled by default)

```bash
# To disable
export ENABLE_EXPERIENCE_SUMMARY="false"
```

When experience summary is enabled, Stop notifications include:
- **Completed work**: Summary of features/changes implemented by Claude
- **How to use**: Testing/running instructions (commands, URLs, etc.)

### Work Statistics (enabled by default)

```bash
# To disable
export ENABLE_WORK_SUMMARY="false"
```

When work statistics are enabled, Stop notifications include:
- Tools used and call counts
- List of modified files
- Commands executed (Bash)
- Next step workflow suggestions

## Commands

### /notification:send

Manually send a custom message to all configured channels.

```bash
# Simple message
/notification:send Deployment complete!

# Send file contents
/notification:send ~/.tmux.conf
```

## Supported Events

| Event | Notification Content |
|-------|---------------------|
| **Stop** | ✅ Claude Code task completed |
| **Notification** | 💬 Claude is waiting for a response |
| **SessionEnd** | 🔚 Claude Code session ended |

## Information Included in Notifications

### Machine Identification
- **When connected via Tailscale**: Uses Tailscale hostname (e.g., `my-desktop`)
- **When not connected**: Uses system hostname

Easily identify which machine triggered the notification when using Claude Code on multiple PCs.

### tmux Session Info
- **Running inside tmux**: Displayed as `session:window` format (e.g., `dev:claude`)
- **Running outside tmux**: This info is omitted

Identify which tmux session triggered the notification when running multiple sessions on a single PC.

## Notification Examples

### Slack

```
✅ Claude Code task completed

- Machine: my-desktop
- tmux: dev:claude
- Time: 2026-01-03 15:30:00
- Working directory: /home/user/my-project
- Session ID: abc123
- Stop reason: end_turn

---
📝 *User request*
"Implement login functionality"
---

🎯 *Completed work*
• Implemented JWT authentication logic
• Added login/logout API endpoints
• Files: auth.ts, login.tsx, api.ts

🚀 *How to use*
`npm run dev`
Access: http://localhost:3000/login
Test account: test@example.com / ****

📊 *Work summary*
- *Tools used*: `Write`(3), `Bash`(5), `Read`(8)
- *Total tool calls*: 16
- *Modified files*: `auth.ts`, `login.tsx`, `api.ts`
- *Commands executed*: `npm`, `git` (7 commands)

💡 *Next step suggestions*
  • 🧪 Write and run tests (`/dev-toolkit2:verify`)
  • 📦 Lint and type check (`npm run lint`, `npm run typecheck`)
  • 💾 Commit changes (`/git-utils:commit`)
```

### Discord (Embed)

```
┌─────────────────────────────────┐
│ ✅ Claude Code task completed    │
│                                 │
│ Machine: my-desktop             │
│ tmux: dev:claude                │
│ Time: 2026-01-03 15:30:00       │
│ Working directory: /home/user/my-project │
│ Session ID: abc123              │
│ Stop reason: end_turn           │
└─────────────────────────────────┘
```

## Adding a New Channel

Register in the `CHANNELS` dictionary in `notifier.py`:

```python
# 1. Write the send function
def send_teams(message: str, webhook_url: str) -> bool:
    # Teams Webhook send logic
    ...

# 2. Register in CHANNELS
CHANNELS = {
    ...
    "teams": {
        "env_var": "TEAMS_WEBHOOK_URL",
        "sender": send_teams,
    },
}
```

## File Structure

```
plugins/notification/
├── .claude-plugin/plugin.json
├── commands/
│   └── send.md              # Manual send command
├── hooks/
│   ├── hooks.json           # Event → script mapping
│   └── scripts/
│       ├── notifier.py            # Unified notification script
│       ├── summarizer.py          # Work statistics and workflow suggestions
│       └── experience_extractor.py # Completion summary and usage guide extraction
└── README.md
```

## License

MIT License

> This plugin respects the language setting in `.hyper-team/metadata.json`. Run `/hyper-team:setup` to configure.
