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
Run build and tests with exit code capture, verify functional requirements against the acceptance criteria in the todo spec.
</task>

<instructions>
1. Read the spec file to understand acceptance criteria.

2. **Detect package manager:**
   ```
   Bash: if [ -f "pnpm-lock.yaml" ]; then echo "PM=pnpm"; elif [ -f "yarn.lock" ]; then echo "PM=yarn"; else echo "PM=npm"; fi
   ```
   Use the detected PM for all subsequent commands.

3. Find existing test files:
   ```
   Glob: **/*.{test,spec}.{ts,tsx,js,jsx,py}
   ```

4. **Run build** (if `build` script exists in package.json):
   ```
   Bash: $PM run build 2>&1; echo "BUILD_EXIT_CODE=$?"
   ```
   - If `BUILD_EXIT_CODE != 0` → mark build as CRITICAL failure, skip test execution, report immediately.

5. **Run tests** (if build passed or no build script):
   ```
   Bash: $PM test 2>&1; echo "TEST_EXIT_CODE=$?"
   ```
   Do NOT use `||` chains between package managers. Use the single detected PM.

6. If a dev server can be started, start it and verify the feature works:
   ```
   Bash: timeout 30 $PM run dev 2>&1 &
   ```

7. Check each acceptance criterion from the spec.

8. **Report to leader in this exact structure:**

   ```
   ## Tester Report

   ### Exit Codes
   - BUILD_EXIT_CODE: {0 or N, or N/A if no build script}
   - TEST_EXIT_CODE: {0 or N, or N/A if no tests}

   ### Build Output (if failed)
   ```
   {raw build error output}
   ```

   ### Test Output (last 20 lines)
   ```
   {raw test output — last 20 lines}
   ```

   ### Acceptance Criteria
   | # | Criterion | Result | Evidence |
   |---|-----------|--------|----------|
   | 1 | {criterion} | PASS/FAIL | {specific evidence} |

   ### Judgment
   - Build: PASS/FAIL (based on BUILD_EXIT_CODE)
   - Tests: PASS/FAIL (based on TEST_EXIT_CODE)
   ```

   **Judgment rules (mandatory):**
   - `BUILD_EXIT_CODE != 0` → Build: FAIL, entire verification: FAIL, skip tests
   - `TEST_EXIT_CODE != 0` → Tests: FAIL (regardless of your interpretation of output)
   - Even if exit code is 0, flag a WARNING if output contains `FAIL`, `Error`, or `failed`
</instructions>

### Teammate 2: code-reviewer

<task>
Analyze code quality with static analysis tools, then review patterns and potential issues in all files listed in the implementation plan.
</task>

<instructions>
1. Read all files listed in the spec's implementation plan.

2. **Run static analysis tools** (capture exit codes):

   a) **Type check** (if `tsconfig.json` exists):
   ```
   Bash: npx tsc --noEmit 2>&1; echo "TYPECHECK_EXIT_CODE=$?"
   ```

   b) **Lint** (if `lint` script exists in package.json):
   ```
   Bash: $PM run lint 2>&1; echo "LINT_EXIT_CODE=$?"
   ```
   (Use the same PM detection as tester: check lock files)

3. Analyze code quality on these criteria:

   <scoring_criteria>
   - **Readability** (0-20): Clear naming, proper formatting, comments where needed
   - **Maintainability** (0-20): SOLID principles, DRY, low coupling
   - **Error Handling** (0-20): Proper try/catch, edge cases handled, validation
   - **Security** (0-20): No vulnerabilities, input sanitization, auth checks
   - **Performance** (0-20): No obvious bottlenecks, efficient algorithms, proper caching
   </scoring_criteria>

4. Check for code smells:
   - Duplicated code
   - Long functions (>50 lines)
   - Deep nesting (>3 levels)
   - Magic numbers/strings
   - Missing type annotations (if typed language)

5. **Report to leader in this exact structure:**

   ```
   ## Code Review Report

   ### Static Analysis Results
   | Tool | Exit Code | Errors | Warnings |
   |------|-----------|--------|----------|
   | Type Check (tsc) | {0/N/N/A} | {count} | {count} |
   | Lint | {0/N/N/A} | {count} | {count} |

   ### Static Analysis Output (if errors found)
   ```
   {raw error output}
   ```

   ### Code Quality Score
   | Criteria | Score | Notes |
   |----------|-------|-------|
   | Readability | /20 | {notes} |
   | Maintainability | /20 | {notes} |
   | Error Handling | /20 | {notes} |
   | Security | /20 | {notes} |
   | Performance | /20 | {notes} |
   | **Total** | **/100** | |

   ### Code Smells
   {list of findings}
   ```
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

