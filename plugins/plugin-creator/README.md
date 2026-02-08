# Plugin Creator

A toolkit for easily creating all components (plugins, agents, skills, commands, hooks) of Claude Code plugins.

## Overview

plugin-creator provides 7 skills, 7 agents, and 4 commands to help you create high-quality Claude Code plugins.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Commands                              │
│  (Orchestration: user interaction + agent coordination)      │
│                                                              │
│  /create-plugin     /modify-plugin     /validate            │
│  /create-orchestration-command                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                        Agents                                │
│  (Execution: autonomous file creation/validation)            │
│                                                              │
│  skill-creator    agent-creator    command-creator          │
│  hook-creator     settings-creator plugin-validator          │
│  skill-reviewer                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                        Skills                                │
│  (Knowledge: guides, patterns, best practices)               │
│                                                              │
│  plugin-development   skill-development   agent-development │
│  command-development  hook-development    plugin-settings   │
│  cli-guide                                                   │
└─────────────────────────────────────────────────────────────┘
```

### Role Distribution

| Component | Role | Activation Method |
|-----------|------|-------------------|
| **Commands** | Orchestrate agents while interacting with users | `/command-name` input |
| **Agents** | Autonomously execute file creation, validation, etc. | Called via Task tool from commands |
| **Skills** | Provide knowledge/guides, preloaded into agents | Auto-selected based on description |

## Quick Start

### Full Plugin Creation (Recommended)

```bash
/plugin-creator:create-plugin "database migration management tool"
```

4-phase workflow:
1. **Discovery & Planning** - Identify purpose, design components
2. **Structure Setup** - Create directories, manifest
3. **Component Implementation** - Create components using agents
4. **Validation & Completion** - Validate, finalize

### Modify Existing Plugin

```bash
/plugin-creator:modify-plugin my-plugin
# or by path
/plugin-creator:modify-plugin ./plugins/my-plugin
```

3-phase workflow:
1. **Analysis** - Assess current state, plan modifications
2. **Implementation** - Execute additions/modifications/deletions
3. **Validation & Completion** - Validate, version bump, finalize

### Individual Component Creation

Skills are automatically triggered to guide you:

```
"create a plugin" → plugin-development skill
"create an agent" → agent-creator agent delegation
"create a skill" → skill-creator agent delegation
"create a command" → command-creator agent delegation
"create a hook" → hook-creator agent delegation
```

## Commands (4)

| Command | Purpose |
|---------|---------|
| **/create-plugin** | Full plugin creation (4 Phases) |
| **/modify-plugin** | Modify existing plugin (3 Phases) |
| **/validate** | Validate plugin |
| **/create-orchestration-command** | Create orchestration command |

## Agents (7)

| Agent | Role | When to Use |
|-------|------|-------------|
| **skill-creator** | Create skill files | When adding skills |
| **skill-reviewer** | Review skill quality | After skill creation/modification |
| **agent-creator** | Create agent files | When adding agents |
| **command-creator** | Create command files | When adding commands |
| **hook-creator** | Create hook configuration | When adding hooks |
| **settings-creator** | Create settings files | When adding settings |
| **plugin-validator** | Full plugin validation | When validation is needed |

## Skills (7)

| Skill | Trigger | Purpose |
|-------|---------|---------|
| **plugin-development** | "create a plugin", "plugin structure" | Plugin structure, manifest |
| **skill-development** | "create a skill", "SKILL.md" | Skill creation, progressive disclosure |
| **agent-development** | "create an agent", "agent" | Agent creation, system prompts |
| **command-development** | "create a command", "command" | Slash commands, frontmatter |
| **hook-development** | "create a hook", "hook" | Event hooks, automation |
| **plugin-settings** | ".local.md", "settings" | Plugin settings patterns |
| **cli-guide** | "CLI options", "--debug" | Claude CLI usage |

## Orchestration Patterns

Recommended patterns for calling agents from commands:

### Agent Delegation Pattern

```markdown
## Phase N: Component Creation

**Delegate to skill-creator agent**:
- Information to pass: skill name, purpose, trigger phrases
- Expected output: skills/{name}/SKILL.md and supporting files

After creation, **delegate quality review to skill-reviewer agent**.
```

### Skill Load Pattern

```markdown
Load `plugin-creator:skill-development` skill.
```

See `skills/command-development/references/orchestration-patterns.md` for detailed patterns.

## Utility Scripts

```bash
# Hook validation
./skills/hook-development/scripts/validate-hook-schema.sh hooks.json

# Hook testing
./skills/hook-development/scripts/test-hook.sh hook.sh input.json

# Agent validation
./skills/agent-development/scripts/validate-agent.sh agent.md

# Settings parsing
./skills/plugin-settings/scripts/parse-frontmatter.sh settings.md
```

## Installation

```bash
# Install from marketplace
/plugin install plugin-creator@marketplace

# Or test locally
claude --plugin-dir /path/to/plugin-creator
```

## Best Practices

- **Security first**: Input validation, HTTPS, manage credentials via environment variables
- **Portability**: Use ${CLAUDE_PLUGIN_ROOT}, relative paths only
- **Testing**: Validate configuration before deployment, use debug mode
- **Documentation**: README, environment variable docs, usage examples

## Version History

- **1.1.0** - Command refactoring (Phase simplification), orchestration pattern additions
- **1.0.0** - Initial release

## Author

de-monkey-v

## License

MIT License

> This plugin respects the language setting in `.hyper-team/metadata.json`. Run `/hyper-team:setup` to configure.
