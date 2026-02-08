# hyper-team

Agent Teams workflow helper for Claude Code. Helps you set up, generate team prompts, and verify implementations using Claude Code's experimental Agent Teams feature.

## Prerequisites

- Claude Code CLI
- tmux (for split-pane teammate display)

## Commands

### `/hyper-team:setup`

Configure your environment for Agent Teams:
- Checks and installs tmux
- Adds `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` to settings.json
- Configures teammate display mode (tmux/in-process/auto)

### `/hyper-team:make-prompt`

Generate a copy-paste-ready team prompt from your requirements:

```bash
/hyper-team:make-prompt Add user authentication with JWT
```

What it does:
1. Analyzes your project structure and tech stack
2. Researches best practices via web search
3. Creates a detailed spec at `.hyper-team/todos/NNN-subject.md`
4. Generates a team prompt starting with "Create a team."
5. You copy-paste the prompt into a new session

### `/hyper-team:verify`

Verify implementation against a todo spec:

```bash
/hyper-team:verify 001
/hyper-team:verify 001-user-auth
```

Generates a team verification prompt that:
- Runs tests and checks acceptance criteria
- Analyzes code quality (readability, maintainability, security, performance)
- Checks git status and integration
- Provides a score out of 100

## Workflow

```
1. /hyper-team:setup          # One-time setup
2. /hyper-team:make-prompt    # Describe what you want
3. Copy prompt → New session  # Team builds it
4. /hyper-team:verify NNN     # Verify the result
```

## Language Configuration

Set your preferred language during `/hyper-team:setup`, or manually edit:

```json
// .hyper-team/metadata.json
{ "language": "eng" }  // or "kor"
```

All plugins in the marketplace respect this setting. The `--language` argument overrides it per-command.

## Todo File Structure

Todo files are stored in `.hyper-team/todos/`:
- `001-subject.md` - Active task
- `001-subject-complete.md` - Completed task
