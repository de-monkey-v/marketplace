---
name: commit
description: This skill should be used when the user asks to "커밋해줘", "커밋하고", "커밋 좀", "변경사항 저장", "커밋하고 푸시", "commit changes", "git commit", "make a commit", "commit and push", "stage and commit", or mentions committing code changes. Generates meaningful commit messages following Conventional Commits.
allowed-tools: Bash, Read, Grep, Glob, AskUserQuestion
---

# Git Commit Skill

Analyze changes and generate meaningful commit messages following Conventional Commits. **Default is DETAILED format** with What/Why sections. Use `--simple` flag for brief format.

## Language Resolution

1. Check `$ARGUMENTS` for `--language=eng` or `--language=kor` → use if present
2. Read `.hyper-team/metadata.json` → use `language` field if file exists
3. Default: `eng`

Produce all user-facing output in the resolved language. Write commit messages in the resolved language.

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
<type>(scope): concise subject (max 50 chars)

## What
Describe the specific changes made.

- `path/to/file.ts`: change summary
- Added classes/functions/methods
- Modified core logic
- Removed elements

## Why
Explain the motivation and how it differs from previous behavior.

- Background: context that led to the change
- Problem: specific issue being resolved
- Effect: expected improvements after the change

## Impact — if applicable
- Affected features/modules
- Dependency changes (added/removed/updated)
- Performance impact

## Notes — if applicable
- Test scenarios to verify
- Caveats
- Related documentation links

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
<type>: concise subject (max 50 chars)

1. Primary change
2. Secondary change
3. Additional details (if needed)
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
<feat>: Add user authentication API

1. Implement JWT token-based auth
2. Add login/logout endpoints
3. Integrate Spring Security

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
<feat>: Add user authentication API

1. Implement JWT token-based auth
2. Add login/logout endpoints
3. Integrate Spring Security
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
- Subject, What, Why sections — all in the resolved language
- Code paths, issue numbers, and technical terms remain as-is
- Example (eng): `<feat>(auth): implement user authentication`
- Example (kor): `<feat>(auth): 사용자 인증 기능 추가`

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

**Correct:** `<feat>: add user authentication`
**Wrong:** `feat: Add user auth` (no brackets)

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
