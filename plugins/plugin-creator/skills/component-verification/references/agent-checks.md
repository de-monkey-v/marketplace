# Agent Verification: 2 Parallel Tasks

## Overview

Each created/modified agent is verified by 2 parallel Tasks:

| # | Agent | Focus |
|---|-------|-------|
| V1 | `claude-code-guide` | Frontmatter spec |
| V2 | `claude-code-guide` | System prompt quality |

## V1: Frontmatter Spec (claude-code-guide)

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Verify {agent-name} agent frontmatter spec"
- prompt: |
    <task-context>
    <component-type>agent</component-type>
    <component-path>{path to agent .md file}</component-path>
    <validation-type>frontmatter-spec</validation-type>
    </task-context>

    <instructions>
    Read the agent file and verify its frontmatter against Claude Code official agent specification:

    **Required fields:**
    - `name`: 3-50 characters, lowercase with hyphens
    - `description`: Must exist and be non-empty

    **Valid optional fields:**
    - `tools`: list of tools available to the agent
    - `disallowedTools`: list of explicitly disallowed tools
    - `model`: valid model (inherit/sonnet/opus/haiku)
    - `permissionMode`: permission mode setting
    - `maxTurns`: maximum number of turns
    - `skills`: list of skill references
    - `mcpServers`: MCP server configurations
    - `hooks`: hook configurations
    - `memory`: memory configuration
    - `background`: boolean for background execution
    - `isolation`: isolation mode

    **Critical constraints:**
    - Subagent nesting: agents (subagents) cannot spawn other subagents.
      Listing Task tool in an agent's tools field has no effect at runtime.
      If Task tool is listed, report as Major issue.

    **Check for:**
    - Missing required fields (Critical)
    - Invalid/unknown frontmatter fields (Major)
    - Name format violations — not kebab-case, outside 3-50 char range (Major)
    - Invalid model values (Major)
    - Task tool in tools list — subagent nesting violation (Major)

    Report findings using severity: Critical / Major / Minor.
    If no issues found, report "PASS".
    </instructions>
```

## V2: System Prompt Quality (claude-code-guide)

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Verify {agent-name} agent system prompt quality"
- prompt: |
    <task-context>
    <component-type>agent</component-type>
    <component-path>{path to agent .md file}</component-path>
    <plugin-path>{path to plugin or .claude/ root}</plugin-path>
    <validation-type>system-prompt-quality</validation-type>
    </task-context>

    <instructions>
    Read the agent file and verify the system prompt body (content after frontmatter):

    1. **XML structure** (recommended but not required):
       - Check for `<context>`, `<instructions>` sections
       - Check for `<examples>`, `<constraints>`, `<output-format>` if applicable
       - Well-organized structure improves agent effectiveness

    2. **Skill path references**:
       - If the agent references skills (e.g., "Load skill X"), verify the skill exists
       - Check skill paths match actual file locations within the plugin

    3. **Tools consistency**:
       - Tools listed in frontmatter `tools` field should align with tool usage
         described in the system prompt instructions
       - If instructions mention using Read/Write/Edit but tools doesn't list them,
         report as Major issue
       - If tools lists tools never mentioned in instructions, report as Minor

    4. **Description includes examples**:
       - Agent description should include example trigger phrases or use cases
       - Missing examples is a Minor issue

    Report findings using severity: Critical / Major / Minor.
    If no issues found, report "PASS".
    </instructions>
```

## Parallel Launch Example

Launch both Tasks in a single message:

```
[Message with 2 Task tool calls]

Task 1: claude-code-guide frontmatter (V1)
Task 2: claude-code-guide system prompt (V2)
```

## Result Integration

Collect results from both Tasks and merge:

1. Aggregate all Critical/Major/Minor findings
2. Apply overall judgment (PASS/WARN/FAIL)
3. If FAIL -> trigger auto-fix loop (see [auto-fix-loop.md](auto-fix-loop.md))
