---
description: Interactive plugin/component creation with conversational design, automated implementation, and per-component verification pipeline
argument-hint: [description]
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion, Skill, Task, TaskCreate, TaskUpdate, TaskList
---

# Interactive Plugin/Component Creation (v2 — Per-Component Verification)

Interactively design and automatically create plugins or project components.
Each component is verified immediately after creation via parallel validation Tasks.

**Supported Modes:**
- **Project Mode**: Add commands/agents/skills to the current project's `.claude/` folder
- **Plugin Mode**: Create independent plugins deployable to the marketplace

**Core Philosophy:**
- Iteratively collect and refine requirements like a Plan agent
- Only ask about direction; AI decides the details
- Recommend Skill -> Agent -> Command structure
- **Per-component verification** — every component is validated immediately after creation
- **Skill-based verification logic** — orchestration here, details in `component-verification` skill

**Initial request:** $ARGUMENTS

---

## Phase 0: Initialization

### Step 1: Load Skills

```
Skill tool: "plugin-creator:plugin-development"
Skill tool: "plugin-creator:component-verification"
```

### Step 2: Mode Selection

**MUST EXECUTE: Determine the creation mode first.**

```
AskUserQuestion:
- question: "What would you like to create?"
- header: "Type"
- options:
  - label: "Project components (Recommended)"
    description: "Add commands/agents/skills to the current project's .claude/ folder"
  - label: "Plugin"
    description: "Independent plugin deployable to the marketplace"
```

| Item | Project Mode | Plugin Mode |
|------|-------------|-------------|
| Location | `./.claude/` | `plugins/{name}/` or specified path |
| Manifest | None | `.claude-plugin/plugin.json` |
| Skills path | `.claude/skills/{name}/SKILL.md` | `{plugin}/skills/{name}/SKILL.md` |
| Agents path | `.claude/agents/{name}.md` | `{plugin}/agents/{name}.md` |
| Commands path | `.claude/commands/{name}.md` or `.claude/commands/{ns}/{name}.md` | `{plugin}/commands/{name}.md` |
| Hooks path | `.claude/hooks.json` | `{plugin}/hooks/hooks.json` |

**Project Mode Namespaced Commands:**
`.claude/commands/{namespace}/{name}.md` -> `/{namespace}:{name}` invocation

### Step 3: Clean Up Tasks

```
TaskList tool -> check existing tasks
TaskUpdate tool -> delete existing tasks (status: "deleted")
```

### Step 4: Register Tasks

```
TaskCreate (4 times):
1. "Phase 1: Plan Design" / "Designing plan"
2. "Phase 2: Component Creation + Verification" / "Creating and verifying"
3. "Phase 3: Cross-Component Validation" / "Validating cross-references"
4. "Phase 4: Completion" / "Finalizing"
```

Set task dependencies: Phase 2 -> Phase 1, Phase 3 -> Phase 2, Phase 4 -> Phase 3.

---

## Phase 1: Plan Design

**MUST EXECUTE: Delegate interactive plan design to the plan-designer agent.**

### Step 1: Confirm Creation Location

- **Project Mode:** Automatically use `./.claude/`
- **Plugin Mode:** AskUserQuestion for location (plugins/, current dir, custom)

### Step 1.5: Ensure Plans Directory

```
Bash: mkdir -p ~/.claude/plans/
```

### Step 2: Call plan-designer

```
Task tool:
- subagent_type: "plugin-creator:plan-designer"
- description: "Interactive plan design"
- prompt: |
    <task-context>
    <request>$ARGUMENTS</request>
    <mode>{project or plugin}</mode>
    <location>{selected path}</location>
    <type>create</type>
    </task-context>

    <instructions>
    Design the plan interactively like a Plan agent:
    1. **Discovery Phase**: Ask relevant questions via AskUserQuestion
    2. **Design Phase**: Design optimal structure (Skill -> Agent -> Command)
    3. **Review Phase**: Show design, allow modifications
    4. **Finalize Phase**: Write plan to `~/.claude/plans/{mode}-create-{name}-{timestamp}.md`

    **Mode-specific path rules:**
    - Project Mode: `.claude/skills/`, `.claude/agents/`, `.claude/commands/`, `.claude/hooks.json`
    - Project Mode (namespaced): `.claude/commands/{ns}/{name}.md` -> `/{ns}:{name}`
    - Plugin Mode: `{plugin}/skills/`, `{plugin}/agents/`, `{plugin}/commands/`, `{plugin}/hooks/hooks.json`

    **CRITICAL**: Continue until user explicitly approves.
    **CRITICAL**: Save plan file using Write tool and return the path.
    </instructions>
```

Extract plan file path from result. Update "Phase 1" task to `completed`.

---

## Phase 1.5: Plan Review and Approval

