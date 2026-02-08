# git-utils

Git workflow automation plugin - commit, branch, status check, and more.

## Installation

```bash
/plugin install git-utils@de-monkey-v-marketplace
```

## Usage

### Natural Language Requests (Auto Skill Activation)

```
"커밋해줘"
"변경사항 뭐 있어?"
"commit my changes"
"show me the branch list"
"recent commit history"
```

### Commands (Explicit Execution)

```bash
/git-utils:commit              # Start commit workflow
/git-utils:commit "message"    # Commit with specified message
```

## Components

### Commands

| Command | Description |
|---------|-------------|
| `/git-utils:commit` | Analyze changes, generate commit message, execute commit |

### Skills

| Skill | Description | Triggers |
|-------|-------------|----------|
| commit | Generate commit message and commit | "커밋해줘", "commit changes" |
| status | Check repository status | "상태 확인", "git status" |
| diff | Analyze changes | "변경 내용", "what changed" |
| branch | Branch management | "브랜치 만들어줘", "switch branch" |
| log | View commit history | "커밋 기록", "commit history" |

## Commit Skill Details

**Key Features**:
- Analyze Git changes (git status, git diff)
- Learn project style from commit history analysis
- Follow CONTRIBUTING.md conventions (`<type>:` format)
- Auto-detect files containing sensitive information
- Selective file staging

**Commit Types**:

| Type | When to Use |
|------|-------------|
| `<feat>` | New feature |
| `<fix>` | Bug fix |
| `<refactor>` | Code restructure |
| `<docs>` | Documentation changes |
| `<test>` | Add/modify tests |
| `<style>` | Code formatting |
| `<perf>` | Performance improvement |
| `<chore>` | Miscellaneous tasks |

**Important**: Never include signatures like `generated with [Claude Code]`.

## Keywords

git, commit, branch, status, diff, log, version-control, automation

> This plugin respects the language setting in `.hyper-team/metadata.json`. Run `/hyper-team:setup` to configure.
