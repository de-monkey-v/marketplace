# Hook Lifecycle and Limitations

This reference covers hook loading, execution timing, and important limitations.

## Hook Loading

### When Hooks Load

Hooks are loaded when Claude Code session starts:

1. Claude Code initializes
2. Plugin manifests read
3. `hooks/hooks.json` files parsed
4. Hook configurations validated
5. Hooks registered for events

### Cannot Hot-Swap Hooks

**Important:** Changes to hook configuration require restarting Claude Code.

**What doesn't work during a session:**
- Editing `hooks/hooks.json` won't affect current session
- Adding new hook scripts won't be recognized
- Changing hook commands/prompts won't update
- Modifying timeout values won't apply

**To apply hook changes:**
1. Edit hook configuration or scripts
2. Exit Claude Code session
3. Restart: `claude` or `cc`
4. New hook configuration loads
5. Test hooks with `claude --debug`

### Hook Validation at Startup

Hooks are validated when Claude Code starts:

| Issue | Behavior |
|-------|----------|
| Invalid JSON in hooks.json | Loading failure, error shown |
| Missing hook scripts | Warning logged, hook skipped |
| Syntax errors in scripts | Error on first execution |
| Invalid matcher patterns | Hook may not trigger |

## Execution Behavior

### Parallel Execution

All matching hooks run **in parallel**, not sequentially:

```json
{
  "PreToolUse": [
    {
      "matcher": "Write",
      "hooks": [
        {"type": "command", "command": "check1.sh"},  // Runs
        {"type": "command", "command": "check2.sh"},  // simultaneously
        {"type": "prompt", "prompt": "Validate..."}   // with these
      ]
    }
  ]
}
```

**Design implications:**
- Hooks don't see each other's output
- Execution order is non-deterministic
- Design hooks to be independent
- Don't rely on one hook's result in another

### Execution Timing

| Event | When Hooks Run |
|-------|----------------|
| PreToolUse | Before tool executes |
| PostToolUse | After tool completes |
| UserPromptSubmit | After user sends message |
| Stop | When agent considers stopping |
| SubagentStop | When subagent considers stopping |
| SubagentStart | When subagent begins execution |
| SessionStart | At session initialization |
| SessionEnd | When session terminates |
| PreCompact | Before context compaction |
| Notification | When notification sent |
| PermissionRequest | When permission dialog would show |

### Timeout Handling

**Default timeouts:**
- Command hooks: 60 seconds
- Prompt hooks: 30 seconds

**When timeout occurs:**
- Hook execution stops
- Hook treated as non-blocking (returns empty)
- Warning logged in debug mode
- Other hooks continue normally

### Exit Code Behavior

| Exit Code | Meaning | Effect |
|-----------|---------|--------|
| 0 | Success | stdout shown in transcript |
| 2 | Blocking error | stderr fed back to Claude |
| Other | Non-blocking error | Logged, continues |

## Temporarily Active Hooks

Create hooks that activate conditionally using flag files or configuration.

### Pattern 1: Flag File Activation

```bash
#!/bin/bash
set -euo pipefail

# Only active when flag file exists
FLAG_FILE="$CLAUDE_PROJECT_DIR/.enable-strict-validation"

if [ ! -f "$FLAG_FILE" ]; then
  # Flag not present, skip validation
  exit 0
fi

# Flag present, run validation
input=$(cat)
# ... validation logic ...
```

**Use cases:**
- Enable strict validation only when needed
- Temporary debugging hooks
- Feature flags for hooks

### Pattern 2: Configuration-Based Activation

```bash
#!/bin/bash
set -euo pipefail

# Check configuration for activation
CONFIG_FILE="$CLAUDE_PROJECT_DIR/.claude/plugin-config.json"

if [ -f "$CONFIG_FILE" ]; then
  enabled=$(jq -r '.strictMode // false' "$CONFIG_FILE")
  if [ "$enabled" != "true" ]; then
    exit 0  # Not enabled, skip
  fi
fi

# Enabled, run hook logic
input=$(cat)
# ... hook logic ...
```

### Pattern 3: Settings File Activation

```bash
#!/bin/bash
set -euo pipefail

STATE_FILE=".claude/my-plugin.local.md"

# Quick exit if not configured
if [[ ! -f "$STATE_FILE" ]]; then
  exit 0
fi

# Read enabled flag from YAML frontmatter
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$STATE_FILE")
ENABLED=$(echo "$FRONTMATTER" | grep '^enabled:' | sed 's/enabled: *//')

if [[ "$ENABLED" != "true" ]]; then
  exit 0  # Disabled
fi

# Run hook logic
input=$(cat)
# ... hook logic ...
```

**Best practice:** Document activation mechanism in plugin README so users know how to enable/disable hooks.

## Debugging Hooks

### Enable Debug Mode

```bash
claude --debug
```

Look for:
- Hook registration logs
- Hook execution timing
- Input/output JSON
- Error messages
- Timeout warnings

### View Loaded Hooks

Use `/hooks` command to review loaded hooks in current session:

```
> /hooks

PreToolUse:
  - matcher: Write|Edit
    type: command
    command: ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh

Stop:
  - matcher: *
    type: prompt
    prompt: Verify task completion
```

### Test Hook Scripts Directly

```bash
# Create test input
echo '{"tool_name": "Write", "tool_input": {"file_path": "/test"}}' > test-input.json

# Run hook script
cat test-input.json | bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh

# Check exit code
echo "Exit code: $?"

# Validate JSON output
cat test-input.json | bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh | jq .
```

### Common Issues

**Hook not triggering:**
- Check matcher pattern matches tool name
- Verify JSON syntax in hooks.json
- Restart Claude Code after changes
- Check `/hooks` to see if hook loaded

**Hook script failing:**
- Test script directly in terminal
- Check script has execute permission
- Verify ${CLAUDE_PLUGIN_ROOT} resolves
- Check for missing dependencies

**Timeout issues:**
- Reduce hook complexity
- Add internal timeouts
- Cache expensive operations
- Use prompt hooks for complex logic

## Performance Considerations

### Optimization Tips

1. **Use command hooks for quick checks**
   - Fast deterministic validations
   - File existence checks
   - Pattern matching

2. **Use prompt hooks for complex reasoning**
   - Context-aware decisions
   - Multiple condition evaluation
   - Natural language analysis

3. **Cache results when possible**
   ```bash
   CACHE_FILE="/tmp/hook-cache-$$"
   if [ -f "$CACHE_FILE" ] && [ "$(stat -c %Y "$CACHE_FILE")" -gt $(($(date +%s) - 60)) ]; then
     cat "$CACHE_FILE"
     exit 0
   fi
   # ... expensive operation ...
   echo "$result" > "$CACHE_FILE"
   echo "$result"
   ```

4. **Minimize I/O in hot paths**
   - Avoid reading large files
   - Don't write to disk unnecessarily
   - Use in-memory processing

### Hook Execution Overhead

| Hook Type | Typical Time | Impact |
|-----------|--------------|--------|
| Simple command | 10-50ms | Minimal |
| Complex command | 100-500ms | Noticeable |
| Prompt hook | 500-2000ms | Significant |

Design hooks to be as fast as possible, especially for frequently triggered events like PreToolUse.
