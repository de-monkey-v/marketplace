# Script Reference Patterns Detail

## Context-Specific Usage Guide

### Pattern A: Hook Context — Detailed

When scripts are called from `hooks.json`, the Claude Code runtime handles `${CLAUDE_PLUGIN_ROOT}` expansion.

**hooks.json entry:**
```json
{
  "type": "command",
  "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/validate.py",
  "timeout": 15
}
```

**Script receives stdin JSON:**
```json
{
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file",
    "content": "..."
  },
  "session_id": "abc123"
}
```

**Script must output decision JSON:**
```json
{"decision": "allow", "systemMessage": "Validation passed"}
```
or
```json
{"decision": "deny", "systemMessage": "Blocked: sensitive path"}
```

**Exit codes:**
- `0` — Allow (stdout shown in transcript)
- `2` — Block (stderr fed back to Claude)
- Other — Non-blocking error

**Bash example (Hook context):**
```bash
#!/bin/bash
set -euo pipefail
input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

if [[ "$file_path" == /etc/* ]]; then
  echo '{"decision": "deny", "systemMessage": "System path blocked"}' >&2
  exit 2
fi
echo '{"decision": "allow", "systemMessage": "OK"}'
```

**Python example (Hook context):**
```python
#!/usr/bin/env python3
import json, sys
input_data = json.loads(sys.stdin.read())
tool_name = input_data.get("tool_name", "")
# ... validation logic ...
print(json.dumps({"decision": "allow", "systemMessage": "OK"}))
```

### Pattern B: Skill/Command Context — Detailed

Skills and commands instruct Claude to run scripts via the Bash tool.

**In a skill `.md` file:**
```markdown
## How to Search

Run the search script:
```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/search.sh -q "query" -c 10
```

The script returns JSON results to stdout.
```

**In a command `.md` file:**
```markdown
---
description: "Run analysis"
allowed-tools: Bash(bash ${CLAUDE_PLUGIN_ROOT}/scripts/*)
---

Execute the analysis:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/analyze.py "$ARGUMENTS"
```
```

**Key differences from Hook context:**
- Input via CLI arguments (not stdin)
- Output via stdout (not decision JSON)
- Shell expands `${CLAUDE_PLUGIN_ROOT}` (not Claude Code runtime)
- `allowed-tools` should grant Bash access for the script path

### Pattern C: Dynamic Context Injection — Detailed

The `!` backtick syntax runs scripts during skill preprocessing.

**In SKILL.md:**
```markdown
## Current Project State
!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/project-status.sh`

## Available Resources
!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/list-resources.py --format markdown`
```

**How it works:**
1. Claude Code loads the skill
2. Before sending to Claude, it finds `!` backtick blocks
3. Executes each command in a shell
4. Replaces the block with the command's stdout
5. Claude sees the final content with dynamic data injected

**Best practices:**
- Keep scripts fast (< 5 seconds)
- Output in markdown format for readability
- Handle errors gracefully (empty output is better than error traces)
- Suitable for: status checks, environment info, resource listings

## Real Plugin Code Examples

### search plugin: Skill -> Script (Pattern B)

```markdown
# In skills/tavily-search/SKILL.md
## Execution
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-search.sh "$QUERY"
```

Script: `scripts/tavily-search.sh`
- Takes query as positional argument
- Uses `TAVILY_API_KEY` environment variable
- Outputs JSON search results to stdout

### notification plugin: Hook -> Script (Pattern A)

```json
// hooks/hooks.json
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/notify-complete.sh",
        "timeout": 10
      }]
    }]
  }
}
```

Script: `hooks/scripts/notify-complete.sh`
- Reads session data from stdin JSON
- Sends notification via webhook
- Exit 0 (always allow, notification is side effect)

### claude-team: Both Patterns (A + B)

Hook scripts for lifecycle management:
```json
{
  "type": "command",
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/team-lifecycle.sh"
}
```

Utility scripts called from skills:
```markdown
bash ${CLAUDE_PLUGIN_ROOT}/scripts/spawn-teammate.sh --role reviewer
```

## Usage Guide Template

After creating a script, provide this usage guide:

```markdown
### Usage Guide

**From Skills/Commands (Bash tool):**
```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/{name}.sh [args]
```

**From Skills (Dynamic injection):**
```
!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/{name}.sh`
```

**From Hooks (hooks.json):**
```json
{
  "type": "command",
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/{name}.sh",
  "timeout": 30
}
```

**allowed-tools hint:**
```yaml
allowed-tools: Bash(bash ${CLAUDE_PLUGIN_ROOT}/scripts/*)
```
```
