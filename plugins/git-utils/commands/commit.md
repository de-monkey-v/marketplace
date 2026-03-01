---
name: git-utils:commit
description: Analyze changes and create a commit with auto-generated message
argument-hint: "[--simple|-s] [--auto|-a] [--push] [message]"
allowed-tools: Bash, Read, Grep, Glob, AskUserQuestion
---

<!--
Usage: /git-utils:commit [options] [message]
Examples:
  /git-utils:commit                          # Detailed (default)
  /git-utils:commit --simple                 # Simple format
  /git-utils:commit -s                       # Simple format (short)
  /git-utils:commit "Fix bug"                # Detailed with title
  /git-utils:commit -s "Fix bug"             # Simple with title
  /git-utils:commit --auto                   # Auto commit without confirmation
  /git-utils:commit -a -s "Fix bug"          # Auto + Simple
  /git-utils:commit --push                   # Commit + push
  /git-utils:commit -a --all --push          # Auto commit all + push
  /git-utils:commit -a --split --push        # Auto split commits + push
-->

Analyze Git changes and create a commit following Conventional Commits.

## Language Resolution

1. Check `$ARGUMENTS` for `--language=eng` or `--language=kor` → use if present
2. Check current conversation language and recent `git log` style
3. Read `.hyper-team/metadata.json` only as a fallback hint when 1-2 are inconclusive
4. Default: `kor`

Produce all user-facing output in the resolved language. Write the commit subject and body content in the resolved language. Keep section labels such as `What`, `Why`, `Impact`, and `Notes` in English unless the repository explicitly defines different labels.

## CRITICAL — Never Forget

**Commit types MUST be wrapped in `<>`:**
- Correct: `<feat>`, `<fix>`, `<refactor>`, `<docs>`
- Wrong: `feat`, `fix`, `refactor`, `docs`

**Always verify before every commit:** Does the subject start with `<type>`?

## Context Gathering

