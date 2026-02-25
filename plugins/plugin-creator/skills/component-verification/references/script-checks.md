# Script Verification: 2 Parallel Tasks

## Overview

Each created/modified script is verified by 2 parallel Tasks:

| # | Agent | Focus |
|---|-------|-------|
| V1 | `claude-code-guide` | Structure & quality |
| V2 | `claude-code-guide` | Script security |

## V1: Script Structure & Quality (claude-code-guide)

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Verify script structure and quality"
- prompt: |
    <task-context>
    <component-type>script</component-type>
    <component-path>{path to script file}</component-path>
    <plugin-path>{path to plugin or .claude/ root}</plugin-path>
    <validation-type>script-structure-quality</validation-type>
    </task-context>

    <instructions>
    Read the script file and verify structure and quality:

    1. **Shebang line** (Critical):
       - Bash scripts: must start with `#!/bin/bash`
       - Python scripts: must start with `#!/usr/bin/env python3`
       - Missing shebang prevents direct execution

    2. **Error handling** (Major):
       - Bash: `set -euo pipefail` must be present near the top
       - Python: main logic wrapped in `try-except` with proper error messages
       - Errors should output to stderr, not stdout

    3. **Documentation header** (Major):
       - Script purpose description
       - Usage instructions with examples
       - Options/arguments documentation
       - Required environment variables listed

    4. **Portable paths** (Major):
       - Uses `${CLAUDE_PLUGIN_ROOT}` for plugin-internal paths
       - No hardcoded absolute paths to user directories
       - Relative paths within the plugin are acceptable

    5. **Exit codes** (Minor):
       - Documented or consistent with conventions
       - 0 for success, non-zero for errors
       - Hook scripts: 0=allow, 2=block

    6. **Output format** (Minor):
       - JSON output uses valid JSON structure
       - Text output is clean and parseable
       - Errors go to stderr, results to stdout

    Report findings using severity: Critical / Major / Minor.
    If no issues found, report "PASS".
    </instructions>
```

## V2: Script Security (claude-code-guide)

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Verify script security"
- prompt: |
    <task-context>
    <component-type>script</component-type>
    <component-path>{path to script file}</component-path>
    <plugin-path>{path to plugin or .claude/ root}</plugin-path>
    <validation-type>script-security</validation-type>
    </task-context>

    <instructions>
    Read the script file and verify security practices:

    1. **Hardcoded secrets** (Critical):
       - No API keys, tokens, passwords, or credentials in code
       - Check for patterns: strings matching key/token/secret formats
       - Environment variables should be used instead
       - Report any hardcoded secrets as Critical

    2. **Command injection** (Critical):
       - Bash: No `eval` with untrusted input, no unquoted `$(...)` with user data
       - Python: No `shell=True` in subprocess with user input
       - No string interpolation in shell commands with untrusted data
       - Report injection vectors as Critical

    3. **Input validation** (Major):
       - User-provided arguments are validated (type, range, format)
       - File paths checked for traversal patterns (`..`)
       - Expected data formats verified before processing
       - Report missing validation as Major

    4. **Variable quoting (Bash)** (Major):
       - All variable references quoted: `"$var"` not `$var`
       - Array expansion quoted: `"${arr[@]}"` not `${arr[@]}`
       - Command substitution quoted: `"$(cmd)"` not `$(cmd)`
       - Report unquoted variables as Major

    5. **Temp file safety** (Minor):
       - Uses `mktemp` (Bash) or `tempfile` module (Python)
       - No predictable temp file paths like `/tmp/myapp_output`
       - Cleanup via trap (Bash) or context manager (Python)
       - Report unsafe temp usage as Minor

    6. **Python subprocess safety** (Major):
       - No `shell=True` with user-controllable input
       - Commands passed as list, not string
       - If `shell=True` is needed, input is properly validated/escaped
       - Report unsafe subprocess as Major

    Report findings using severity: Critical / Major / Minor.
    If no issues found, report "PASS".
    </instructions>
```

## Parallel Launch Example

Launch both Tasks in a single message:

```
[Message with 2 Task tool calls]

Task 1: claude-code-guide structure & quality (V1)
Task 2: claude-code-guide script security (V2)
```

## Result Integration

Collect results from both Tasks and merge:

1. Aggregate all Critical/Major/Minor findings
2. Apply overall judgment (PASS/WARN/FAIL)
3. If FAIL -> trigger auto-fix loop (see [auto-fix-loop.md](auto-fix-loop.md))
