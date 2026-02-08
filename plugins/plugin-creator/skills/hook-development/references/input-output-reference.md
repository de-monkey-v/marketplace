# Hook Input/Output Reference

This reference details the input and output schemas for each hook event type.

## Common Input Fields

All hook events receive JSON input with these common fields:

```json
{
  "session_id": "abc123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Event-Specific Input Schemas

### PreToolUse

```json
{
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "content": "file contents..."
  }
}
```

**Available in prompts:** `$ARGUMENTS` (maps to `tool_input`)

### PostToolUse

```json
{
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "content": "file contents..."
  },
  "tool_result": "File written successfully"
}
```

### UserPromptSubmit

```json
{
  "prompt": "User's message text"
}
```

### Stop / SubagentStop

```json
{
  "stop_reason": "task_complete"
}
```

### SubagentStart

```json
{
  "agent_name": "code-reviewer",
  "task_description": "Review the authentication module"
}
```

### SessionStart

```json
{
  "project_dir": "/path/to/project",
  "session_type": "cli"
}
```

### SessionEnd

```json
{
  "duration_seconds": 3600,
  "tools_used": ["Read", "Write", "Bash"]
}
```

### PreCompact

```json
{
  "context_tokens": 150000,
  "compact_reason": "token_limit"
}
```

### Notification

```json
{
  "notification_type": "user_input_request",
  "message": "Notification content"
}
```

**Notification types:**
- `user_input_request` - Prompting user for input
- `help_requested` - Help command triggered
- `elicitation_dialog` - MCP tool input dialog

### PermissionRequest

```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf ./temp"
  },
  "permission_type": "tool_execution"
}
```

## Output Schemas

### Standard Output (All Events)

```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Optional message for Claude"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `continue` | boolean | Whether to proceed (default: true) |
| `suppressOutput` | boolean | Hide hook output from transcript |
| `systemMessage` | string | Message injected into Claude's context |

### Decision Output (Stop/SubagentStop)

```json
{
  "decision": "approve",
  "reason": "All tasks completed"
}
```

| Decision | Effect |
|----------|--------|
| `approve` | Allow agent to stop |
| `block` | Prevent stopping, provide reason |

### hookSpecificOutput (PreToolUse)

For modifying tool input or controlling permission:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Safe operation",
    "updatedInput": {
      "file_path": "/modified/path.txt"
    },
    "additionalContext": "Extra info for Claude"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `hookEventName` | string | Must match the event ("PreToolUse") |
| `permissionDecision` | string | "allow", "deny", or "ask" |
| `permissionDecisionReason` | string | Explanation for decision |
| `updatedInput` | object | Partial update to tool_input |
| `additionalContext` | string | Context injected for Claude |

**Note:** `permissionDecision` replaces the deprecated `decision` field.

### hookSpecificOutput (PermissionRequest)

For auto-handling permission dialogs:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Auto-approved safe operation"
  }
}
```

| Decision | Effect |
|----------|--------|
| `allow` | Auto-approve without user prompt |
| `deny` | Auto-deny without user prompt |
| `ask` | Show normal permission dialog (default) |

## Exit Codes (Command Hooks)

| Code | Meaning | Effect |
|------|---------|--------|
| 0 | Success | stdout shown in transcript |
| 2 | Blocking error | stderr fed back to Claude |
| Other | Non-blocking error | Logged, execution continues |

## Prompt Placeholders

Available placeholders for prompt-based hooks:

| Placeholder | Description | Events |
|-------------|-------------|--------|
| `$ARGUMENTS` | Tool input as JSON | PreToolUse |
| `$PROMPT` | User's prompt text | UserPromptSubmit |
| `$TRANSCRIPT_PATH` | Path to transcript file | All |
| `$CLAUDE_PROJECT_DIR` | Project root path | All |

## Environment Variables (Command Hooks)

| Variable | Description | Events |
|----------|-------------|--------|
| `$CLAUDE_PROJECT_DIR` | Project root path | All |
| `$CLAUDE_PLUGIN_ROOT` | Plugin directory | All |
| `$CLAUDE_ENV_FILE` | Env file to write to | SessionStart only |
| `$CLAUDE_CODE_REMOTE` | "true" if remote/web | All |

## Example: Complete PreToolUse Flow

**Input received by hook:**
```json
{
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/home/user/project/config.json",
    "content": "{\"key\": \"value\"}"
  }
}
```

**Hook script processing:**
```bash
#!/bin/bash
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

# Validate path
if [[ "$file_path" == *".env"* ]]; then
  echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "Cannot write to .env files"}}' >&2
  exit 2
fi

# Modify path if needed
new_path=$(echo "$file_path" | sed 's/config.json/config.local.json/')
echo "{\"hookSpecificOutput\": {\"hookEventName\": \"PreToolUse\", \"permissionDecision\": \"allow\", \"updatedInput\": {\"file_path\": \"$new_path\"}}}"
```

**Output for denial:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Cannot write to .env files"
  }
}
```

**Output for approval with modification:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "updatedInput": {
      "file_path": "/home/user/project/config.local.json"
    }
  }
}
```