Gather repository state by running these commands (user's current working directory):
```bash
git status -s
git log --oneline -5
git branch --show-current
git diff --stat
git diff --name-status
```

If `--push` is present, also check remote tracking:
```bash
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "NO_UPSTREAM"
```

## Arguments Parsing

**FIRST: Parse `$ARGUMENTS` and determine mode BEFORE doing anything else.**

Parse `$ARGUMENTS`:
- `--simple` or `-s`: Use simple format (numbered list)
- `--auto` or `-a`: Auto-commit mode (NO confirmation, NO preview)
- `--all`: Include all changed files (use with `-a`: `-a --all`)
- `--split`: Split commits by change type (use with `-a`: `-a --split`)
- `--push`: Push to remote after commit completes
- Remaining text: User-provided commit message/title

**Default is DETAILED format (Conventional Commits with body).**

### Auto Mode (`-a`) — CRITICAL

**When `-a` is present, you MUST NOT ask for confirmation. Proceed directly to commit.**

| Option | File Scope | Confirmation |
|--------|-----------|--------------|
| `-a` | Only files Claude modified via Edit/Write in current session | **NEVER ask** |
| `-a --all` | **ALL** changed files (staged + unstaged + untracked) | **NEVER ask** |
| `-a --split` | Group related files, separate commits per group | **NEVER ask** |
| *(no `-a`)* | All changed files | Ask user |

## Workflow

1. **Analyze Changes**
   - Run `git status` and `git diff` to understand modifications
   - Identify change type: new feature, bug fix, refactor, docs, etc.
   - Extract scope from file paths (common directory/module)
   - **Identify Claude-modified files** (auto mode):
     - Track files modified via Edit/Write tool in current conversation
     - When `-a` option is used, only include those files for commit
     - Exclude unrelated files unless `--all` option is present

   **Detailed Analysis (for Detailed format):**
   - Per-file changes: Identify each file's role and modification details
   - Context analysis: Background (why needed), Problem (previous code issues), Effect (improvements)
   - Impact analysis: Affected modules, dependency changes, Breaking changes
   - Notes: Test scenarios, caveats, migration requirements

2. **Security Check**
   - Detect sensitive files: `.env`, `credentials.json`, `*-prod.yml`
   - Warn if secrets detected, request confirmation

3. **Generate Commit Message**

   **CRITICAL: type MUST be wrapped in `<>` (e.g., `<feat>`, `<fix>`)**

   ### If `--simple` or `-s` flag:
   ```
   <feat>: 간결한 제목 (50자 내외)

   1. 주요 변경 사항
   2. 보조 변경 사항
   3. 추가 설명 (필요 시)
   ```

   ### Default (Detailed Conventional Commits):
   ```
   <feat>(scope): 간결한 제목 (50자 내외)

   What
   구체적으로 무엇을 바꿨는지 작성한다.

   - `path/to/file.ts`: 변경 요약
   - 추가한 클래스/함수/메서드
   - 수정한 핵심 로직
   - 제거한 요소

   Why
   왜 바꿨는지와 이전 동작 대비 차이를 작성한다.

   - Background: 변경 배경
   - Problem: 해결하려는 문제
   - Effect: 기대 효과

   Impact — if applicable
   - 영향 받는 기능/모듈
   - 의존성 변경 (추가/제거/수정)
   - 성능 영향

   Notes — if applicable
   - 확인할 테스트 시나리오
   - 주의 사항
   - 관련 문서 링크

   Fixes: #123
   Related: #456
   BREAKING CHANGE: description of API change (if applicable)
   ```

   **Quality Check (after generating message):**
   - Can the change be understood from the subject alone?
   - Does the body explain "why" the change was made?
   - Will this commit be understandable 6 months from now?

   **References extraction:**
   - Branch name: `feature/123-xxx` → `Fixes: #123`
   - Look for issue numbers in recent context

4. **User Confirmation**
   - **If `-a` (auto mode): SKIP this step entirely. Do NOT show preview. Go directly to Step 5.**
   - Otherwise: Show preview with message and files, request approval

5. **Execute Commit**

   **Final check before execution:** Does the subject start with `<type>`?
   - Correct: `<feat>(scope):` / Wrong: `feat(scope):`

   ```bash
   git add <selected-files>
   git commit -m "$(cat <<'EOF'
   <commit message here>
   EOF
   )"
   ```

6. **Push (if `--push`)**

   Only execute this step when `--push` is present. Run after ALL commits are complete (including `--split`).

   ```bash
   # If no upstream, set it:
   git push -u origin $(git branch --show-current)
   # If upstream exists:
   git push
   ```

   - `--split --push`: Create all split commits first, then push once at the end
   - Push failure: Show error and suggest manual resolution (do NOT retry with `--force`)

7. **Report Result**
   Show commit hash, branch, and next steps.
   If `--push` was used, include push result (remote URL, branch).

## Critical Rules

**Commit message language follows resolved language:**
- Write the subject and bullet contents in the resolved language
- Keep section labels such as `What`, `Why`, `Impact`, and `Notes` in English unless repo docs say otherwise
- Code paths, issue numbers, and technical terms remain in their original form
- If the user asks in Korean, keep the commit message content in Korean unless the repository explicitly requires another language

**Signatures are NEVER allowed:**
- `generated with [Claude Code]` — forbidden
- `Co-Authored-By: Claude` — forbidden
- `🤖` emoji — forbidden
- Any form of auto-generated signature — forbidden

**Commit types — MUST include `<>`:**
- `<feat>` - New feature
- `<fix>` - Bug fix
- `<refactor>` - Code restructure
- `<docs>` - Documentation
- `<test>` - Tests
- `<style>` - Formatting
- `<perf>` - Performance
- `<chore>` - Misc tasks

**Correct subject examples:**
```
<feat>(auth): JWT 인증 미들웨어 추가
<fix>(api): 사용자 조회 null 오류 수정
<refactor>(domain): 엔티티 구조 정리
```

**Wrong examples (NEVER do this):**
```
feat: subject          ← missing <>
feat(scope): subject   ← missing <>
```

**Get user approval before executing commit — UNLESS `-a` (auto mode) is present.**
