# Cross-Component Validation (Phase 3)

## Overview

After all individual components pass per-component verification, run cross-component validation to check inter-component references and overall structure integrity.

```
All individual components PASS/WARN
     ↓
Phase 3: Cross-Component Validation
     ├── Task A: claude-code-guide cross-reference check (always)
     ├── Task B: plugin-validator full structure (Plugin Mode only)
     └── [parallel execution]
     ↓
Result Integration
     ├── PASS → Phase 4
     ├── WARN → Display warnings → Phase 4
     └── FAIL → Auto-fix (max 3 rounds total)
```

## Task A: Cross-Reference Validation (always)

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Cross-component reference validation"
- prompt: |
    <task-context>
    <mode>{project or plugin}</mode>
    <path>{.claude/ or plugin-path}</path>
    <validation-type>cross-reference</validation-type>
    </task-context>

    <instructions>
    Validate cross-component references and consistency across all components:

    1. **Agent → Skill references**:
       - If agents have `skills` field, verify each referenced skill exists
       - Check skill paths resolve to actual SKILL.md files
       - Report missing skills as Critical

    2. **Command → Agent references**:
       - If commands reference agents (via `agent` field or Task tool in body),
         verify each referenced agent exists
       - Check agent file paths resolve correctly
       - Report missing agents as Critical

    3. **Hook → Script references**:
       - If hooks reference external scripts, verify scripts exist
       - Check ${CLAUDE_PLUGIN_ROOT} paths resolve correctly
       - Report missing scripts as Critical

    3b. **Script references from agents/commands**:
        - If agents or commands reference scripts (via Bash tool in body text),
          verify referenced script files exist at specified paths
        - Check ${CLAUDE_PLUGIN_ROOT}/scripts/ paths resolve correctly
        - Report missing scripts as Critical

    4. **Naming consistency**:
       - All component names should use consistent kebab-case
       - Skill directory names should match skill frontmatter names
       - Agent filenames should match agent frontmatter names
       - Report inconsistencies as Major

    5. **Skill → Agent → Command pattern**:
       - Check if the recommended pattern is followed
       - Skills provide knowledge, agents use skills, commands invoke agents
       - Report pattern violations as Minor (recommendation, not requirement)

    6. **Orphaned components**:
       - Skills not referenced by any agent or command
       - Scripts not referenced by any agent, command, or hook
       - Agents not invoked by any command
       - Report as Minor (informational)

    Report findings using severity: Critical / Major / Minor.
    If no issues found, report "PASS".
    </instructions>
```

## Task B: Full Structure Validation (Plugin Mode only)

**Skip this Task in Project Mode.**

```
Task tool:
- subagent_type: "plugin-creator:plugin-validator"
- description: "Plugin structure validation"
- prompt: |
    <task-context>
    <plugin-path>{plugin-path}</plugin-path>
    <validation-scope>full</validation-scope>
    </task-context>

    <instructions>
    Perform full plugin structure validation:

    1. **Manifest validity** (plugin.json)
       - Valid JSON syntax
       - Required field: name
       - Semantic versioning if version present
       - No unknown critical fields

    2. **Directory structure**
       - Standard locations: commands/, agents/, skills/, hooks/
       - No unexpected top-level files/directories

    3. **Component format compliance**
       - Each component follows its type-specific format
       - Frontmatter present and valid for all .md files

    4. **Naming conventions**
       - kebab-case throughout
       - Consistent naming between manifest and directory structure

    5. **Skill → Agent → Command pattern compliance**
       - Architecture pattern assessment
       - Recommendations for improvement

    Provide detailed report with fix suggestions for each issue.
    Report overall assessment: PASS / WARN / FAIL.
    </instructions>
```

## Parallel Launch

Launch Task A and Task B (if Plugin Mode) in a single message:

```
[Single message with parallel Task tool calls]

Task A: claude-code-guide cross-reference (always)
Task B: plugin-validator full structure (Plugin Mode only)
```

## Result Integration

1. Collect results from Task A (and Task B if Plugin Mode)
2. Merge findings by severity
3. Apply overall judgment:

| Judgment | Condition | Action |
|----------|-----------|--------|
| **PASS** | 0 Critical, 0 Major | Proceed to Phase 4 |
| **WARN** | 0 Critical, 0 Major, Minor > 0 | Display warnings, proceed to Phase 4 |
| **FAIL** | Critical > 0 or Major > 0 | Trigger cross-component auto-fix |

## Cross-Component Auto-Fix

When cross-component validation FAILs:

1. Identify the specific components causing the issue
2. Re-invoke the appropriate Creator agent(s) with the cross-component feedback
3. Re-run cross-component validation (Task A + Task B)
4. **Maximum 3 total rounds** of cross-component auto-fix

After 3 rounds, escalate to user via AskUserQuestion:

```
AskUserQuestion:
- question: "Cross-component validation found persistent issues after 3 fix attempts.
  Issues remaining:
  {remaining issue summary}

  How would you like to proceed?"
- header: "Cross-Component Validation Issues"
- options:
  - label: "Review manually and continue (Recommended)"
    description: "Examine the issues yourself and decide how to proceed"
  - label: "Ignore issues and continue"
    description: "Accept current state and proceed to completion"
  - label: "Cancel creation"
    description: "Stop the entire creation process"
```