### Step 1: Validate via claude-code-guide

```
Task tool:
- subagent_type: "claude-code-guide"
- description: "Plan specification validation"
- prompt: |
    <task-context>
    <plan-file>{plan file path}</plan-file>
    <validation-type>specification</validation-type>
    </task-context>

    <instructions>
    Verify plan conforms to Claude Code specs:
    - Skill frontmatter (required: description; optional: name, argument-hint, allowed-tools, model, context, agent, hooks, disable-model-invocation, user-invocable)
    - Agent frontmatter (required: name, description; optional: tools, disallowedTools, model, permissionMode, maxTurns, skills, mcpServers, hooks, memory, background, isolation)
    - Subagent nesting constraint (subagents cannot spawn other subagents)
    - Command frontmatter (required: description; optional: name, allowed-tools, argument-hint, model, context, agent, hooks, disable-model-invocation, user-invocable)
    - Hook events (17 valid: PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, UserPromptSubmit, Stop, SubagentStop, SubagentStart, SessionStart, SessionEnd, PreCompact, Notification, TeammateIdle, TaskCompleted, ConfigChange, WorktreeCreate, WorktreeRemove)
    </instructions>
```

### Step 2: Handle Results

Issues found -> AskUserQuestion: Fix/Ignore/Cancel.
- Fix -> re-invoke plan-designer
- Cancel -> mark all tasks `completed` and exit

### Step 3: Display Plan + Request Approval

Read plan file, display to user, then:

```
AskUserQuestion: "Approve plan?" -> Approve / Needs changes / Cancel
```

| Selection | Action |
|-----------|--------|
| **Approve** | Proceed to Phase 2 |
| **Needs changes** | Re-invoke plan-designer |
| **Cancel** | Exit |

---

## Phase 2: Component Creation + Per-Component Verification

### Step 1: Extract Delegation from Plan File

Parse `## Delegation Instructions` section.

### Step 2: Create Base Structure

- **Project Mode:** `mkdir -p .claude/skills .claude/agents .claude/commands .claude/scripts`
- **Plugin Mode:** Create dirs (including scripts/) + Write `plugin.json`

### Step 3: Create & Verify Components

**Per-component verification pipeline.**
Follow loaded `component-verification` skill guidelines.

**Type-by-type sequential execution (Skills -> Scripts -> Agents -> Commands -> Hooks):**

For each type:
1. **Create** same-type components in parallel via Creator agent Task calls
   - `plugin-creator:skill-creator`, `plugin-creator:agent-creator`, etc.
   - Prompt includes `<task-context>`, `<specification>`, `<instructions>`
2. **Verify** each component — launch type-specific parallel verification Tasks
   - Skill: `references/skill-checks.md` — 3 parallel Tasks
   - Script: `references/script-checks.md` — 2 parallel Tasks
   - Agent: `references/agent-checks.md` — 2 parallel Tasks
   - Command: `references/command-checks.md` — 2 parallel Tasks
   - Hook: `references/hook-checks.md` — 2 parallel Tasks
3. **Collect results** — apply judgment (PASS/WARN/FAIL)
4. **Handle issues** — Critical/Major -> `references/auto-fix-loop.md` (max 2 rounds)
5. **Proceed** — all PASS/WARN -> next type

### Step 4: Update Plan File Status

```
Edit: "**Status**: PENDING_APPROVAL" -> "**Status**: COMPLETED"
```

Update "Phase 2" task to `completed`.

---

## Phase 3: Cross-Component Validation

Follow `component-verification` skill, `references/cross-component.md`.

**Launch parallel Tasks:**
- **Task A**: claude-code-guide cross-reference validation (always)
- **Task B**: plugin-validator full structure (Plugin Mode only)

| Result | Action |
|--------|--------|
| PASS | Phase 4 |
| WARN | Display warnings, Phase 4 |
| FAIL | Auto-fix (max 3 rounds), then escalate |

Update "Phase 3" task to `completed`.

---

## Phase 4: Completion

### Step 1: Marketplace Registration (Plugin Mode only)

AskUserQuestion: Register in marketplace? Yes/Later.

### Step 2: Completion Summary

Display summary including:
- Created components list (skills, agents, commands, hooks)
- Verification summary (components verified, auto-fix rounds, issues found)
- Architecture pattern used
- Testing instructions (`claude` or `claude --plugin-dir {path}`)
- Next steps

Update "Phase 4" task to `completed`.

---

## Error Handling

| Error | Action |
|-------|--------|
| Unclear request | plan-designer clarifies with questions |
| Agent call failure | Retry (max 2), discuss alternative, or cancel |
| Specification validation failure | Pass to plan-designer for correction |
| Verification persistent failure | AskUserQuestion: manual review / ignore / cancel |

---

**Begin with Phase 0: Initialization**
