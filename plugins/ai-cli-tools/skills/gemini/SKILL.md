---
name: "gemini"
description: "Run prompts via Gemini CLI headless mode"
user-invocable: true
---

# Gemini CLI Headless

Non-interactive execution using the `gemini -p` option.

## Default Model

Default model: `gemini-3.0-pro-preview`

## Basic Usage

```bash
gemini -m gemini-3.0-pro-preview -p "your prompt"
```

## Key Options

| Option | Description |
|--------|-------------|
| `-p "prompt"` | Headless mode |
| `-m model` | Model selection |
| `-o json` | JSON output |
| `-y` | Auto-approve (YOLO) |

## Examples

```bash
# File analysis
cat file.py | gemini -m gemini-3.0-pro-preview -p "Analyze this"

# Git diff review
git diff | gemini -m gemini-3.0-pro-preview -p "Review this"

# JSON response
gemini -m gemini-3.0-pro-preview -p "your prompt" -o json | jq '.response'
```
