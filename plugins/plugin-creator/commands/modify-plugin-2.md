---
description: Interactive plugin/component modification with conversational design, automated implementation, and per-component verification pipeline
argument-hint: [plugin-name, plugin-path, or "project"]
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion, Skill, Task, TaskCreate, TaskUpdate, TaskList
---

# Interactive Plugin/Component Modification (v2 — Per-Component Verification)

Interactively analyze and modify existing plugins or project components.
Each modified/added component is verified immediately. Deletions include pre/post safety checks.

**Supported Modes:**
- **Project Mode**: Modify components in the current project's `.claude/` folder
- **Plugin Mode**: Modify existing plugins

**Core Philosophy:**
- Iteratively collect and refine requirements like a Plan agent
- Only ask about direction; AI decides the details
- Recommend Skill -> Agent -> Command structure and suggest refactoring
- **Per-component verification** — every modified/added component is validated immediately
- **Deletion safety** — pre-deletion reference check + post-deletion dangling scan
- **Regression verification** — post-modification compatibility check
- **Skill-based verification logic** — orchestration here, details in skills

**Target:** $ARGUMENTS

---

## Phase 0: Initialization

### Step 1: Load Skills

```
Skill tool: "plugin-creator:plugin-development"
Skill tool: "plugin-creator:component-verification"
Skill tool: "plugin-creator:modify-safety"
```

### Step 2: Mode Detection

**MUST EXECUTE: Analyze arguments to determine mode.**

1. Argument is "project" or ".claude" -> Project Mode
2. Argument is a path with `.claude-plugin/plugin.json` -> Plugin Mode
3. Argument is a name, search finds `.claude-plugin/` -> Plugin Mode
4. Current project has `.claude/`, no argument -> Suggest Project Mode
5. None -> AskUserQuestion: Project components / Plugin

| Item | Project Mode | Plugin Mode |
|------|-------------|-------------|
| Target path | `./.claude/` | `plugins/{name}/` or specified |
| Manifest | None | `.claude-plugin/plugin.json` |
| Version mgmt | None | Update plugin.json version |

**Namespaced Commands:** `.claude/commands/{ns}/{name}.md` -> `/{ns}:{name}`

### Step 3: Clean Up Tasks

```
TaskList -> check existing; TaskUpdate -> delete (status: "deleted")
```

### Step 4: Register Tasks

```
TaskCreate (4 times):
1. "Phase 1: Plan Design" / "Designing modification plan"
2. "Phase 2: Modification + Verification" / "Modifying and verifying"
3. "Phase 3: Cross-Component + Regression" / "Validating"
4. "Phase 4: Completion" / "Finalizing"
```

Set dependencies: Phase 2 -> 1, Phase 3 -> 2, Phase 4 -> 3.

---

## Phase 1: Plan Design

### Step 1: Confirm Target Location

**Project Mode:** Path `./.claude/`, check with `ls -la .claude/`

**Plugin Mode:** Find from $ARGUMENTS:
1. Path given -> use directly
2. Name given -> search `./plugins/{name}/`, `./.claude-plugin/`, `~/.claude/plugins/{name}/`

### Step 1.5: Pre-Analysis

**MUST EXECUTE: Analyze existing structure before plan design.**
Follow `modify-safety` skill, `references/pre-analysis.md`.

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Pre-analysis: existing structure"
- prompt: |
    <task-context>
    <mode>{project or plugin}</mode>
    <path>{target path}</path>
    <user-request>$ARGUMENTS</user-request>
    <validation-type>pre-analysis</validation-type>
    </task-context>

    <instructions>
    Analyze existing structure:
    1. Component inventory (skills, agents, commands, hooks)
    2. Architecture pattern assessment (Skill -> Agent -> Command)
    3. Inter-component reference map
    4. Improvement opportunities
    5. Risk assessment for requested modification
    Format as structured report for plan-designer context.
    </instructions>
