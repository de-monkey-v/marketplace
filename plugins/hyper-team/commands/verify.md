---
name: verify
description: Verify implementation against a todo spec. Runs tests, analyzes code quality, checks git status, and provides a comprehensive score. Specify NNN-subject or just NNN.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, AskUserQuestion, Task, TeamCreate, TeamDelete, SendMessage, TaskCreate, TaskUpdate, TaskList, TaskGet
---

Create a team. Verify the implementation specified in a hyper-team todo file.

**Arguments:** `$ARGUMENTS` (NNN-subject or just NNN)

---

## Phase 1: Locate Todo File

<instructions>
Parse `$ARGUMENTS` to find the matching todo file.

If `$ARGUMENTS` is a 3-digit number (e.g., `001`):
</instructions>

```
Glob: .hyper-team/todos/{$ARGUMENTS}*
```

<instructions>
If `$ARGUMENTS` is a full name (e.g., `001-user-auth`):
</instructions>

```
Read: .hyper-team/todos/$ARGUMENTS.md
```

<instructions>
If the file is not found, also check for the completed variant:
</instructions>

```
Glob: .hyper-team/todos/{$ARGUMENTS}*-complete*
```

<instructions>
If no arguments provided, list available todos:
</instructions>

```
Bash: ls -la .hyper-team/todos/ 2>/dev/null
```

Then ask the user which one to verify.

If no todo files exist, inform the user:
```
No todo files found. Use `/hyper-team:make-prompt` to create one first.
```

---

## Phase 2: Parse Requirements

<instructions>
Read the todo file and extract:

1. All items from `<requirements>` section
2. All items from `<acceptance_criteria>` section
3. Files listed in `<implementation_plan>` (CREATE and MODIFY)
4. Items from `<side_effects>` to watch for

Store these in your context for team task creation.
</instructions>

---

## Phase 3: Create Team and Verify

<instructions>
Create a team with 3 teammates to perform verification in parallel.

Spawn the following teammates:
</instructions>

### Teammate 1: tester

<task>
Run all tests, start the dev server if applicable, and verify functional requirements against the acceptance criteria in the todo spec.
</task>

<instructions>
1. Read the spec file to understand acceptance criteria.
2. Find and run existing tests:
   ```
   Glob: **/*.{test,spec}.{ts,tsx,js,jsx,py}
   ```
3. If a test script exists in package.json, run it:
   ```
   Bash: npm test 2>&1 || yarn test 2>&1 || pnpm test 2>&1
   ```
4. If a dev server can be started, start it and verify the feature works:
   ```
   Bash: timeout 30 npm run dev 2>&1 &
   ```
5. Check each acceptance criterion from the spec.
6. Report results back to the leader.
</instructions>

### Teammate 2: code-reviewer

<task>
Analyze code quality, patterns, and potential issues in all files listed in the implementation plan.
</task>

<instructions>
1. Read all files listed in the spec's implementation plan.
2. Analyze code quality on these criteria:

   <scoring_criteria>
   - **Readability** (0-20): Clear naming, proper formatting, comments where needed
   - **Maintainability** (0-20): SOLID principles, DRY, low coupling
   - **Error Handling** (0-20): Proper try/catch, edge cases handled, validation
   - **Security** (0-20): No vulnerabilities, input sanitization, auth checks
   - **Performance** (0-20): No obvious bottlenecks, efficient algorithms, proper caching
   </scoring_criteria>

3. Check for code smells:
   - Duplicated code
   - Long functions (>50 lines)
   - Deep nesting (>3 levels)
   - Magic numbers/strings
   - Missing type annotations (if typed language)

4. Report findings and scores back to the leader.
</instructions>

### Teammate 3: integration-checker

<task>
Check git status, verify no regressions, and test for side effects.
</task>

<instructions>
1. Run git status and git diff to see all changes:
   ```
   Bash: git status
   Bash: git diff --stat
   ```
2. Verify files match the spec (all CREATE/MODIFY files exist and are changed).
3. Check for unintended changes to files not in the spec.
4. Look for potential side effects from `<side_effects>` section.
5. Verify no existing tests are broken.
6. Report findings back to the leader.
</instructions>

---

## Phase 4: Compile Final Report + Extract Issues

<instructions>
After all teammates complete their work, compile a final verification report:
</instructions>

<output_format>

## Verification Report: NNN-subject

### Test Results
- Tests Passed: X/Y
- Acceptance Criteria Met: X/Y
- Server Check: PASS/FAIL/N/A

### Code Quality Score
| Criteria | Score | Notes |
|----------|-------|-------|
| Readability | /20 | {notes} |
| Maintainability | /20 | {notes} |
| Error Handling | /20 | {notes} |
| Security | /20 | {notes} |
| Performance | /20 | {notes} |
| **Total** | **/100** | |

### Grade
- 90-100: A (Excellent)
- 80-89: B (Good)
- 70-79: C (Acceptable)
- 60-69: D (Needs Improvement)
- Below 60: F (Major Issues)

### Integration Status
- Files Changed: {expected vs actual}
- Unintended Changes: {list or "None"}
- Regressions: {list or "None"}

### Recommendations
1. {Recommendation 1}
2. {Recommendation 2}

</output_format>

<instructions>
After presenting the report, extract structured issues from each teammate's findings.

Categorize issues by source and severity:

**Test Issues** (from tester):
- CRITICAL: Tests that fail and block functionality
- MAJOR: Acceptance criteria not met

**Code Quality Issues** (from code-reviewer):
- CRITICAL: Score below 10/20 in any category
- MAJOR: Score below 15/20 in any category
- MINOR: Code smells, style issues

