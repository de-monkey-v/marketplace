# Writing Style Guide for Skills

This reference provides detailed guidance on writing style requirements for Claude Code plugin skills.

## Imperative/Infinitive Form

Write using verb-first instructions, not second person:

**Correct (imperative):**
```
To create a hook, define the event type.
Configure the MCP server with authentication.
Validate settings before use.
```

**Incorrect (second person):**
```
You should create a hook by defining the event type.
You need to configure the MCP server.
You must validate settings before use.
```

## Third-Person in Description

The frontmatter description must use third person:

**Correct:**
```yaml
description: This skill should be used when the user asks to "create X", "configure Y"...
```

**Incorrect:**
```yaml
description: Use this skill when you want to create X...
description: Load this skill when user asks...
```

## Objective, Instructional Language

Focus on what to do, not who should do it:

**Correct:**
```
Parse the frontmatter using sed.
Extract fields with grep.
Validate values before use.
```

**Incorrect:**
```
You can parse the frontmatter...
Claude should extract fields...
The user might validate values...
```

## Writing Principles

### Voice and Perspective

| Context | Voice | Example |
|---------|-------|---------|
| SKILL.md body | Imperative | "Create the hook configuration" |
| Description field | Third person | "This skill should be used when..." |
| System prompts (agents) | Second person | "You are an agent that..." |

### Clarity Guidelines

1. **Be specific**: Instead of "process the file", say "parse the YAML frontmatter"
2. **Be direct**: Instead of "it might be helpful to...", say "use X to..."
3. **Be consistent**: Use the same terminology throughout

### Common Transformations

| Avoid (2nd person) | Use (imperative) |
|--------------------|------------------|
| You should start by... | Start by... |
| You need to validate... | Validate... |
| You can use the tool... | Use the tool... |
| You must ensure... | Ensure... |
| You will want to... | Consider... |

### Paragraph Structure

**Good structure:**
```markdown
Parse the configuration file to extract settings. Use the sed command
to isolate the YAML frontmatter. Validate each field before use.
```

**Avoid:**
```markdown
First, you should parse the configuration file. Then you need to use
sed to extract the YAML. Finally, you must validate each field.
```

## Description Best Practices

### Trigger Phrase Patterns

**Strong triggers:**
- "create a hook"
- "add a PreToolUse hook"
- "validate tool use"
- "implement prompt-based hooks"

**Weak triggers:**
- "work with hooks"
- "hook help"
- "hooks"

### Description Structure

```yaml
description: This skill should be used when the user asks to "[action 1]",
"[action 2]", "[action 3]", or needs guidance on [topic]. Provides
[brief summary of what skill provides].
```

**Example:**
```yaml
description: This skill should be used when the user asks to "create a hook",
"add a PreToolUse hook", "validate tool use", or mentions hook events
(PreToolUse, PostToolUse, Stop). Provides comprehensive hooks API guidance.
```

## Quality Checklist

Before finalizing:

- [ ] All SKILL.md body text uses imperative form
- [ ] No "you should/need/can/must" constructions
- [ ] Description uses third person
- [ ] Description includes 3-5 specific trigger phrases
- [ ] Trigger phrases match actual user queries
- [ ] Instructions are clear and actionable
- [ ] Terminology is consistent throughout
