# Auto-Fix Loop Pattern

## Overview

When verification detects Critical or Major issues, the auto-fix loop re-invokes the Creator agent with feedback, then re-runs only the failed verification Tasks.

```
Verification FAIL (Critical/Major)
     ↓
Round 1: Creator re-invocation with feedback
     ↓
Re-run failed verifications only
     ├── PASS → Continue
     └── FAIL → Round 2
           ↓
Round 2: Creator re-invocation with accumulated feedback
     ↓
Re-run failed verifications only
     ├── PASS → Continue
     └── FAIL → AskUserQuestion (3 options)
```

## Step 1: Creator Agent Re-Invocation

Re-invoke the appropriate Creator agent Task with `<review-feedback>`:

```
Task tool:
- subagent_type: "plugin-creator:{type}-creator"
- description: "Fix {component-name} based on verification feedback"
- prompt: |
    <task-context>
    <plugin-path>{plugin-path}</plugin-path>
    <component-name>{component-name}</component-name>
    <mode>{project or plugin}</mode>
    </task-context>

    <review-feedback>
    The following issues were found during verification:

    **Critical issues:**
    {list of critical issues with specific file paths and line context}

    **Major issues:**
    {list of major issues with specific fix suggestions}
    </review-feedback>

    <instructions>
    Fix the issues listed in the review feedback.
    Read the current file(s) first, then apply the necessary corrections.
    Preserve all existing functionality while fixing the reported issues.
    </instructions>
```

**Creator agent mapping:**

| Component Type | Creator Agent |
|---------------|---------------|
| Skill | `plugin-creator:skill-creator` |
| Agent | `plugin-creator:agent-creator` |
| Command | `plugin-creator:command-creator` |
| Hook | `plugin-creator:hook-creator` |

## Step 2: Re-Run Failed Verifications Only

After the Creator fixes issues, re-run **only the Tasks that reported Critical/Major issues**.

Example: If a skill's V1 (skill-reviewer) reported Major issues but V2 and V3 passed:
- Only re-run V1
- Do NOT re-run V2 and V3

This reduces overhead and avoids redundant checks.

## Step 3: Maximum Rounds

**Maximum 2 rounds of auto-fix** per component.

After 2 rounds, if issues persist:

```
AskUserQuestion:
- question: "Verification found persistent issues after 2 auto-fix attempts.
  Issues remaining:
  {remaining issue summary}

  How would you like to proceed?"
- header: "Persistent Verification Issues"
- options:
  - label: "Review manually and continue (Recommended)"
    description: "Examine the issues yourself and decide how to proceed"
  - label: "Ignore issues and continue"
    description: "Accept current state and move to next component (not recommended)"
  - label: "Cancel creation"
    description: "Stop the entire creation process"
```

## Minor Issue Handling

Minor issues do **not** trigger the auto-fix loop.

- Display minor issues as warnings to the user
- Continue to the next component
- Minor issues are included in the final summary

Example warning:

```markdown
> **Verification Warning** ({component-name}):
> - Minor: Consider adding Korean trigger phrases to description
> - Minor: references/advanced.md exists but is not referenced from SKILL.md
```

## Accumulated Feedback Pattern

In Round 2, include both the original issues and the issues from Round 1 re-verification:

```
<review-feedback>
**Round 1 issues (original):**
{original issues}

**Round 2 issues (persisted after first fix):**
{issues that were not resolved}

**Note:** These issues persisted after the first fix attempt.
Focus specifically on resolving the remaining issues.
</review-feedback>
```

## Flow Summary

```
For each component with FAIL result:
  round = 0
  while round < 2:
    round += 1
    1. Re-invoke Creator with <review-feedback>
    2. Re-run failed verification Tasks only
    3. Collect results
    4. If all PASS/WARN → break (success)

  if still FAIL after 2 rounds:
    AskUserQuestion → user decides
```
