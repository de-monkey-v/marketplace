---
name: diff
description: This skill should be used when the user asks to "변경 내용 보여줘", "diff 보여줘", "show diff", "what changed", "뭐가 바뀌었어", "수정된 내용", "compare changes", "staged changes", or "unstaged changes". Analyzes and displays detailed change information with clear distinction between staged and unstaged modifications.
allowed-tools: Bash, Read
---

# Git Diff Skill

Analyze and display detailed change information with clear distinction between staged and unstaged modifications.

## Core Workflow

### Step 1: Determine Diff Scope

Based on user request, select appropriate command:

| Request | Command |
|---------|---------|
| Unstaged changes | `git diff` |
| Staged changes | `git diff --cached` |
| All changes | `git diff HEAD` |
| Specific file | `git diff <file>` |
| Branch comparison | `git diff branch1..branch2` |

### Step 2: Get Change Statistics

```bash
git diff --stat           # File change summary
git diff --shortstat      # Line count only
```

Output format:
```
 src/api/user.ts    | 25 +++++++----
 src/types/user.ts  | 10 +++++
 2 files changed, 28 insertions(+), 7 deletions(-)
```

### Step 3: Analyze Changes

For each changed file, identify:
- Lines added (+) and removed (-)
- Nature of change (logic, formatting, comments)
- Impact on functionality

### Step 4: Present Summary

```
=== Change Analysis ===

Total: 3 files, +45 lines, -12 lines

Staged (ready to commit):
  src/api/user.ts    | +20 -5  | API endpoint additions
  src/types/user.ts  | +10 -0  | Type definitions

Unstaged (not staged yet):
  src/utils/helper.ts | +15 -7 | Helper function updates

Summary: User-related feature additions
```

## Diff Commands Reference

### Basic Comparisons

```bash
# Working directory vs index
git diff

# Index vs last commit
git diff --cached
git diff --staged    # Same as --cached

# Working directory vs last commit
git diff HEAD

# Between commits
git diff abc123..def456
```

### Branch Comparisons

```bash
# Compare two branches
git diff main..feature/branch

# Changes since branch diverged
git diff main...feature/branch

# Only file names
git diff --name-only main..feature
```

### Output Options

```bash
# Statistics only
git diff --stat

# Word-level diff
git diff --word-diff

# Ignore whitespace
git diff -w

# Color output
git diff --color
```

## Interpreting Diff Output

### Line Markers

| Marker | Meaning |
|--------|---------|
| `+` | Line added |
| `-` | Line removed |
| ` ` | Unchanged context |
| `@@` | Chunk header |

### Chunk Header

```
@@ -10,5 +10,7 @@
```
- `-10,5`: Old file, starting line 10, 5 lines
- `+10,7`: New file, starting line 10, 7 lines

## Common Use Cases

### Review Before Commit

```bash
git diff --cached    # What will be committed
git diff             # What won't be committed yet
```

### Compare with Remote

```bash
git diff origin/main..HEAD    # Local changes not pushed
```

### Check Specific File

```bash
git diff -- path/to/file.ts
git diff HEAD~3 -- path/to/file.ts   # Last 3 commits
```

## Related Skills

- `status`: Quick overview of changed files
- `commit`: Commit after reviewing changes
- `log`: View commit history with diffs
