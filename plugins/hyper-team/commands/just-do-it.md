---
name: just-do-it
description: Analyze the task, create a todo spec, build a team, and execute immediately. One command to go from idea to implementation.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, AskUserQuestion, Task, TeamCreate, TeamDelete, SendMessage, TaskCreate, TaskUpdate, TaskList, TaskGet
---

Create a team. Execute the task described in `$ARGUMENTS` by analyzing the project, creating a todo spec, and dispatching a team to implement it.

**CRITICAL RULE — DO NOT SKIP TEAM CREATION:**
- You are the **team leader**. You MUST NOT implement code directly.
- You MUST always create a team (TeamCreate) and spawn teammates (Task tool) to do the work.
- Even for single-file changes, you MUST spawn at least an **implementer** teammate.
- Your role is to: analyze, plan, create tasks, spawn teammates, coordinate, and verify.
- If you find yourself writing code or editing files (other than the todo spec), STOP — you are violating this rule.

**Arguments:** `$ARGUMENTS`

---

## Phase 1: Validate Input

<instructions>
If `$ARGUMENTS` is empty, ask the user what they want to build:

```
AskUserQuestion:
- question: "What do you want to build or fix?"
- header: "Task"
- options:
  - label: "New feature"
    description: "Build something new from scratch"
  - label: "Bug fix / improvement"
    description: "Fix or improve existing functionality"
  - label: "Refactoring"
    description: "Restructure code without changing behavior"
```

Then ask for a description using AskUserQuestion.

If `$ARGUMENTS` is provided, proceed directly to Phase 2.
</instructions>

---

## Phase 2: Project Analysis

<instructions>
Analyze the current project to understand tech stack, architecture, and relevant code. Perform these steps in parallel:
</instructions>

### Step 1: Discover project structure

```
Glob: **/{package.json,requirements.txt,Cargo.toml,go.mod,pom.xml,build.gradle,Gemfile,pyproject.toml,composer.json}
```

```
Glob: **/{tsconfig.json,next.config.*,vite.config.*,webpack.config.*,nuxt.config.*,.env.example}
```

### Step 2: Read key config files

Read the discovered config files to identify:
- Language and runtime version
- Framework and its version
- Key dependencies
- Build tools and scripts
- Test commands available

### Step 3: Analyze relevant source code

```
Glob: src/**/*.{ts,tsx,js,jsx,py,go,rs,java}
```

Read relevant files that relate to the user's task to understand:
- Existing code patterns and conventions
- File/folder organization
- API structure

### Step 4: Research (if needed)

<instructions>
If the task involves unfamiliar libraries or patterns, use WebSearch to look up:
1. Best practices for the identified framework
2. Documentation for new libraries or APIs needed
3. Known issues or gotchas related to the task
</instructions>

---

## Phase 3: Create Todo Spec

### Step 1: Determine next number

```
Bash: ls .hyper-team/todos/ 2>/dev/null | sort -n | tail -1 | grep -oP '^\d+' || echo "000"
```

Increment the number by 1 and zero-pad to 3 digits.

### Step 2: Create the directory

```
Bash: mkdir -p .hyper-team/todos
```

### Step 3: Write the todo document

<instructions>
Write the file to `.hyper-team/todos/NNN-subject.md` following this format:
</instructions>

```markdown
# NNN: Subject Title

<task>
Brief description of what needs to be built.
</task>

<context>
## Tech Stack
- Language: {language} {version}
- Framework: {framework} {version}
- Key Dependencies: {list}
- Build Tool: {tool}

## Current Architecture
{Brief description of relevant parts of the codebase}

## Relevant Files
- `path/to/file.ts` - {description}
</context>

<requirements>
## Functional Requirements
1. {requirement 1}
2. {requirement 2}

## Non-Functional Requirements
- Performance: {expectations}
- Security: {considerations}
- Testing: {coverage expectations}
</requirements>

<implementation_plan>
## Approach
{High-level approach description}

## Steps
1. {Step 1 - what to do and where}
2. {Step 2}

## Files to Create/Modify
- CREATE: `path/to/new-file.ts` - {purpose}
- MODIFY: `path/to/existing.ts` - {what to change}
</implementation_plan>

<side_effects>
## Potential Risks
- {Risk 1 and mitigation}

## Dependencies
- {Any new dependencies to install}
</side_effects>

<acceptance_criteria>
- [ ] {Criterion 1}
- [ ] {Criterion 2}
- [ ] All tests pass
- [ ] No regressions in existing features
</acceptance_criteria>
```

---

## Phase 4: Determine Team Strategy

<instructions>
Analyze the todo spec and decide the optimal team composition.

### Decision criteria

1. **Count the files** in the implementation plan (CREATE + MODIFY).
2. **Classify the work** into domains (backend, frontend, database, test, infra, etc.).
3. **Choose a pattern:**

| Condition | Pattern | Team |
|-----------|---------|------|
| All files in same domain, ≤5 files | **Small focused** | implementer + tester |
| All files in same domain, >5 files | **Uniform workers** | coordinator + worker-1..N + tester |
| Multiple domains | **Specialized workers** | domain-specific workers + tester |

### Guidelines

- Maximum 4 teammates (avoid overhead).
- Always include a **tester** role unless the task is purely non-functional (docs, config).
- If there's a shared utility/component that multiple workers depend on, assign a **coordinator** who creates it first.
- Assign clear file ownership to each teammate — no two teammates should modify the same file.
- Set task dependencies so dependent work waits for prerequisites.
- **NEVER skip team creation.** No matter how small the task, you MUST create a team and dispatch teammates. You are the leader — leaders do not implement.
- Minimum team size is **1 implementer** (for trivial/non-functional tasks) or **implementer + tester** (for code changes).