```

Store result for Step 2.

### Step 1.5b: Ensure Plans Directory

```
Bash: mkdir -p ~/.claude/plans/
```

### Step 2: Call plan-designer

```
Task tool:
- subagent_type: "plugin-creator:plan-designer"
- description: "Interactive modification plan design"
- prompt: |
    <current-state>
    <mode>{project or plugin}</mode>
    <path>{target path}</path>
    <user-request>$ARGUMENTS</user-request>
    <type>modify</type>
    </current-state>

    <current-analysis>
    {Pre-analysis result from Step 1.5}
    </current-analysis>

    <instructions>
    Design modification plan interactively:
    0. **Analysis Phase**: Analyze current structure
    1. **Discovery Phase**: Ask 2-3 questions about modification direction
    2. **Design Phase**: Design modification plan, suggest refactoring if needed
    3. **Review Phase**: Show plan, allow modifications
    4. **Finalize Phase**: Write to `~/.claude/plans/{mode}-modify-{name}-{timestamp}.md`

    **Path rules:**
    - Project: `.claude/skills/`, `.claude/agents/`, `.claude/commands/`, `.claude/hooks.json`
    - Plugin: `{plugin}/skills/`, `{plugin}/agents/`, `{plugin}/commands/`, `{plugin}/hooks/hooks.json`

    **Refactoring conditions:**
    - Skills but no agents -> suggest agents
    - Commands with all logic -> suggest agent separation
    - Agents without skills -> suggest skill extraction

    **CRITICAL**: Continue until user approves. Save plan file and return path.
    </instructions>
```

Extract plan file path. Update "Phase 1" task to `completed`.

---

## Phase 1.5: Plan Review and Approval

### Step 1: Validate via claude-code-guide

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Modification plan spec validation"
- prompt: |
    <task-context>
    <plan-file>{plan file path}</plan-file>
    <validation-type>specification</validation-type>
    </task-context>

    <instructions>
    Verify plan conforms to Claude Code specs:
    - Skill frontmatter (required: description; optional: name, argument-hint, allowed-tools, model, context, agent, hooks, disable-model-invocation, user-invocable)
    - Agent frontmatter (required: name, description; optional: tools, disallowedTools, model, permissionMode, maxTurns, skills, mcpServers, hooks, memory, background, isolation)
    - Subagent nesting constraint
    - Command frontmatter (required: description; optional: name, allowed-tools, argument-hint, model, context, agent, hooks, disable-model-invocation, user-invocable)
    - Hook events (17 valid types)
    </instructions>
```

### Step 2: Handle Results

Issues found -> AskUserQuestion: Fix/Ignore/Cancel.

### Step 3: Display Plan + Request Approval

Read plan, display, then AskUserQuestion: Approve / Needs changes / Cancel.

| Selection | Action |
|-----------|--------|
| **Approve** | Phase 2 |
| **Needs changes** | Re-invoke plan-designer |
| **Cancel** | Exit |

---

## Phase 2: Component Modification + Per-Component Verification

### Step 1: Extract Delegation from Plan File

Parse `## Delegation Instructions` section.

### Step 2: Execute Tasks

**Task order:** Delete -> Modify -> Add

#### Delete (if needed)

Follow `modify-safety` skill, `references/deletion-safety.md`:

1. **Pre-deletion check**: claude-code-guide Task scans for references
   - References found -> AskUserQuestion: delete+update / cancel
2. **Execute deletion**: `rm -rf {path}`
3. **Post-deletion scan**: claude-code-guide Task checks for dangling references
   - Dangling found -> fix with Edit, re-scan once

#### Modify

- Partial: Edit tool directly
- Full rewrite: Creator agent Task

**After modification, verify** per loaded `component-verification` skill:
- Skill: `references/skill-checks.md` — 3 parallel Tasks
- Agent: `references/agent-checks.md` — 2 parallel Tasks
- Command: `references/command-checks.md` — 2 parallel Tasks
- Hook: `references/hook-checks.md` — 2 parallel Tasks

