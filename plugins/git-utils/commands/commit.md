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
2. Read `.hyper-team/metadata.json` → use `language` field if file exists
3. Default: `eng`

Produce all user-facing output in the resolved language. Write commit messages in the resolved language.

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
   <feat>: concise subject (max 50 chars)

   1. Primary change
   2. Secondary change
   3. Additional details (if needed)
   ```

   ### Default (Detailed Conventional Commits):
   ```
   <feat>(scope): concise subject (max 50 chars)

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
- Write the subject, What, and Why sections in the resolved language
- Code paths, issue numbers, and technical terms remain in their original form

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
<feat>(auth): implement JWT authentication middleware
<fix>(api): fix null error on user lookup
<refactor>(domain): improve entity structure
```

**Wrong examples (NEVER do this):**
```
feat: subject          ← missing <>
feat(scope): subject   ← missing <>
```

**Get user approval before executing commit — UNLESS `-a` (auto mode) is present.**
