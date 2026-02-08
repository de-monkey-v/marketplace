# Common Plugin Patterns

Reference patterns for different plugin architectures.

## Minimal Plugin

Single command with no dependencies:
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json    # Just name field
└── commands/
    └── hello.md       # Single command
```

**Use when:** Simple utility, single purpose, no complex workflows.

## Full-Featured Plugin

Complete plugin with all component types:
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/          # User-facing commands
├── agents/            # Specialized subagents
├── skills/            # Auto-activating skills
├── hooks/             # Event handlers
│   ├── hooks.json
│   └── scripts/
├── .mcp.json          # External integrations
└── scripts/           # Shared utilities
```

**Use when:** Complex workflows, multiple entry points, external integrations.

## Skill-Focused Plugin

Plugin providing only skills (knowledge/guidance):
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    ├── skill-one/
    │   └── SKILL.md
    └── skill-two/
        └── SKILL.md
```

**Use when:** Providing domain knowledge, coding standards, best practices.

## Agent-Centric Plugin

Plugin with agents as primary functionality:
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   ├── analyzer.md
│   ├── generator.md
│   └── validator.md
└── skills/
    └── domain-knowledge/
        └── SKILL.md
```

**Use when:** Autonomous task execution, specialized workflows.

## Hook-Based Plugin

Automation through event handlers:
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── hooks/
│   ├── hooks.json
│   └── scripts/
│       ├── validate.sh
│       └── notify.sh
└── README.md
```

**Use when:** Code validation, notifications, pre/post processing.

## Command Workflow Plugin

Multiple commands forming a workflow:
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── init.md
│   ├── process.md
│   └── finalize.md
└── skills/
    └── workflow-guide/
        └── SKILL.md
```

**Use when:** Multi-step processes, deployment pipelines, project setup.

## Hybrid Plugin

Combining multiple patterns:
```
enterprise-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/          # Entry points
├── agents/            # Heavy lifting
├── skills/            # Domain knowledge
├── hooks/             # Automation
└── .mcp.json          # External services
```

**Use when:** Enterprise needs, comprehensive tooling.
