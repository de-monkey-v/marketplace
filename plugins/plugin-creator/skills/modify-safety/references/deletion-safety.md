# Deletion Safety: Pre/Post Deletion Checks

## Overview

Two-phase safety check around component deletion:

```
Phase 1: Pre-Deletion Reference Check
     ↓
[References found?]
     ├── Yes → Report to user → Confirm or cancel
     └── No → Proceed
     ↓
Delete Component
     ↓
Phase 2: Post-Deletion Dangling Scan
     ↓
[Dangling references?]
     ├── Yes → Report and fix
     └── No → Continue
```

## Phase 1: Pre-Deletion Reference Check

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Pre-deletion reference check: {component-name}"
- prompt: |
    <task-context>
    <mode>{project or plugin}</mode>
    <path>{.claude/ or plugin-path}</path>
    <deletion-target>
      <type>{skill/agent/command/hook}</type>
      <name>{component-name}</name>
      <file-path>{path to component file(s)}</file-path>
    </deletion-target>
    <validation-type>pre-deletion-reference-check</validation-type>
    </task-context>

    <instructions>
    Before deleting the specified component, scan all other components for references to it.

    **Check these reference patterns based on deletion target type:**

    If deleting a **Skill**:
    - Agent frontmatter `skills` field → lists this skill name?
    - Agent/command body content → mentions this skill path?
    - Other skill references/ files → links to this skill?

    If deleting an **Agent**:
    - Command frontmatter `agent` field → references this agent?
    - Command body content → Task tool calls with this agent as subagent_type?
    - Other agent files → references to this agent?

    If deleting a **Command**:
    - Hook configurations → references this command?
    - Other command files → references to this command?
    - README or documentation → mentions this command?

    If deleting a **Hook** or hook script:
    - hooks.json → references the script being deleted?
    - Other hooks → chain references?

    **Output format:**

    If references found:
    ```
    REFERENCES FOUND for {component-name}:

    1. {referencing-file-path}
       - Line/field: {specific location}
       - Reference: {exact reference text}
       - Impact: {what breaks if deleted}

    2. ...

    Recommendation: Update these references before or after deletion.
    ```

    If no references found:
    ```
    NO REFERENCES FOUND for {component-name}.
    Safe to delete.
    ```
    </instructions>
```

### Handling Pre-Deletion Results

If references are found, ask the user:

```
AskUserQuestion:
- question: "The following components reference {component-name}:
  {list of referencing components}

  Deleting it will break these references. How would you like to proceed?"
- header: "Deletion Reference Check"
- options:
  - label: "Delete and update references (Recommended)"
    description: "Delete the component and update all referencing components"
  - label: "Cancel deletion"
    description: "Keep the component, skip this deletion task"
```

## Phase 2: Post-Deletion Dangling Scan

After the deletion is executed, scan for any remaining broken references:

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Post-deletion dangling reference scan"
- prompt: |
    <task-context>
    <mode>{project or plugin}</mode>
    <path>{.claude/ or plugin-path}</path>
    <deleted-components>
      {list of deleted component names, types, and former paths}
    </deleted-components>
    <validation-type>post-deletion-dangling-scan</validation-type>
    </task-context>

    <instructions>
    Scan all remaining components for dangling references to deleted components.

    **Check for:**

    1. **Broken skill paths**: Agent `skills` fields referencing non-existent skills
    2. **Missing agent references**: Command `agent` fields or Task invocations
       referencing non-existent agents
    3. **Orphaned hook scripts**: hooks.json referencing non-existent script files
    4. **Invalid cross-references**: Any remaining file containing paths or names
       that no longer resolve

    **Search method:**
    - Grep for deleted component names across all remaining .md and .json files
    - Check frontmatter fields specifically for structured references
    - Check body content for path-based references

    **Output format:**

    If dangling references found:
    ```
    DANGLING REFERENCES FOUND:

    1. {file-path}
       - Reference to: {deleted-component-name}
       - Location: {line/field}
       - Fix: {remove reference / update to new target}

    2. ...
    ```

    If no dangling references:
    ```
    NO DANGLING REFERENCES FOUND.
    All references are clean after deletion.
    ```
    </instructions>
```

### Handling Post-Deletion Results

If dangling references are found:
1. Report the dangling references to the user
2. Use Edit tool to remove or update the broken references
3. Re-run the dangling scan to confirm all clean (max 1 re-check)
