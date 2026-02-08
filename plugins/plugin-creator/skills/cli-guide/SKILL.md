---
name: cli-guide
description: Claude Code CLI usage guide. This skill should be used when the user asks about "CLI options", "--debug usage", "--plugin-dir for plugin testing", "--agents flag", "--allowedTools settings", "claude -p mode", "SDK mode", "non-interactive mode", "CLI 옵션", "--debug 사용법", "비인터랙티브 모드".
---

# Claude Code CLI Guide

Guide to Claude Code CLI commands, flags, and usage patterns.

---

## Basic Commands

### claude (default)

Run in interactive REPL mode:

```bash
claude                     # Default launch
claude "query"             # Launch with initial prompt
claude -c                  # Continue last session
claude -r <session-id>     # Resume specific session
```

### claude -p (Print/SDK mode)

Non-interactive mode that exits after a single response:

```bash
echo "query" | claude -p            # stdin input
claude -p "query"                   # Direct input
cat file.txt | claude -p "analyze"  # Analyze file contents
```

**SDK mode characteristics**:
- Exits after single turn response
- Suitable for pipelines/automation
- Control output format with `--output-format`

### Other Commands

```bash
claude mcp                 # MCP server management
claude config              # Settings management
claude update              # CLI update
```

---

## Flag Categories (Quick Reference)

| Category | Key Flags | Purpose |
|----------|-----------|---------|
| **Debugging** | `--debug`, `--verbose` | Log output, problem diagnosis |
| **Plugins** | `--plugin-dir` | Local plugin testing |
| **Permissions** | `--allowedTools`, `--permission-mode` | Tool usage restrictions |
| **Model** | `--model`, `--agents` | Model/agent configuration |
| **Prompts** | `--system-prompt`, `--append-system-prompt` | System prompt customization |
| **Output** | `--output-format`, `--json-schema` | SDK output format |
| **Session** | `--resume`, `--continue`, `--session-id` | Session management |
| **MCP** | `--mcp-config` | MCP server configuration |

> Detailed flag list: `references/flags-by-category.md`

---

## Essential Flags for Plugin Developers

### --plugin-dir (Local Plugin Testing)

Immediately load a plugin under development:

```bash
# Single plugin
claude --plugin-dir ./my-plugin "test command"

# Multiple plugins
claude --plugin-dir ./plugin-a --plugin-dir ./plugin-b "query"

# Test marketplace plugin
claude --plugin-dir /home/user/dev/marketplace/plugins/my-plugin "query"
```

### --debug (Debug Logs)

Output debug information by category:

```bash
claude --debug "mcp" "query"           # MCP-related logs
claude --debug "hooks" "query"         # Hook execution logs
claude --debug "api,mcp" "query"       # Multiple categories
claude --debug "all" "query"           # All logs
claude --debug "all,!statsig" "query"  # Exclude statsig
```

**Debug categories**:
- `api`: API requests/responses
- `mcp`: MCP server communication
- `hooks`: Hook triggers/execution
- `file`: File operations
- `tool`: Tool invocations
- `statsig`: Feature flags

### --verbose

Detailed execution information output (more info when used with --debug):

```bash
claude --verbose "query"
claude --debug "mcp" --verbose "query"
```

### --agents (Dynamic Agent Definitions)

Define temporary agents without a plugin:

```bash
claude --agents '[{
  "name": "test-agent",
  "description": "Test agent",
  "prompt": "You are a test assistant"
}]' "test query"
```

> Detailed format: `references/agents-flag-format.md`

---

## Permission Control Flags

### --allowedTools / --disallowedTools

Restrict available tools:

```bash
# Read-only mode
claude --allowedTools "Read,Grep,Glob" "analyze code"

# Block specific tools
claude --disallowedTools "Bash,Write" "review code"
```

### --tools (SDK mode)

Control tool behavior in SDK mode:

```bash
claude -p --tools "Read,Grep" "analyze"
```

### --permission-mode

Permission presets:

```bash
claude --permission-mode default    # Default (prompt)
claude --permission-mode auto       # Auto-allow
claude --permission-mode plan       # Plan mode only
```

---

## SDK Mode Usage

### Basic Patterns

```bash
# Simple question
claude -p "What is TypeScript?"

# File analysis
cat package.json | claude -p "list dependencies"

# JSON output
claude -p --output-format json "query"
```

### Structured Output

```bash
# Force output format with JSON Schema
claude -p --json-schema '{"type":"object","properties":{"summary":{"type":"string"}}}' "summarize"
```

### Streaming

```bash
# Streaming JSON output
claude -p --output-format stream-json "long query"
```

> Detailed formats: `references/output-formats.md`

---

## Common Workflows

### 1. Plugin Development & Testing

```bash
# Test plugin under development
claude --plugin-dir ./my-plugin "run /my-command"

# Verify hook behavior in debug mode
claude --plugin-dir ./my-plugin --debug "hooks" "trigger hook"

# Test with only specific tools allowed
claude --plugin-dir ./my-plugin --allowedTools "Read,Grep" "analyze"
```

### 2. Problem Diagnosis

```bash
# Diagnose MCP connection issues
claude --debug "mcp" --verbose "use mcp tool"

# All logs output (excluding noise)
claude --debug "all,!statsig,!file" "problematic query"
```

### 3. Automation Scripts

```bash
#!/bin/bash
# Automate code review in CI
git diff HEAD~1 | claude -p --output-format json \
  --json-schema '{"type":"object","properties":{"issues":{"type":"array"}}}' \
  "find issues in this diff"
```

### 4. Session Management

```bash
# Continue working on a session
claude -c                              # Last session
claude -r abc123                       # Specific session ID

# Fork session (branch)
claude --fork-session abc123 "new direction"
```

---

## References

For detailed information, see the following documents:

| Document | Content |
|----------|---------|
| `references/flags-by-category.md` | Complete flag reference |
| `references/system-prompt-flags.md` | System prompt customization |
| `references/agents-flag-format.md` | --agents JSON format |
| `references/output-formats.md` | SDK output formats |
| `examples/plugin-testing.md` | Plugin testing workflows |
| `examples/debugging-patterns.md` | Debugging patterns |
