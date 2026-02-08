---
name: status
description: This skill should be used when the user asks to "상태 확인", "git status", "check status", "뭐 바뀌었어", "스테이징 확인", "repo status", "staged files", "untracked files", or "what's changed". Check repository state and summarize changes with clear classification of staged, unstaged, and untracked files.
allowed-tools: Bash, Read
---

# Git Status Skill

Check repository state and summarize changes with clear classification of staged, unstaged, and untracked files.

## Core Workflow

### Step 1: Gather Status Information

Run these commands:

```bash
git status              # Full status
git status -sb          # Short format with branch
git branch --show-current
```

### Step 2: Classify Changes

Categorize files into:

| Status | Description | Indicator |
|--------|-------------|-----------|
| Staged | Ready to commit | `A`, `M`, `D` (index) |
| Modified | Changed but not staged | `M` (working tree) |
| Untracked | Not tracked by git | `??` |
| Deleted | Removed files | `D` |

### Step 3: Check Remote Status

Determine relationship with remote:

```bash
git status -sb   # Shows ahead/behind count
```

Possible states:
- `[ahead N]` - Local has N commits not pushed
- `[behind N]` - Remote has N commits not pulled
- `[ahead N, behind M]` - Diverged branches

### Step 4: Present Summary

Format output clearly:

```
=== Git Status ===

Branch: feature/my-branch
Remote: origin/feature/my-branch (2 commits ahead)

Staged (ready to commit):
  - src/file1.ts (modified)
  - src/file2.ts (new file)

Modified (not staged):
  - src/file3.ts

Untracked:
  - temp.log
  - .env.local

Summary: 2 staged, 1 modified, 2 untracked
```

## Status Indicators Quick Reference

| Short | Long | Meaning |
|-------|------|---------|
| `M ` | modified (staged) | File modified and staged |
| ` M` | modified (unstaged) | File modified but not staged |
| `A ` | added | New file staged |
| `D ` | deleted | File deleted and staged |
| ` D` | deleted (unstaged) | File deleted but not staged |
| `??` | untracked | File not tracked |
| `!!` | ignored | File ignored by .gitignore |

## Common Scenarios

### Clean Working Directory

```
On branch main
nothing to commit, working tree clean
```

### Ready to Commit

```
Changes to be committed:
  - All staged files listed
```

### Uncommitted Changes

```
Changes not staged for commit:
  - Modified files need staging
```

## Related Skills

- `diff`: View detailed changes
- `commit`: Commit staged changes
- `branch`: Check branch information
