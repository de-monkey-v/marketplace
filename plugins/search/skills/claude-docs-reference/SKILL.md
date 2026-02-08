# Claude Docs Reference Skill

Answers questions about Claude Code, Claude Agent SDK, and Claude API based on official documentation.

## Trigger Keywords

| Keyword | Target |
|---------|--------|
| Claude Code, CLI, slash command | Claude Code general |
| plugin, skill | Plugin/skill system |
| hook, PreToolUse, PostToolUse | Hook automation |
| MCP, Model Context Protocol | MCP integration |
| subagent, Task tool | Subagents |
| Agent SDK, Python SDK, TypeScript SDK | Agent SDK |
| Claude API, Messages API, Tool Use | Claude API |
| `!\`, backtick, dynamic context, preprocessing | Skill advanced patterns |

## Category References

Based on question type, read the relevant reference file and access URLs to query latest information.

| Question Type | Reference File |
|--------------|---------------|
| CLI commands, flags, options | [`references/command.md`](references/command.md) |
| Subagents, Task tool | [`references/subagent.md`](references/subagent.md) |
| Hooks, event automation | [`references/hook.md`](references/hook.md) |
| MCP server integration | [`references/mcp.md`](references/mcp.md) |
| Skill development, `!\` dynamic context, ultrathink | [`references/skill.md`](references/skill.md) |
| Plugin development | [`references/plugin.md`](references/plugin.md) |
| Marketplace | [`references/marketplace.md`](references/marketplace.md) |
| Best practices, engineering | [`references/engineering.md`](references/engineering.md) |
| Claude API | [`references/api.md`](references/api.md) |
| Agent SDK | [`references/sdk.md`](references/sdk.md) |

## Workflow

```
1. Analyze question -> Identify category
2. Read relevant references/*.md file
3. Access URLs via WebFetch to query latest info
4. Synthesize information into answer
```

## Output Format

```markdown
## [Question Topic]

### Answer

[Answer based on latest info from WebFetch]

### Code Examples (if applicable)

```[language]
[example code]
```

### Reference Docs

- [Doc title](URL)
```

## Important Notes

- **Always access URLs** to verify latest information
- Never guess - **answer based on documentation only**
- General libraries (React, FastAPI, etc.) are handled by context7-searcher