Critical/Major -> `references/auto-fix-loop.md` (max 2 rounds).

#### Add

Creator agent Task -> type-specific verification (same as Modify above).

### Step 3: Update Plan File Status

```
Edit: "**Status**: PENDING_APPROVAL" -> "**Status**: COMPLETED"
```

Update "Phase 2" task to `completed`.

---

## Phase 3: Cross-Component Validation + Regression

**Launch 2-3 parallel Tasks:**

- **Task A**: claude-code-guide cross-reference validation (always)
  Follow `component-verification` skill, `references/cross-component.md`
- **Task B**: plugin-validator full structure (Plugin Mode only)
  Follow `component-verification` skill, `references/cross-component.md`
- **Task C**: claude-code-guide regression verification (always)
  Follow `modify-safety` skill, `references/regression-check.md`

### Handle Results

| Result | Action |
|--------|--------|
| PASS | Version Update (Plugin Mode) or Phase 4 |
| WARN | Display warnings, proceed |
| FAIL | Auto-fix (max 3 rounds), then escalate |

### Version Update (Plugin Mode only)

| Modification Type | Version Bump |
|-------------------|-------------|
| Metadata only | patch (1.0.0 -> 1.0.1) |
| Component addition | minor (1.0.0 -> 1.1.0) |
| Component deletion | minor (1.0.0 -> 1.1.0) |
| Breaking Change | major (1.0.0 -> 2.0.0) |

AskUserQuestion: Use recommended / Specify different / Keep current.

Update "Phase 3" task to `completed`.

---

## Phase 4: Completion

### Step 1: Completion Summary

Display summary including:
- Changes (added, modified, deleted components)
- Verification summary (verified count, auto-fix rounds, issues, regression result)
- Architecture changes (before/after)
- Testing instructions
- Next steps

### Step 2: Check for Additional Work

```
AskUserQuestion: "Anything else to modify?"
- Done -> exit
- Additional modifications -> Phase 1 (max 3 rounds)
- Update README -> update then exit
```

Update "Phase 4" task to `completed`.

---

## Quick Reference

### Path Rules

| Component | Project Mode | Plugin Mode |
|-----------|-------------|-------------|
| Skills | `.claude/skills/{name}/SKILL.md` | `{plugin}/skills/{name}/SKILL.md` |
| Agents | `.claude/agents/{name}.md` | `{plugin}/agents/{name}.md` |
| Commands | `.claude/commands/{name}.md` | `{plugin}/commands/{name}.md` |
| Hooks | `.claude/hooks.json` | `{plugin}/hooks/hooks.json` |
| Manifest | None | `{plugin}/.claude-plugin/plugin.json` |

### Verification Pipeline

| Type | Tasks | Agents |
|------|-------|--------|
| Skill | 3 parallel | skill-reviewer + ccg x2 |
| Agent | 2 parallel | ccg x2 |
| Command | 2 parallel | ccg x2 |
| Hook | 2 parallel | ccg x2 |
| Cross-component | 2-3 parallel | ccg + plugin-validator + regression |

### Safety Checks

| Operation | Check | Skill Reference |
|-----------|-------|-----------------|
| Delete | Pre + Post check | modify-safety/deletion-safety.md |
| Modify/Add | Type-specific verification | component-verification/{type}-checks.md |
| All | Cross-component + Regression | cross-component.md + regression-check.md |

### Component Dependencies

| Component | Dependencies |
|-----------|-------------|
| Skills | Referenced by agents, commands |
| Agents | Called from commands via Task |
| Hooks | Depend on script files |
| Commands | May reference agents/skills |

---

## Error Handling

| Error | Action |
|-------|--------|
| Target not found | Suggest create-plugin or different path |
| Invalid structure | Suggest create-plugin or initialize |
| Agent call failure | Retry (max 2), alternative, or cancel |
| Spec validation failure | Pass to plan-designer |
| Verification persistent failure | AskUserQuestion: review/ignore/cancel |

---

**Begin with Phase 0: Initialization**
