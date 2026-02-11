# AI CLI Tools

A plugin for leveraging AI CLI tools within Claude Code.

## Supported Tools

| Tool | Status | Components |
|------|--------|-----------|
| Gemini CLI | ✅ Supported | Skill + Agent |
| Codex CLI | ✅ Supported | Skill + Agent |

## Installation

```bash
/plugin install ai-cli-tools@de-monkey-v/marketplace
/plugin enable ai-cli-tools
```

## Agent

### llms

Invokes Gemini CLI or Codex CLI to perform code analysis/review. **Cannot modify files**.

The agent automatically detects which provider to use based on keywords in your message:
- **Codex**: `codex`, `openai`, `o3`, `o4-mini`, `gpt`
- **Gemini**: `gemini`, `google`
- **Default**: Gemini (when no keyword is detected)

You can also specify explicitly with `--provider=gemini` or `--provider=codex`.

**Usage examples:**
```
@llms review this with gemini
@llms codex 호출해서 이 코드 리뷰해줘
@llms --provider=codex review this PR
@llms openai한테 현재 변경사항 리뷰 받아봐
@llms analyze current changes
```

**Capabilities:**
- Code review/analysis via Gemini CLI or Codex CLI
- Solution research via web search
- Git change analysis

## Skills

### gemini

Guide for using Gemini CLI headless mode (`gemini -p`).

**Activation keywords**: gemini cli, gemini headless, gemini -p

### codex

Guide for using Codex CLI headless mode (`codex exec`).

**Activation keywords**: codex cli, codex headless, codex exec

## Requirements

- At least one CLI tool must be installed:
  - Gemini CLI: [Official installation guide](https://github.com/google-gemini/gemini-cli)
  - Codex CLI: [Official installation guide](https://github.com/openai/codex)
- Run `/ai-cli-tools:setup` to install both tools

## License

MIT

> This plugin respects the language setting in `.hyper-team/metadata.json`. Run `/hyper-team:setup` to configure.
