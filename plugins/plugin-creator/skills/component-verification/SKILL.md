---
name: component-verification
description: "Component verification pipeline for plugin creation/modification. This skill should be used when verifying created components, running parallel validation tasks, handling auto-fix loops, or performing cross-component reference checks. Activation: component verification, validate components, 컴포넌트 검증, 검증 파이프라인, per-component validation"
---

# Component Verification Pipeline

Per-component verification pipeline for plugin creation and modification workflows.
Each component is verified immediately after creation/modification, before proceeding to the next type.

## Pipeline Overview

```
Component Created/Modified
     ↓
Parallel Verification Tasks (type-specific)
     ↓
Result Collection
     ↓
[Critical/Major issues?]
     ├── Yes → Auto-Fix Loop (max 2 rounds)
     │         ├── Creator re-invocation with feedback
     │         ├── Re-run failed verifications only
     │         └── Still failing? → AskUserQuestion
     └── No → PASS/WARN → Next component
     ↓
All components done
     ↓
Cross-Component Validation (Phase 3)
```

## Type-Specific Verification Summary

| Type | Tasks | Agents | Details |
|------|-------|--------|---------|
| Skill | 3 parallel | skill-reviewer + claude-code-guide x2 | [skill-checks.md](references/skill-checks.md) |
| Agent | 2 parallel | claude-code-guide x2 | [agent-checks.md](references/agent-checks.md) |
| Command | 2 parallel | claude-code-guide x2 | [command-checks.md](references/command-checks.md) |
| Hook | 2 parallel | claude-code-guide x2 | [hook-checks.md](references/hook-checks.md) |

### Skill Verification (3 Tasks)

| # | Agent | Focus | Key Checks |
|---|-------|-------|------------|
| V1 | `plugin-creator:skill-reviewer` | Content quality | Description triggers 3-5, progressive disclosure (SKILL.md <500 lines/3000 words), references/ separation, path link validity, imperative style |
| V2 | `claude-code-guide` | Frontmatter spec | required: description. valid optional: name, argument-hint, allowed-tools, model, context, agent, hooks, disable-model-invocation, user-invocable |
| V3 | `claude-code-guide` | References & structure | references/ files exist, SKILL.md path references valid, examples/ structure |

### Agent Verification (2 Tasks)

| # | Focus | Key Checks |
|---|-------|------------|
| V1 | Frontmatter spec | required: name (3-50 chars), description. optional: tools, disallowedTools, model, permissionMode, maxTurns, skills, mcpServers, hooks, memory, background, isolation. Subagent nesting constraint |
| V2 | System prompt quality | XML structure (`<context>`, `<instructions>`), skill path references valid, tools field consistent with instructions tool usage |

### Command Verification (2 Tasks)

| # | Focus | Key Checks |
|---|-------|------------|
| V1 | Frontmatter spec | required: description. optional: name, allowed-tools, argument-hint, model, context, agent, hooks, disable-model-invocation, user-invocable |
| V2 | Content quality | AI instruction (not user documentation), allowed-tools consistent with actual tool usage, $ARGUMENTS utilization |

### Hook Verification (2 Tasks)

| # | Focus | Key Checks |
|---|-------|------------|
| V1 | Event type validity | 17 valid events (PreToolUse, PostToolUse, etc.), matcher pattern |
| V2 | Script security | Command injection vulnerabilities, `${CLAUDE_PLUGIN_ROOT}` path usage, execution permissions |

## Verification Execution Pattern

For each component type (Skills -> Agents -> Commands -> Hooks):

1. **Create components** — Same-type components in parallel via Creator agent Tasks
2. **Verify each component** — Launch type-specific verification Tasks in parallel
3. **Collect results** — Wait for all verification Tasks to complete
4. **Handle issues** — Critical/Major issues trigger auto-fix loop. See [auto-fix-loop.md](references/auto-fix-loop.md)
5. **Proceed** — All PASS/WARN -> move to next type

### Parallel Verification Launch Pattern

```
Task tool (parallel launch for each component):
- subagent_type: {verification agent}
- description: "Verify {component-name}: {check-focus}"
- prompt: {see type-specific references/ for full prompt templates}
```

Launch all verification Tasks for a single component **in one message** to maximize parallelism.

## Auto-Fix Loop

When Critical or Major issues are detected:

1. Re-invoke the Creator agent Task with `<review-feedback>` containing the issues
2. Re-run **only the failed** verification Tasks (not all)
3. Maximum **2 rounds** of auto-fix attempts
4. After 2 rounds, present 3 options via AskUserQuestion:
   - "Review manually and continue" (recommended)
   - "Ignore issues and continue"
   - "Cancel creation"
5. **Minor issues**: Display as warnings, proceed without fix

See [auto-fix-loop.md](references/auto-fix-loop.md) for detailed patterns and prompt templates.

## Cross-Component Validation

After all individual components pass verification, run Phase 3 cross-component checks:

- **Task A**: claude-code-guide cross-reference validation (always)
  - agent -> skill references valid
  - command -> agent references valid
  - hook -> command/script references valid
  - Naming consistency across components
- **Task B**: plugin-validator full structure (Plugin Mode only)
  - Manifest validity
  - Directory structure
  - Pattern compliance

See [cross-component.md](references/cross-component.md) for detailed patterns.

## Result Judgment Criteria

### Severity Classification

| Severity | Description | Action |
|----------|-------------|--------|
| **Critical** | Broken functionality — invalid frontmatter, missing required fields, broken references | Must fix (auto-fix or manual) |
| **Major** | Quality degradation — weak description triggers, missing progressive disclosure, security issues | Should fix (auto-fix attempted) |
| **Minor** | Improvement opportunity — naming style, additional triggers suggested, documentation gaps | Warn and proceed |

### Overall Judgment

| Judgment | Condition | Action |
|----------|-----------|--------|
| **PASS** | 0 Critical, 0 Major | Proceed immediately |
| **WARN** | 0 Critical, 0 Major, Minor > 0 | Display warnings, proceed |
| **FAIL** | Critical > 0 or Major > 0 | Trigger auto-fix loop |

## Reference Files

- **[references/skill-checks.md](references/skill-checks.md)** — Skill verification: 3 parallel Task prompt templates
- **[references/agent-checks.md](references/agent-checks.md)** — Agent verification: 2 parallel Task prompt templates
- **[references/command-checks.md](references/command-checks.md)** — Command verification: 2 parallel Task prompt templates
- **[references/hook-checks.md](references/hook-checks.md)** — Hook verification: 2 parallel Task prompt templates
- **[references/auto-fix-loop.md](references/auto-fix-loop.md)** — Auto-fix loop patterns and escalation
- **[references/cross-component.md](references/cross-component.md)** — Phase 3 cross-component validation
