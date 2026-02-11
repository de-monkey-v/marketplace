---
name: "codex"
description: "Run prompts via Codex CLI headless mode"
user-invocable: true
---

# Codex CLI Headless

Non-interactive execution using `codex exec` and `codex review`.

## Default Model

Default model: `gpt-5.3-codex`

## Basic Usage

```bash
codex exec -m gpt-5.3-codex -s read-only "your prompt"
```

## Key Options

| Option | Description |
|--------|-------------|
| `exec "prompt"` | Execute a prompt non-interactively |
| `review` | Review code changes |
| `-m model` | Model selection |
| `-s read-only` | Sandbox: read-only (no file modifications) |
| `-` | Read input from stdin |

## Commands

### exec — Run a prompt

```bash
# Direct prompt
codex exec -m gpt-5.3-codex -s read-only "Explain this code"

# With stdin input
cat file.py | codex exec -m gpt-5.3-codex -s read-only - "Analyze this"
```

### review — Review code changes

```bash
# Review uncommitted changes
codex review --uncommitted "Review these changes"

# Review against a branch
codex review --base main

# Review with specific instructions
codex review --uncommitted "Check for security vulnerabilities"
```

## Examples

```bash
# File analysis
cat file.py | codex exec -m gpt-5.3-codex -s read-only - "Analyze this"

# Git diff review
codex review --uncommitted "Review this"

# Review against main branch
codex review --base main "Focus on breaking changes"
```
