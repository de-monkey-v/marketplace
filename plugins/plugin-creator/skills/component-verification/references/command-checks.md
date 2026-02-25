# Command Verification: 2 Parallel Tasks

## Overview

Each created/modified command is verified by 2 parallel Tasks:

| # | Agent | Focus |
|---|-------|-------|
| V1 | `claude-code-guide` | Frontmatter spec |
| V2 | `claude-code-guide` | Content quality |

## V1: Frontmatter Spec (claude-code-guide)

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Verify {command-name} command frontmatter spec"
- prompt: |
    <task-context>
    <component-type>command</component-type>
    <component-path>{path to command .md file}</component-path>
    <validation-type>frontmatter-spec</validation-type>
    </task-context>

    <instructions>
    Read the command file and verify its frontmatter against Claude Code official
    command (slash command) specification:

    **Required field:**
    - `description`: Must exist and be non-empty

    **Valid optional fields:**
    - `name`: custom command name
    - `allowed-tools`: list of tools the command can use
    - `argument-hint`: hint text shown to user for arguments
    - `model`: model to use for this command
    - `context`: context configuration
    - `agent`: agent to delegate to
    - `hooks`: hook configurations
    - `disable-model-invocation`: boolean
    - `user-invocable`: boolean (default true for commands)

    **Check for:**
    - Missing description field (Critical)
    - Invalid/unknown frontmatter fields (Major)
    - Malformed YAML syntax (Critical)
    - Empty description value (Major)

    Report findings using severity: Critical / Major / Minor.
    If no issues found, report "PASS".
    </instructions>
```

## V2: Content Quality (claude-code-guide)

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Verify {command-name} command content quality"
- prompt: |
    <task-context>
    <component-type>command</component-type>
    <component-path>{path to command .md file}</component-path>
    <validation-type>content-quality</validation-type>
    </task-context>

    <instructions>
    Read the command file and verify the content body (after frontmatter):

    1. **AI instruction check**:
       - The content must be instructions for AI (Claude), not user documentation
       - It should direct Claude on what to do when the command is invoked
       - If it reads like a README or user guide, report as Major issue

    2. **allowed-tools consistency**:
       - If `allowed-tools` is specified in frontmatter, check that the body
         instructions actually use or reference those tools
       - If instructions reference tools not in allowed-tools, report as Major
       - If allowed-tools lists tools never used in instructions, report as Minor

    3. **$ARGUMENTS utilization**:
       - If `argument-hint` is specified, the body should reference `$ARGUMENTS`
         to use the provided arguments
       - If argument-hint exists but $ARGUMENTS is never referenced, report as Major
       - If $ARGUMENTS is referenced but no argument-hint, report as Minor

    4. **Content substantiality**:
       - Body should have meaningful instructions (>50 words minimum)
       - Extremely short bodies suggest incomplete implementation (Major)

    Report findings using severity: Critical / Major / Minor.
    If no issues found, report "PASS".
    </instructions>
```

## Parallel Launch Example

Launch both Tasks in a single message:

```
[Message with 2 Task tool calls]

Task 1: claude-code-guide frontmatter (V1)
Task 2: claude-code-guide content quality (V2)
```

## Result Integration

Collect results from both Tasks and merge:

1. Aggregate all Critical/Major/Minor findings
2. Apply overall judgment (PASS/WARN/FAIL)
3. If FAIL -> trigger auto-fix loop (see [auto-fix-loop.md](auto-fix-loop.md))
