---
name: script-development
description: "Script development patterns and best practices for Claude Code plugins. Activation: create a script, write a bash script, make a Python utility, 스크립트 개발, 유틸리티 스크립트, 스크립트 작성"
---

# Script Development Guide

Development patterns and best practices for executable scripts in Claude Code plugins.
Scripts are standalone utilities (`.sh` or `.py`) that provide API integration, data processing, validation, and automation capabilities.

## Script Reference Patterns

Scripts behave differently depending on the calling context. This is the most critical concept for script development.

### Pattern A: Hook Context (Runtime Variable Expansion)

When a hook's `hooks.json` references a script, `${CLAUDE_PLUGIN_ROOT}` is expanded by the **Claude Code hook runtime**.
The script receives JSON event data via stdin and communicates decisions via exit codes.

```json
{
  "type": "command",
  "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/notifier.py",
  "timeout": 15
}
```

- **Expanded by**: Claude Code hook runtime
- **Input**: stdin JSON (hook event data)
- **Output**: JSON decision + exit code (0=allow, 2=block)
- **Location**: `hooks/scripts/` (hook-specific scripts)

### Pattern B: Skill/Command Context (Bash Tool Execution)

When a skill or command `.md` file instructs Claude to run a script, Claude invokes it via the Bash tool.
The **shell** expands `${CLAUDE_PLUGIN_ROOT}`.

```markdown
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-search.sh "query"
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-search.py "topic" --count 20
```

- **Expanded by**: Bash shell (when Claude calls Bash tool)
- **Input**: CLI arguments (argparse/getopts)
- **Output**: stdout (JSON or text)
- **Location**: `scripts/` (plugin-level) or `skills/*/scripts/` (skill-level)

**Important**: Skills/commands that use Bash to call scripts should declare it in `allowed-tools`:
```yaml
allowed-tools: Bash(bash ${CLAUDE_PLUGIN_ROOT}/scripts/*)
```

### Pattern C: Dynamic Context Injection (Preprocessing)

The `!` backtick syntax in skills preprocesses script output before the skill content reaches Claude.

```markdown
## Current Status
!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/check-status.sh`
```

- **Expanded by**: Claude Code preprocessor -> shell
- **Timing**: Before skill content is delivered to Claude
- **Use case**: Injecting dynamic data into skill context

### Real-World Plugin Examples

| Plugin | Pattern | Usage |
|--------|---------|-------|
| search | B (Skill->Script) | Skills instruct Bash tool to call `tavily-search.sh`, `brave-search.py` |
| notification | A (Hook->Script) | Hook triggers `slack-notify.sh` via stdin JSON |
| claude-team | A+B (Both) | Hook scripts for lifecycle + utility scripts for team management |

## Script Type Selection Guide

| Criteria | Bash (.sh) | Python (.py) |
|----------|-----------|--------------|
| Simple file/text ops | Preferred | Overkill |
| Pipeline/piping | Preferred | Possible |
| JSON processing | jq required | Native |
| API calls (simple) | curl | urllib/requests |
| API calls (complex) | Difficult | Preferred |
| Error handling | Limited | Rich (try/except) |
| Argument parsing | getopts (basic) | argparse (full) |
| Data structures | Arrays only | Full (dict, list, class) |
| Cross-platform | Check commands | More portable |

**Rule of thumb**: If it needs `jq` more than twice or complex error handling, use Python.

## Placement Rules

| Level | Path | When to Use |
|-------|------|-------------|
| Plugin-level | `{plugin}/scripts/` | Shared across multiple skills/commands |
| Skill-level | `{plugin}/skills/{name}/scripts/` | Used only by a specific skill |

- Scripts referenced by hooks go in `hooks/scripts/` (managed by hook-creator)
- Scripts referenced by skills/commands go in `scripts/` or `skills/*/scripts/`

## Interface Design

### CLI Arguments (Pattern B/C)

**Bash (getopts):**
```bash
while getopts "q:c:o:h" opt; do
  case $opt in
    q) QUERY="$OPTARG" ;;
    c) COUNT="$OPTARG" ;;
    o) OUTPUT="$OPTARG" ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done
```

**Python (argparse):**
```python
parser = argparse.ArgumentParser(description="Script purpose")
parser.add_argument("query", help="Search query")
parser.add_argument("--count", type=int, default=10)
parser.add_argument("--output", choices=["json", "text"], default="json")
```

### Environment Variables

Use `${CLAUDE_PLUGIN_ROOT}` for all internal paths:
```bash
SCRIPT_DIR="${CLAUDE_PLUGIN_ROOT}/scripts"
DATA_DIR="${CLAUDE_PLUGIN_ROOT}/data"
```

### Exit Codes

| Code | Meaning | Context |
|------|---------|---------|
| 0 | Success | All contexts |
| 1 | General error | All contexts |
| 2 | Blocking decision | Hook context (Pattern A) |

### Output Format

- **JSON output** for structured data (API responses, parsed results)
- **Plain text** for human-readable output (status, logs)
- **Always output to stdout**; errors to stderr

## Error Handling Patterns

### Bash
```bash
#!/bin/bash
set -euo pipefail

# Trap for cleanup
cleanup() { rm -f "$TMPFILE"; }
trap cleanup EXIT

# Error with message
die() { echo "ERROR: $1" >&2; exit "${2:-1}"; }

# Validate dependencies
command -v jq >/dev/null 2>&1 || die "jq is required"
```

### Python
```python
#!/usr/bin/env python3
import sys

try:
    result = main()
    print(json.dumps(result))
except FileNotFoundError as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Unexpected: {e}", file=sys.stderr)
    sys.exit(1)
```

## Portable Path Handling

Always use `${CLAUDE_PLUGIN_ROOT}` — never hardcode absolute paths:

```bash
# Correct
CONFIG="${CLAUDE_PLUGIN_ROOT}/config/settings.json"

# Wrong - breaks portability
CONFIG="/home/user/.claude/plugins/my-plugin/config/settings.json"
```

## Security Best Practices

- **Always quote variables**: `"$var"` not `$var`
- **Never use `eval`** with untrusted input
- **Validate inputs** before use
- **No hardcoded secrets** — use environment variables
- **Use `mktemp`** for temporary files
- **Avoid `shell=True`** in Python subprocess calls

See [references/security-guidelines.md](references/security-guidelines.md) for comprehensive security guidance.

## Progressive Reference Guide

For detailed patterns, see:
- **[references/bash-patterns.md](references/bash-patterns.md)** — Bash scripting patterns (getopts, jq, curl, temp files, color output)
- **[references/python-patterns.md](references/python-patterns.md)** — Python scripting patterns (argparse, urllib, json, subprocess)
- **[references/security-guidelines.md](references/security-guidelines.md)** — Security guidelines (secrets, injection, path validation, variable quoting)
- **[references/reference-patterns.md](references/reference-patterns.md)** — Script reference patterns detail (per-context usage, real plugin code examples)