**Integration Issues** (from integration-checker):
- CRITICAL: Missing files from implementation plan, regressions detected
- MAJOR: Unintended file changes, potential side effects

Build an issue list with this structure for each issue:
- ID: Sequential number (e.g., #1, #2, ...)
- Source: tester / code-reviewer / integration-checker
- Severity: CRITICAL / MAJOR / MINOR
- Description: Clear description of the problem
- File: Affected file path (if applicable)
- Suggested Fix: Brief description of how to fix it

Store the initial score and issue list in context. Then clean up the team:
</instructions>

```
TeamDelete
```

<instructions>
If there are **zero issues**, skip directly to Phase 8.

If there are issues, proceed to Phase 5.
</instructions>

---

## Phase 5: Fix Decision Loop

<instructions>
Present the extracted issues to the user, grouped by severity:
</instructions>

<output_format>

## Issues Found

### CRITICAL
| # | Source | Description | File |
|---|--------|-------------|------|
| {id} | {source} | {description} | {file} |

### MAJOR
| # | Source | Description | File |
|---|--------|-------------|------|
| {id} | {source} | {description} | {file} |

### MINOR
| # | Source | Description | File |
|---|--------|-------------|------|
| {id} | {source} | {description} | {file} |

</output_format>

<instructions>
Ask the user what to do using `AskUserQuestion`:

- **Option 1: "모든 이슈 수정 (Recommended)"** — Fix all issues, proceed to Phase 6 with full list
- **Option 2: "Critical/Major만 수정"** — Fix only CRITICAL and MAJOR issues, proceed to Phase 6
- **Option 3: "현재 점수 수용"** — Accept current score, skip to Phase 8

If the user chooses to fix, proceed to Phase 6 with the selected issue list.
If the user accepts the current score, proceed to Phase 8.
</instructions>

---

## Phase 6: Apply Fixes

<instructions>
Fix the selected issues directly (no team needed). Follow this order for dependencies:
1. **Integration issues** first (missing files, structural problems)
2. **Code quality issues** next (code improvements)
3. **Test issues** last (functional fixes that depend on correct structure)

For each issue:
1. Read the affected file(s)
2. Analyze the issue and determine the fix
3. Apply the fix using `Edit` or `Write`
4. For test issues: run the specific failing test to verify
   ```
   Bash: {test command for the specific test}
   ```
5. For code issues: re-read the file to confirm the change looks correct
6. Report progress:
   ```
   Fixed [N/total]: {description of what was fixed}
   ```

If a fix cannot be applied automatically (e.g., requires architectural changes, external dependencies, or user decisions), report it as:
```
SKIPPED [N/total]: {reason why it cannot be auto-fixed}
```

Important:
- Do NOT create git commits. All changes stay in the working tree.
- Keep fixes minimal and focused. Do not refactor beyond what is needed to resolve the issue.
- If fixing one issue might affect another, note the dependency.
</instructions>

---

## Phase 7: Re-verify

<instructions>
Perform a lightweight re-verification without creating a team:

1. **Re-run tests** (if test issues were fixed):
   ```
   Bash: {same test command used in Phase 3}
   ```

2. **Re-evaluate code quality** on modified files only:
   - Read each file that was modified in Phase 6
   - Re-score using the same 5 criteria (Readability, Maintainability, Error Handling, Security, Performance)

3. **Check integration status**:
   ```
   Bash: git status
   Bash: git diff --stat
   ```

4. Present a comparison table:
</instructions>

<output_format>

## Re-verification Results (Iteration {N})

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Tests Passed | X/Y | X/Y | {+/-} |
| Acceptance Criteria | X/Y | X/Y | {+/-} |
| Code Quality | /100 | /100 | {+/-} |
| Issues Remaining | N | N | {-N} |

### Resolved Issues
- ✅ #{id}: {description}

### Remaining Issues
- ❌ #{id}: {description}

</output_format>

<instructions>
Determine next step based on results:

- **All issues resolved OR score >= 90 (Grade A):** Proceed to Phase 8
- **Issues remain AND iteration < 3:** Return to Phase 5 with updated issue list
- **Iteration >= 3 with issues remaining:** Ask the user using `AskUserQuestion`:
  - **Option 1: "현재 결과 수용 (Recommended)"** — Accept current state, proceed to Phase 8
  - **Option 2: "한 번 더 시도"** — Allow one more fix iteration (return to Phase 5)
  - **Option 3: "수동 리뷰로 전환"** — End with remaining issues listed for manual review, proceed to Phase 8
</instructions>

---

## Phase 8: Final Summary

<instructions>
Present the complete verification-fix summary:
</instructions>

<output_format>

## Final Summary: NNN-subject

### Score Progression
| Iteration | Score | Grade | Issues |
|-----------|-------|-------|--------|
| Initial | /100 | {grade} | {count} |
| Fix #{N} | /100 | {grade} | {count} |
| ... | ... | ... | ... |
| **Final** | **/100** | **{grade}** | **{count}** |

### Files Modified During Fixes
{list of files changed during Phase 6, or "None" if no fixes were applied}

### Remaining Issues
{list of unresolved issues, or "None — all issues resolved!"}

</output_format>

<instructions>
If the final grade is A (>= 90) and no issues remain, suggest marking the todo as complete:
```
Grade A achieved! Consider marking this todo as complete by renaming:
  .hyper-team/todos/NNN-subject.md → .hyper-team/todos/NNN-subject-complete.md
```

If fixes were applied but not committed, remind the user:
```
Note: All fixes have been applied to the working tree but NOT committed.
Review the changes with `git diff` and commit when ready.
```
</instructions>