Store the chosen team composition and file assignments in context.
</instructions>

---

## Phase 5: Create Team and Execute

<instructions>
**MANDATORY:** This phase is NOT optional. You MUST execute all steps below.
You are the team leader. Your job is to create the team, assign tasks, and spawn teammates.
You MUST NOT write implementation code yourself — all code changes must be done by spawned teammates.
</instructions>

### Step 1: Create the team

```
TeamCreate:
- team_name: "just-do-it-NNN"
- description: "Implementing NNN-subject"
```

### Step 2: Create tasks

<instructions>
Create tasks for each teammate using TaskCreate. Example tasks:

For **Small focused** pattern:
1. "Implement NNN-subject" — assigned to implementer
2. "Write tests for NNN-subject" — assigned to tester, blockedBy implementer task

For **Uniform workers** pattern:
1. "Create shared utilities/components" — assigned to coordinator
2. "Implement {file-group-1}" — assigned to worker-1, blockedBy coordinator task
3. "Implement {file-group-2}" — assigned to worker-2, blockedBy coordinator task
4. "Write tests and verify" — assigned to tester, blockedBy all worker tasks

For **Specialized workers** pattern:
1. "Implement backend: {details}" — assigned to backend
2. "Implement frontend: {details}" — assigned to frontend, blockedBy backend if dependent
3. "Write tests and verify" — assigned to tester, blockedBy all implementation tasks

Set task dependencies using `addBlockedBy` where applicable.
</instructions>

### Step 3: Spawn teammates

<instructions>
Spawn each teammate with a clear prompt. Every teammate must:

1. Read the todo spec at `.hyper-team/todos/NNN-subject.md`
2. Check the task list and claim their assigned task
3. Do their work
4. Run relevant tests after changes
5. Mark their task as completed
6. Report results to the leader

**Teammate prompt template:**

```
You are the **{role}** on team "just-do-it-NNN".

1. Read the task spec: `.hyper-team/todos/NNN-subject.md`
2. Check TaskList and claim your task: "{task subject}"
3. Your responsibility:
   - {specific files and work to do}
   - {constraints: which files NOT to touch}
4. After completing your work:
   - Run tests: `{test command}`
   - Mark your task as completed
   - Send a message to the leader with your results
```

Spawn teammates using the Task tool with `team_name` parameter. Use `subagent_type: "general-purpose"` for all teammates.
</instructions>

### Step 4: Coordinate

<instructions>
As the team leader:

1. Monitor teammate progress via TaskList.
2. When a teammate completes a task that unblocks others, notify the blocked teammates.
3. If a teammate reports an issue, help resolve it or reassign work.
4. Wait for all tasks to complete.
</instructions>

---

## Phase 6: Verification

<instructions>
After all teammates finish, perform verification:
</instructions>

### Step 1: Re-read modified files

```
Read each file listed in the implementation plan to confirm changes are correct.
```

### Step 2: Build check

```
Bash: {build command from project analysis — e.g., npm run build, cargo build, go build}
```

<instructions>
If no build command exists, skip this step.
If build fails, fix the issues directly.
</instructions>

### Step 3: Run all tests

```
Bash: {test command from project analysis — e.g., npm test, pytest, go test ./...}
```

<instructions>
If tests fail:
1. Analyze the failure.
2. Fix the issue directly.
3. Re-run the failing test to confirm.
Repeat until all tests pass or the issue requires user input.
</instructions>

### Step 4: Dev server + browser test (if applicable)

<instructions>
If the project has a dev server and the task involves UI changes:

1. Start the dev server:
   ```
   Bash: timeout 30 {dev command} 2>&1 &
   ```
2. Use Playwright browser tools to verify:
   - `browser_navigate` to the relevant page
   - `browser_snapshot` to capture state
   - `browser_click` / `browser_fill` to test interactions
3. Stop the dev server when done.

Skip this step if:
- No dev server exists
- The task is backend-only or non-UI
</instructions>

---

## Phase 7: Cleanup and Report

### Step 1: Clean up team

```
TeamDelete
```

### Step 2: Mark todo as complete

<instructions>
If all verifications passed:

```
Bash: mv .hyper-team/todos/NNN-subject.md .hyper-team/todos/NNN-subject-complete.md
```

If there are remaining issues, do NOT rename the file.
</instructions>

### Step 3: Present final report

<output_format>

## Done: NNN-subject

### Team
| Role | Tasks | Status |
|------|-------|--------|
| {role} | {what they did} | {pass/fail} |

### Verification
| Check | Result |
|-------|--------|
| Build | {PASS/FAIL/N/A} |
| Tests | {X/Y passed} |
| Browser | {PASS/FAIL/N/A} |

### Files Changed
- `path/to/file.ts` — {what changed}

### Remaining Issues
{list or "None — all done!"}

### Todo
`.hyper-team/todos/NNN-subject-complete.md`

</output_format>

<instructions>
If there are remaining issues that couldn't be auto-fixed, list them clearly and suggest next steps:

```
Some issues remain. You can:
1. Fix them manually
2. Run `/hyper-team:verify NNN` for a detailed quality check
3. Run `/hyper-team:just-do-it fix the remaining issues in NNN-subject`
```
</instructions>
