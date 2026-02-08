---
name: hook-development
description: Hook configuration and event automation guide. This skill should be used when the user asks to "create a hook", "add a hook", "훅 만들어줘", or mentions hook events like "PreToolUse", "PostToolUse", "SessionStart".
---

# Hook Development for Claude Code Plugins

Hooks are event-driven automation scripts that execute in response to Claude Code events. Use hooks to validate operations, enforce policies, add context, and integrate external tools.

## Hook Types

### Prompt-Based Hooks (Recommended)

Use LLM-driven decision making for context-aware validation:

```json
{
  "type": "prompt",
  "prompt": "Evaluate if this tool use is appropriate: $ARGUMENTS",
  "timeout": 30
}
```

**Supported events:** Stop, SubagentStop, UserPromptSubmit, PreToolUse, PermissionRequest

### Command Hooks

Execute bash commands for deterministic checks:

```json
{
  "type": "command",
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh",
  "timeout": 60
}
```

**Use for:** Fast deterministic validations, file operations, external tools.

## Plugin hooks.json Format

**For plugin hooks** in `hooks/hooks.json`, use wrapper format:

```json
{
  "description": "Validation hooks (optional)",
  "hooks": {
    "PreToolUse": [...],
    "Stop": [...],
    "SessionStart": [...]
  }
}
```

## Hook Events

| Event | When | Use For |
|-------|------|---------|
| PreToolUse | Before tool | Validation, modification |
| PostToolUse | After tool | Feedback, logging |
| UserPromptSubmit | User input | Context, validation |
| Stop | Agent stopping | Completeness check |
| SubagentStop | Subagent done | Task validation |
| SubagentStart | Subagent begins | Agent tracking, context injection |
| SessionStart | Session begins | Context loading |
| SessionEnd | Session ends | Cleanup, logging |
| PreCompact | Before compact | Preserve context |
| Notification | User notified | Reactions |
| PermissionRequest | Permission dialog | Auto-approve/deny |

### PreToolUse Example

```json
{
  "PreToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Validate file write safety. Check: system paths, credentials, path traversal. Return 'approve' or 'deny'."
        }
      ]
    }
  ]
}
```

### Stop Example

```json
{
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Verify task completion: tests run, build succeeded. Return 'approve' to stop or 'block' with reason."
        }
      ]
    }
  ]
}
```

### SessionStart Example

```json
{
  "SessionStart": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/load-context.sh",
          "timeout": 10
        }
      ]
    }
  ]
}
```

**Persist environment variables using `$CLAUDE_ENV_FILE`:**
```bash
echo "export PROJECT_TYPE=nodejs" >> "$CLAUDE_ENV_FILE"
```

## Matchers

```json
"matcher": "Write"           // Exact match
"matcher": "Read|Write|Edit" // Multiple tools
"matcher": "*"               // All tools
"matcher": "mcp__.*"         // Regex pattern (all MCP tools)
```

### Notification Matchers

For Notification events, match notification types:

```json
"matcher": "user_input_request"    // Input prompts
"matcher": "help_requested"        // Help requests
"matcher": "elicitation_dialog"    // MCP tool input dialogs
"matcher": "*"                     // All notifications
```

## Hook Output

### Standard Output

```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Message for Claude"
}
```

### Decision Output (Stop/SubagentStop)

```json
{
  "decision": "approve|block",
  "reason": "Explanation"
}
```

### hookSpecificOutput (Advanced)

For PreToolUse hooks, use `hookSpecificOutput` to modify tool input or control permissions:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Safe operation approved",
    "updatedInput": {
      "file_path": "/modified/path.txt"
    },
    "additionalContext": "Extra context for Claude"
  }
}
```

| Field | Description |
|-------|-------------|
| `permissionDecision` | "allow", "deny", or "ask" (replaces deprecated `decision`) |
| `permissionDecisionReason` | Explanation for the decision |
| `updatedInput` | Modified tool input (partial update supported) |
| `additionalContext` | Extra context injected into Claude's context |

### Exit Codes

- `0` - Success (stdout shown in transcript)
- `2` - Blocking error (stderr fed back to Claude)
- Other - Non-blocking error

## Environment Variables

Available in command hooks:

- `$CLAUDE_PROJECT_DIR` - Project root path
- `$CLAUDE_PLUGIN_ROOT` - Plugin directory (always use for portability)
- `$CLAUDE_ENV_FILE` - SessionStart only: persist env vars here
- `$CLAUDE_CODE_REMOTE` - "true" if remote/web session, empty if local CLI

**Always use ${CLAUDE_PLUGIN_ROOT} for portable paths:**

```json
{
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh"
}
```

## Security Essentials

```bash
#!/bin/bash
set -euo pipefail

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

# Always quote variables
echo "$file_path"

# Check path traversal
if [[ "$file_path" == *".."* ]]; then
  echo '{"decision": "deny", "reason": "Path traversal"}' >&2
  exit 2
fi
```

See `references/security-best-practices.md` for complete security guidance.

## Best Practices

✅ **DO:**
- Use prompt-based hooks for complex logic
- Use ${CLAUDE_PLUGIN_ROOT} for portability
- Validate all inputs in command hooks
- Quote all bash variables
- Set appropriate timeouts
- Return structured JSON output

❌ **DON'T:**
- Use hardcoded paths
- Trust user input without validation
- Create long-running hooks
- Rely on hook execution order (hooks run in parallel)
- Log sensitive information

## Debugging

```bash
claude --debug  # Enable debug mode
```

Use `/hooks` command to review loaded hooks.

**Test hook scripts directly:**
```bash
echo '{"tool_name": "Write", "tool_input": {"file_path": "/test"}}' | \
  bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh
```

## Additional Resources

### Reference Files

- **`references/patterns.md`** - Common hook patterns (10+ proven patterns)
- **`references/security-best-practices.md`** - Complete security guidance
- **`references/lifecycle.md`** - Hook loading, execution, limitations
- **`references/migration.md`** - Migrating from basic to advanced hooks
- **`references/advanced.md`** - Advanced use cases
- **`references/input-output-reference.md`** - Event-specific input/output schemas

### Example Hook Scripts

- **`examples/validate-write.sh`** - File write validation
- **`examples/validate-bash.sh`** - Bash command validation
- **`examples/load-context.sh`** - SessionStart context loading

### Utility Scripts

- **`scripts/validate-hook-schema.sh`** - Validate hooks.json structure
- **`scripts/test-hook.sh`** - Test hooks with sample input
- **`scripts/hook-linter.sh`** - Check for common issues

## Implementation Workflow

1. Identify events to hook into (PreToolUse, Stop, SessionStart, etc.)
2. Decide between prompt-based (flexible) or command (deterministic) hooks
3. Write hook configuration in `hooks/hooks.json`
4. For command hooks, create scripts in `hooks/scripts/`
5. Use ${CLAUDE_PLUGIN_ROOT} for all file references
6. Validate with `scripts/validate-hook-schema.sh`
7. Test with `claude --debug`
8. Document in plugin README

## See Also

### Related Skills
- **[plugin-development](../plugin-development/SKILL.md)** - Plugin structure
- **[plugin-settings](../plugin-settings/SKILL.md)** - Settings hooks can read
- **[command-development](../command-development/SKILL.md)** - Commands hooks validate

### Related Agents
- **hook-creator** - Create hook configurations
- **plugin-validator** - Validate hook configurations
