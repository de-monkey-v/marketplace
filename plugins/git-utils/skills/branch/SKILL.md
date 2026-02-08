---
name: branch
description: This skill should be used when the user asks to "브랜치 만들어줘", "create branch", "브랜치 전환", "switch branch", "checkout", "새 브랜치", "브랜치 목록", "list branches", "delete branch", or "브랜치 삭제". Provides branch creation, switching, deletion, and listing with safety checks.
allowed-tools: Bash, Read, AskUserQuestion
---

# Git Branch Skill

Manage branches including creation, switching, deletion, and listing with safety checks.

## Core Workflow

### Step 1: Identify Operation

Determine requested action:
- **List**: Show branches
- **Create**: Make new branch
- **Switch**: Change to branch
- **Delete**: Remove branch

### Step 2: Check Current State

```bash
git branch --show-current    # Current branch
git status -s                # Uncommitted changes
```

**Important**: Warn if uncommitted changes exist before switching.

### Step 3: Execute Operation

Based on operation type:

#### List Branches

```bash
git branch              # Local branches
git branch -a           # All (including remote)
git branch -v           # With last commit info
```

#### Create Branch

```bash
git checkout -b <name>                    # Create and switch
git branch <name>                         # Create only
git checkout -b <name> origin/<remote>    # From remote
```

#### Switch Branch

```bash
git checkout <name>     # Traditional
git switch <name>       # Modern (Git 2.23+)
```

#### Delete Branch

```bash
git branch -d <name>    # Safe delete (merged only)
git branch -D <name>    # Force delete
git push origin --delete <name>   # Remote deletion
```

### Step 4: Report Result

```
=== Branch Operation Complete ===

Action: Created and switched to new branch
Branch: feature/user-auth
Base: main

Current state:
* feature/user-auth (current)
  main
  develop
```

## Branch Naming Conventions

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feature/` | New feature | `feature/user-auth` |
| `fix/` | Bug fix | `fix/login-error` |
| `hotfix/` | Urgent fix | `hotfix/security-patch` |
| `refactor/` | Code restructure | `refactor/api-cleanup` |
| `docs/` | Documentation | `docs/readme-update` |
| `test/` | Test additions | `test/unit-tests` |

## Safety Checks

### Before Switching

If uncommitted changes exist:

```
Warning: Uncommitted changes detected.

Options:
1. Stash changes and switch
2. Commit changes first
3. Cancel operation
```

### Before Deletion

```
Branch 'feature/old' has unmerged commits.

Options:
1. Force delete (-D)
2. Merge first, then delete
3. Cancel
```

### Remote Branch Deletion

Always confirm before deleting remote branches:

```
About to delete remote branch: origin/feature/old

This cannot be undone easily. Proceed? (y/n)
```

## Common Operations

### Create Feature Branch

```bash
git checkout main
git pull origin main
git checkout -b feature/new-feature
```

### Sync with Remote

```bash
git fetch origin
git branch -a    # See all branches
```

### Clean Up Merged Branches

```bash
git branch --merged main | grep -v main | xargs git branch -d
```

## Output Format

```
=== Branch Information ===

Current: feature/my-feature
Default: main

Local branches (3):
* feature/my-feature (current)
  main
  develop

Remote branches (5):
  origin/main
  origin/develop
  origin/feature/other
```

## Related Skills

- `status`: Check branch state
- `log`: View branch history
- `commit`: Commit on current branch
