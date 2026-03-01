---
name: commit
description: This skill should be used when the user asks to "커밋해줘", "커밋하고", "커밋 좀", "변경사항 저장", "커밋하고 푸시", "commit changes", "git commit", "make a commit", "commit and push", "stage and commit", or mentions committing code changes. Generates meaningful commit messages following Conventional Commits.
allowed-tools: Bash, Read, Grep, Glob, AskUserQuestion
---

# Git Commit Skill

Analyze changes and generate meaningful commit messages following Conventional Commits. **Default is DETAILED format** with What/Why sections. Use `--simple` flag for brief format.

## Language Resolution

1. Check `$ARGUMENTS` for `--language=eng` or `--language=kor` → use if present
2. Check current conversation language and recent `git log` style
3. Read `.hyper-team/metadata.json` only as a fallback hint when 1-2 are inconclusive
4. Default: `kor`

Produce all user-facing output in the resolved language. Write the commit subject and body content in the resolved language. Keep section labels such as `What`, `Why`, `Impact`, and `Notes` in English unless the repository explicitly defines different labels.

## Core Workflow

### Step 1: Gather Information

Run these commands in parallel:

```bash
git status                    # Changed files
git log --oneline -5          # Recent commit style
git diff --cached             # Staged changes
git diff                      # Unstaged changes
git diff --stat               # Change statistics
git diff --name-status        # File-level change type (A/M/D)
git branch --show-current     # Current branch (for issue extraction)
```

Also read CONTRIBUTING.md if present for commit conventions.

### Step 2: Analyze Changes

#### 2.0 Claude-Modified File Filtering (Auto Mode)

**When `-a` option is used (default):**
- Only include files modified via Edit/Write tool in current conversation
- Filter from full `git status` change list to include only Claude-modified files
- Automatically exclude unrelated files

**When `-a --all` option is used:**
- Include all changed files (legacy behavior)

**When `-a --split` option is used:**
- Group related files together
- Create separate commits per group
- Example: Plugin A changes → commit 1, Plugin B changes → commit 2

#### 2.1 Per-File Analysis
- Identify each changed file's role and modification details
- Check file-level change type (A: added, M: modified, D: deleted)
- Identify added/modified/deleted classes, functions, methods

#### 2.2 Context Analysis
- **Background**: What situation led to the change?
- **Problem**: What specific issue existed in the previous code?
- **Effect**: What improvements are expected after the change?

#### 2.3 Impact Analysis
- Identify affected features, modules, services
- Check for dependency changes (package.json, requirements.txt, etc.)
- Determine whether there are breaking changes

#### 2.4 Test Considerations
- Test scenarios to verify
- Caveats or migration requirements

#### 2.5 Scope Extraction
- **Issue numbers** from branch name (e.g., `feature/123-xxx` → `#123`)

**Scope Extraction Examples:**
- `src/auth/*.java` → `(auth)`
- `plugins/git-utils/*` → `(git-utils)`
- `api/users/*.ts` → `(users)`
- Multiple areas with no common path → omit scope

### Step 3: Generate Commit Message

**Default: Detailed Conventional Commits** (see `references/message-format.md`)

```
<type>(scope): 간결한 제목 (50자 내외)

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

**Quality Check**: Self-review after writing message
- Can the change be understood from the subject alone?
- Does the body explain "why" the change was made?
- Will this commit be understandable 6 months from now?

**Simple format (`--simple` flag):**

```
<type>: 간결한 제목 (50자 내외)

1. 주요 변경 사항
2. 보조 변경 사항
3. 추가 설명 (필요 시)
```

Select commit type from `references/commit-types.md`.

### Step 4: Validate Before Commit

**Security check** - Detect sensitive files:
- `.env`, `.env.*`
- `application-prod.yml`, `application-secret.yml`
- `credentials.json`, `secrets.*`
- Patterns: `password`, `secret`, `api_key`

If detected, warn and request confirmation.

**File relevance check** - If unrelated files are staged, offer options:
1. Commit related files only (recommended)
2. Commit all files
3. Manual selection

### Step 5: User Confirmation

**Normal mode**: Show preview and request approval

```
=== Commit Preview ===

Message:
<feat>: 취미 정리 확인 플로우 추가

What
- 웹, rust-api, ai-service에 취미 제안 엔드포인트와 확인 UI를 추가함
- 저장 후 재진입과 재저장 시 확정 취미 메타데이터가 유지되도록 read/write 계약을 정리함

Why
- 질문 수정 화면에서 카테고리와 근거 표현이 유실되는 회귀를 막기 위해
- 취미 정규화 결과를 저장 전에 사용자가 확인하고 수정할 수 있게 하기 위해

Files to commit:
- src/main/java/UserService.java
- src/main/java/UserController.java

Proceed with commit? (y/n)
```

**Auto mode (`-a`)**: Commit immediately without confirmation
- Only Claude-modified files are auto-selected
- Unrelated files are excluded
- With `--all` option, all changed files are included

### Step 6: Execute Commit

```bash
git add <selected-files>
git commit -m "$(cat <<'EOF'
<feat>: 취미 정리 확인 플로우 추가

What
- 웹, rust-api, ai-service에 취미 제안 엔드포인트와 확인 UI를 추가함
- 저장 후 재진입과 재저장 시 확정 취미 메타데이터가 유지되도록 read/write 계약을 정리함

Why
- 질문 수정 화면에서 카테고리와 근거 표현이 유실되는 회귀를 막기 위해
- 취미 정규화 결과를 저장 전에 사용자가 확인하고 수정할 수 있게 하기 위해
EOF
)"
git status
```

### Step 7: Report Result

```
Commit complete!

Hash: a1b2c3d
Branch: feature/user-auth

Next steps:
- Request code review
- git push origin <branch>
```

## Critical Rules

### Commit message language follows metadata

**Commit messages are written in the resolved language:**
- Subject and bullet contents — in the resolved language
- Keep section labels such as `What`, `Why`, `Impact`, and `Notes` in English unless repo docs say otherwise
- Code paths, issue numbers, and technical terms remain as-is
- Example (eng): `<feat>(auth): implement user authentication`
- Example (kor): `<feat>: 취미 정리 확인 플로우 추가`
- If the user asks in Korean, keep the commit message content in Korean unless the repository explicitly requires another language

### Signatures are NEVER Allowed

**Never include:**
- `generated with [Claude Code]` — forbidden
- `Co-Authored-By: Claude` — forbidden
- `🤖` emoji — forbidden
- Any form of auto-generated signature — forbidden

### CONTRIBUTING.md Compliance

- Use `<type>:` format (angle brackets required)
- Select from 11 valid types only
- Space after colon

**Correct:** `<feat>: 사용자 인증 기능 추가`
**Wrong:** `feat: 사용자 인증 기능 추가` (no brackets)

### User Confirmation Required

Always get user approval before:
- Committing files with sensitive data
- Including unrelated files
- Final commit execution

## Error Handling

| Error | Action |
|-------|--------|
| No changes | Exit with message |
| Merge conflict | Request resolution first |
| Not a git repo | Suggest git init |
| No CONTRIBUTING.md | Use default commit types |

## Additional Resources

### Reference Files

For detailed information, consult:
- **`references/commit-types.md`** - Complete commit type list with examples
- **`references/message-format.md`** - Message format rules and examples

## Related Skills

- `status`: Check repository state before commit
- `diff`: Analyze changes in detail
