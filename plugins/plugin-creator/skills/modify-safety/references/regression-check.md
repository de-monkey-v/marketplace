# Regression Check: Post-Modification Verification

## Overview

After all modifications are complete, verify that changes haven't broken existing functionality or degraded quality. This runs as Task C in Phase 3, parallel with cross-component validation (Task A) and plugin-validator (Task B).

## Task C: Regression Verification

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Regression verification"
- prompt: |
    <task-context>
    <mode>{project or plugin}</mode>
    <path>{.claude/ or plugin-path}</path>
    <modified-components>
      {list of modified component names, types, and what was changed}
    </modified-components>
    <deleted-components>
      {list of deleted component names, types (if any)}
    </deleted-components>
    <added-components>
      {list of added component names, types (if any)}
    </added-components>
    <validation-type>regression</validation-type>
    </task-context>

    <instructions>
    Verify that the modifications haven't introduced regressions:

    1. **Interface compatibility**:
       - For each modified component, check that frontmatter changes are
         backward-compatible
       - If a skill's `name` changed, all agent `skills` references must be updated
       - If an agent's `name` changed, all command references must be updated
       - If a command's name or path changed, user invocation path must be updated
       - Report broken interfaces as Critical

    2. **Description trigger effectiveness**:
       - For modified skills: Does the description still contain effective trigger phrases?
       - For modified agents: Does the description still accurately describe the agent?
       - Compare the spirit of the original description with the new one
       - Report significantly degraded triggers as Major

    3. **Functional consistency**:
       - For modified components: Do they still perform their original intended function?
       - Has the modification inadvertently removed important functionality?
       - Has the scope changed in a way that might surprise users?
       - Report functional regressions as Critical

    4. **Reference integrity post-modification**:
       - After all changes, do all inter-component references still resolve?
       - Skill paths in agents, agent references in commands, hook scripts
       - This overlaps with cross-component validation (Task A) but focuses
         specifically on changes introduced by this modification session
       - Report broken references as Critical

    5. **Added component integration**:
       - Do newly added components follow the same patterns as existing ones?
       - Are they properly integrated into the reference graph?
       - Do they follow naming conventions consistent with existing components?
       - Report integration issues as Major

    **Output format:**

    ```
    REGRESSION CHECK RESULTS:

    Modified components checked: {count}
    Deleted components verified: {count}
    Added components verified: {count}

    Critical: {count}
    - {issue description with file path}

    Major: {count}
    - {issue description with file path}

    Minor: {count}
    - {issue description}

    Overall: {PASS/WARN/FAIL}
    ```

    Report findings using severity: Critical / Major / Minor.
    If no issues found, report "PASS".
    </instructions>
```

## Integration with Phase 3

Phase 3 runs three parallel Tasks:

```
[Single message with parallel Task tool calls]

Task A: claude-code-guide cross-reference validation (from component-verification skill)
Task B: plugin-validator full structure (Plugin Mode only, from component-verification skill)
Task C: claude-code-guide regression verification (this template)
```

## Result Integration

Task C results are merged with Task A and Task B results:

1. Aggregate all Critical/Major/Minor findings from all 3 Tasks
2. Deduplicate overlapping findings (regression + cross-reference may find same issues)
3. Apply overall judgment (PASS/WARN/FAIL)
4. If FAIL -> auto-fix loop (max 3 total rounds for Phase 3)

## Version Update Trigger

For Plugin Mode, regression check results inform version bump recommendation:

| Regression Finding | Version Bump |
|-------------------|-------------|
| No regressions, minor additions only | patch |
| New components added, no breaking changes | minor |
| Interface changes, renamed components | major (Breaking Change) |
