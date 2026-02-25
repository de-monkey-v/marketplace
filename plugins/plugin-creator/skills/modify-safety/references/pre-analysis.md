# Pre-Analysis: Existing Structure Analysis

## Overview

Before invoking plan-designer for a modification workflow, analyze the existing plugin/project structure to provide informed context.

**Execution**: claude-code-guide foreground Task (not background — result needed before plan-designer).

## Task Prompt Template

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Pre-analysis: existing structure"
- prompt: |
    <task-context>
    <mode>{project or plugin}</mode>
    <path>{.claude/ or plugin-path}</path>
    <user-request>{user's modification request}</user-request>
    <validation-type>pre-analysis</validation-type>
    </task-context>

    <instructions>
    Analyze the existing plugin/project structure to inform modification planning.

    1. **Component inventory**:
       - List all skills (find skills/*/SKILL.md)
       - List all agents (find agents/*.md)
       - List all commands (find commands/*.md and commands/**/*.md)
       - List all hooks (check hooks.json or hooks/hooks.json)
       - For each component, note: name, description (from frontmatter), file path

    2. **Architecture pattern assessment**:
       - Is Skill → Agent → Command pattern followed?
       - Which skills are referenced by which agents?
       - Which agents are invoked by which commands?
       - Are there components that don't fit the pattern?

    3. **Inter-component reference map**:
       - Agent skills: [...] fields → which skills
       - Command agent: ... fields → which agents
       - Hook references → which scripts
       - Any circular or unexpected references?

    4. **Improvement opportunities** (relevant to user's request):
       - Components that could benefit from refactoring
       - Missing pattern compliance that should be addressed
       - Opportunities to consolidate or split components

    5. **Risk assessment** (for the requested modification):
       - Components likely affected by the change
       - Potential breaking changes
       - Dependencies that need updating

    Format the output as a structured report suitable for inclusion
    in a plan-designer prompt context.
    </instructions>
```

## Passing Result to plan-designer

Include the analysis result in the plan-designer Task prompt:

```
Task tool:
- subagent_type: "plugin-creator:plan-designer"
- prompt: |
    <current-state>
    <mode>{project or plugin}</mode>
    <path>{path}</path>
    <user-request>$ARGUMENTS</user-request>
    <type>modify</type>
    </current-state>

    <current-analysis>
    {Pre-analysis result from claude-code-guide Task above}
    </current-analysis>

    <instructions>
    Design the modification plan interactively...
    (The current-analysis provides context about the existing structure.
    Use this to inform your analysis and design phases.)
    </instructions>
```

## When Pre-Analysis is Skipped

If the modification target has very few components (0-2 total), pre-analysis may be skipped to save time. In this case, omit the `<current-analysis>` section from the plan-designer prompt entirely.