### Evidence (검증 증거)

**Exit code 기반 판정** — teammate의 자연어 해석과 exit code가 불일치하면 **exit code를 우선**합니다.

| 항목 | Exit Code | 상태 |
|------|-----------|------|
| Build | {BUILD_EXIT_CODE} | PASS/FAIL/N/A |
| Test | {TEST_EXIT_CODE} | PASS/FAIL/N/A |
| Type Check | {TYPECHECK_EXIT_CODE} | PASS/FAIL/N/A |
| Lint | {LINT_EXIT_CODE} | PASS/FAIL/N/A |

#### 테스트 출력 (마지막 20줄)
```
{raw test output from tester report}
```

#### 빌드/타입체크/린트 에러 (해당 시)
```
{raw error output from tester and code-reviewer reports}
```

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

### Static Analysis
| Tool | Exit Code | Errors | Warnings |
|------|-----------|--------|----------|
| Type Check (tsc) | {0/N/N/A} | {count} | {count} |
| Lint | {0/N/N/A} | {count} | {count} |

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
**Exit code 기반 자동 판정 규칙 (필수):**
- exit code가 0이 아닌 항목이 하나라도 있으면 해당 항목은 FAIL
- teammate 메시지에서 "통과"라고 했더라도 exit code가 0이 아니면 FAIL로 판정
- exit code가 0인데 출력에 `FAIL`, `Error`, `failed`가 포함되면 WARNING 표시

After presenting the report, extract structured issues from each teammate's findings.

Categorize issues by source and severity:

**Test Issues** (from tester):
- CRITICAL: `BUILD_EXIT_CODE != 0` or `TEST_EXIT_CODE != 0`
- MAJOR: Acceptance criteria not met (even if tests pass)

**Code Quality Issues** (from code-reviewer):
- CRITICAL: `TYPECHECK_EXIT_CODE != 0` or score below 10/20 in any category
- MAJOR: `LINT_EXIT_CODE != 0` or score below 15/20 in any category
- MINOR: Code smells, style issues (lint warnings)

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

Store the initial score, exit codes, and issue list in context. Then clean up the team:
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
Perform a lightweight re-verification without creating a team. Use the same exit code capture approach:

1. **Detect package manager** (same as Phase 3):
   ```
   Bash: if [ -f "pnpm-lock.yaml" ]; then PM="pnpm"; elif [ -f "yarn.lock" ]; then PM="yarn"; else PM="npm"; fi
   ```

2. **Re-run build** (if build issues were fixed):
   ```
   Bash: $PM run build 2>&1; echo "BUILD_EXIT_CODE=$?"
   ```

3. **Re-run tests** (if test issues were fixed):
   ```
   Bash: $PM test 2>&1; echo "TEST_EXIT_CODE=$?"
   ```

4. **Re-run type check** (if type issues were fixed and tsconfig.json exists):
   ```
   Bash: npx tsc --noEmit 2>&1; echo "TYPECHECK_EXIT_CODE=$?"
   ```

5. **Re-run lint** (if lint issues were fixed and lint script exists):
   ```
   Bash: $PM run lint 2>&1; echo "LINT_EXIT_CODE=$?"
   ```

6. **Re-evaluate code quality** on modified files only:
   - Read each file that was modified in Phase 6
   - Re-score using the same 5 criteria (Readability, Maintainability, Error Handling, Security, Performance)

7. **Check integration status**:
   ```
   Bash: git status
   Bash: git diff --stat
   ```

8. Present a comparison table with exit codes:
</instructions>

<output_format>

## Re-verification Results (Iteration {N})

### Exit Code Comparison
| 항목 | Before | After |
|------|--------|-------|
| Build Exit Code | {N} | {N} |
| Test Exit Code | {N} | {N} |
| Type Check Exit Code | {N/N/A} | {N/N/A} |
| Lint Exit Code | {N/N/A} | {N/N/A} |

### Metrics Comparison
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
