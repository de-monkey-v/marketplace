# AI CLI Tools

A plugin for leveraging AI CLI tools within Claude Code.

## Supported Tools

| Tool | Status | Components |
|------|--------|-----------|
| Gemini CLI | ✅ Supported | Skill + Agent |

## Installation

```bash
/plugin install ai-cli-tools@de-monkey-v-marketplace
/plugin enable ai-cli-tools
```

## Agent

### llms

Invokes Gemini CLI to perform code analysis/review. **Cannot modify files**.

**Usage examples:**
```
@llms review this with gemini
@llms run a security analysis with gemini
@llms analyze current changes
```

**Capabilities:**
- Code review/analysis via Gemini CLI
- Solution research via web search
- Git change analysis

## Skill

### gemini

Guide for using Gemini CLI headless mode (`gemini -p`).

**Activation keywords**: gemini cli, gemini headless, gemini -p

## Requirements

- Gemini CLI must be installed: [Official installation guide](https://github.com/google-gemini/gemini-cli)

## License

MIT

> This plugin respects the language setting in `.hyper-team/metadata.json`. Run `/hyper-team:setup` to configure.
