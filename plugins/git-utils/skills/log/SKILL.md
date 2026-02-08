---
name: log
description: This skill should be used when the user asks to "커밋 기록", "commit history", "히스토리", "git log", "로그 보여줘", "최근 커밋", "recent commits", "show commits", "who changed", or "커밋 검색". View and analyze commit history with various formats, filters, and search options.
allowed-tools: Bash, Read
---

# Git Log Skill

View and analyze commit history with various formats, filters, and search options.

## Core Workflow

### Step 1: Determine Query Type

Identify what user wants:
- Recent commits overview
- Specific author's commits
- Commits mentioning keyword
- File change history
- Branch comparison

### Step 2: Select Appropriate Command

| Query | Command |
|-------|---------|
| Recent commits | `git log --oneline -10` |
| Detailed view | `git log -5` |
| Graph view | `git log --oneline --graph --all -20` |
| By author | `git log --author="name" -10` |
| By message | `git log --grep="keyword" -10` |
| For file | `git log --follow -- <file>` |

### Step 3: Format Output

Present in clear, readable format:

```
=== Commit History ===

Recent 5 commits:

1. a1b2c3d (2 hours ago) - John Doe
   <feat>: Add user authentication API

2. d4e5f6g (1 day ago) - Jane Smith
   <fix>: Resolve login bug

3. h7i8j9k (2 days ago) - John Doe
   <refactor>: Improve API structure

4. l0m1n2o (3 days ago) - Jane Smith
   <docs>: Update README

5. p3q4r5s (1 week ago) - John Doe
   <feat>: Initial project setup
```

## Log Format Options

### Compact Formats

```bash
# One line per commit
git log --oneline -10

# Custom format
git log --pretty=format:"%h %an %ar %s" -10

# With date
git log --date=short --pretty=format:"%ad %h %s" -10
```

### Detailed Formats

```bash
# Full details
git log -5

# With stats
git log --stat -5

# With diff
git log -p -3
```

### Visual Formats

```bash
# ASCII graph
git log --oneline --graph --all -20

# Decorated (branch names)
git log --oneline --decorate -10
```

## Filtering Options

### By Author

```bash
git log --author="John" -10
git log --author="john@email.com" -10
```

### By Date

```bash
git log --since="2024-01-01"
git log --until="2024-12-31"
git log --since="1 week ago"
git log --after="yesterday"
```

### By Message

```bash
git log --grep="fix" -10
git log --grep="API" --grep="auth" --all-match -10
```

### By File

```bash
git log -- path/to/file.ts
git log --follow -- path/to/file.ts    # Follow renames
```

### By Change Content

```bash
git log -S "function_name"    # Code added/removed
git log -G "regex_pattern"    # Regex match
```

## Branch Comparison

```bash
# Commits in feature not in main
git log main..feature/branch --oneline

# Commits not pushed
git log origin/main..HEAD --oneline

# Commits from merge base
git log main...feature/branch --oneline
```

## Useful Options Reference

| Option | Description |
|--------|-------------|
| `--oneline` | One line summary |
| `--graph` | ASCII branch graph |
| `--all` | All branches |
| `--stat` | File change stats |
| `-p` | Show diffs |
| `--follow` | Track file renames |
| `-n` | Limit to n commits |
| `--author` | Filter by author |
| `--grep` | Filter by message |
| `--since/--until` | Filter by date |

## Common Use Cases

### Morning Check

```bash
git log --since="yesterday" --oneline
```

### Review Team Activity

```bash
git log --since="1 week ago" --pretty=format:"%h %an: %s" | head -20
```

### Find When Feature Added

```bash
git log --grep="feature-name" --oneline
```

### Trace File History

```bash
git log --follow -p -- path/to/file.ts
```

## Related Skills

- `diff`: View specific commit changes
- `branch`: Compare branch histories
- `status`: Current repository state
