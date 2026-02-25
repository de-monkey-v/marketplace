# Hook Verification: 2 Parallel Tasks

## Overview

Each created/modified hook configuration is verified by 2 parallel Tasks:

| # | Agent | Focus |
|---|-------|-------|
| V1 | `claude-code-guide` | Event type validity |
| V2 | `claude-code-guide` | Script security |

## V1: Event Type Validity (claude-code-guide)

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Verify hook event type validity"
- prompt: |
    <task-context>
    <component-type>hook</component-type>
    <component-path>{path to hooks.json}</component-path>
    <validation-type>event-type-validity</validation-type>
    </task-context>

    <instructions>
    Read the hooks.json file and verify event types and structure:

    1. **Valid JSON syntax**: The file must be valid JSON

    2. **Event type validity**: Each hook must use one of these 17 valid events:
       - PreToolUse
       - PostToolUse
       - PostToolUseFailure
       - PermissionRequest
       - UserPromptSubmit
       - Stop
       - SubagentStop
       - SubagentStart
       - SessionStart
       - SessionEnd
       - PreCompact
       - Notification
       - TeammateIdle
       - TaskCompleted
       - ConfigChange
       - WorktreeCreate
       - WorktreeRemove

    3. **Matcher pattern**: Each hook should have a valid `matcher` field
       - For PreToolUse/PostToolUse: matcher specifies which tool(s)
       - Pattern can be exact match or wildcard

    4. **Hook structure**: Each hook entry should have:
       - `matcher`: tool/event pattern
       - `hooks`: array of hook actions
       - Each action should have `type` ("command" or "prompt") and appropriate fields

    Report any invalid event names as Critical.
    Report structural issues as Major.
    Report missing optional fields as Minor.
    If no issues found, report "PASS".
    </instructions>
```

## V2: Script Security (claude-code-guide)

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Verify hook script security"
- prompt: |
    <task-context>
    <component-type>hook</component-type>
    <component-path>{path to hooks.json}</component-path>
    <plugin-path>{path to plugin or .claude/ root}</plugin-path>
    <validation-type>script-security</validation-type>
    </task-context>

    <instructions>
    Read the hooks.json file and verify script security:

    1. **Command injection vulnerabilities**:
       - Check for unescaped variable interpolation in commands
       - Check for unsafe use of user input in shell commands
       - Look for patterns like `eval`, backtick execution, `$(...)` with untrusted input
       - Report as Critical if found

    2. **Path usage**:
       - Plugin hooks MUST use `${CLAUDE_PLUGIN_ROOT}` for paths to plugin-internal scripts
       - Hardcoded absolute paths break portability (Major)
       - Relative paths without ${CLAUDE_PLUGIN_ROOT} may fail (Major)

    3. **Script file existence**:
       - If hooks reference external scripts, verify those script files exist
       - Check that referenced script paths resolve correctly
       - Missing scripts are Critical issues

    4. **Execution permissions**:
       - Referenced shell scripts should be executable (check for .sh extension convention)
       - Note: actual permission check may need Bash tool

    5. **Sensitive data**:
       - No hardcoded credentials, tokens, or secrets in hook commands
       - No logging of sensitive environment variables
       - Report as Critical if found

    Report findings using severity: Critical / Major / Minor.
    If no issues found, report "PASS".
    </instructions>
```

## Parallel Launch Example

Launch both Tasks in a single message:

```
[Message with 2 Task tool calls]

Task 1: claude-code-guide event types (V1)
Task 2: claude-code-guide script security (V2)
```

## Result Integration

Collect results from both Tasks and merge:

1. Aggregate all Critical/Major/Minor findings
2. Apply overall judgment (PASS/WARN/FAIL)
3. If FAIL -> trigger auto-fix loop (see [auto-fix-loop.md](auto-fix-loop.md))
