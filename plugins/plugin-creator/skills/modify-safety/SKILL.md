---
name: modify-safety
description: "Safety checks for plugin/component modification. This skill should be used when modifying existing plugins, deleting components, checking for regressions, or analyzing existing plugin structure before changes. Activation: modification safety, 수정 안전성, 삭제 체크, regression check, pre-analysis, deletion safety"
---

# Modification Safety Checks

Safety verification patterns for plugin/component modification workflows.
Ensures structural integrity is maintained when modifying, deleting, or adding components to existing plugins.

## Overview

Modification operations carry risks that creation does not:

| Operation | Risk | Safety Check |
|-----------|------|-------------|
| **Delete** | Dangling references from other components | Pre-deletion reference check + post-deletion dangling scan |
| **Modify** | Breaking existing interfaces or triggers | Regression verification |
| **Add** | Inconsistency with existing structure | Standard component verification (via `component-verification` skill) |

## Pre-Analysis

Before designing a modification plan, analyze the existing plugin structure to provide context for informed decision-making.

**When to run**: Always before plan-designer invocation in modify workflows.

**Purpose**:
- Understand current component landscape
- Identify Skill -> Agent -> Command pattern compliance
- Map inter-component references
- Surface improvement/refactoring opportunities

**Execution**: claude-code-guide foreground Task.
Result is passed to plan-designer prompt as `<current-analysis>` context.

See [references/pre-analysis.md](references/pre-analysis.md) for full Task prompt template.

## Deletion Safety

Deletion is the highest-risk modification operation. Two-phase safety check:

### Phase 1: Pre-Deletion Reference Check

Before deleting any component, scan all other components for references to the deletion target.

**References to check by component type:**

| Deleted Type | Check For References In |
|-------------|------------------------|
| Skill | Agent `skills` fields, command/agent body mentions, other skill references/ links |
| Agent | Command `agent` fields, command body Task invocations, other agent references |
| Command | Hook configurations, other command references |
| Hook script | hooks.json references |

If references are found:
- Report the referencing components to the user
- Ask whether to proceed (update references) or cancel deletion

### Phase 2: Post-Deletion Dangling Scan

After deletion, scan for any broken references that were missed:

- Broken skill paths in agent configurations
- Missing agent references in commands
- Orphaned hook script paths
- Invalid cross-references in remaining components

See [references/deletion-safety.md](references/deletion-safety.md) for full Task prompt templates.

## Regression Check

After all modifications are complete (Phase 3), verify that changes haven't broken existing functionality:

**Regression verification covers:**

1. **Interface compatibility** — Modified frontmatter fields are still valid and backward-compatible
2. **Trigger effectiveness** — Modified descriptions still contain effective trigger phrases
3. **Functional consistency** — Modified components still perform their intended function
4. **Reference integrity** — All inter-component references remain valid after modifications

**Execution**: Runs as Task C in Phase 3, parallel with cross-component validation (Task A) and plugin-validator (Task B).

See [references/regression-check.md](references/regression-check.md) for full Task prompt template.

## Workflow Integration

### In modify-plugin-2 command:

```
Phase 1, Step 1.5: Pre-Analysis
  └── references/pre-analysis.md → claude-code-guide Task
       → Result into plan-designer <current-analysis>

Phase 2, Step 2: Execute Tasks
  ├── [Delete] references/deletion-safety.md
  │   └── Pre-check → Delete → Post-check
  ├── [Modify] Component verification (component-verification skill)
  └── [Add] Component verification (component-verification skill)

Phase 3: Cross-Component + Regression
  ├── Task A: cross-reference (component-verification skill)
  ├── Task B: plugin-validator (Plugin Mode)
  └── Task C: references/regression-check.md → regression verification
```

## Reference Files

- **[references/pre-analysis.md](references/pre-analysis.md)** — Pre-Analysis: existing structure analysis Task prompt
- **[references/deletion-safety.md](references/deletion-safety.md)** — Deletion safety: pre/post deletion check Task prompts
- **[references/regression-check.md](references/regression-check.md)** — Regression: post-modification verification Task prompt
