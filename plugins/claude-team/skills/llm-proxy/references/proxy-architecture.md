# Proxy Architecture Reference

Detailed technical reference for the LLM proxy pattern, including architectural diagrams, implementation protocols, and CLI integration patterns.

## Proxy Pattern Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User / Coordinator                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ SendMessage(team, proxy-member, prompt)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Haiku Proxy Teammate (Thin Wrapper)                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 1. Receive message from inbox                           │   │
│  │ 2. Extract user prompt                                  │   │
│  │ 3. Construct CLI invocation (shell-escaped)             │   │
│  │ 4. Execute: bash -c "external-llm-cli 'prompt'"         │   │
│  │ 5. Capture stdout/stderr                                │   │
│  │ 6. Parse and format result                              │   │
│  │ 7. SendMessage(team, coordinator, result)               │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Bash execution
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External LLM (CLI Tool)                      │
│  • Codex CLI: codex --dangerously-bypass-approvals...          │
│  • Gemini CLI: gemini -p "prompt"                              │
│  • Any CLI that accepts prompt and returns text                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ LLM API call (HTTP/gRPC)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                External LLM Service (GPT-4, Gemini, etc.)       │
└─────────────────────────────────────────────────────────────────┘
```

## Why Pure External LLM Teammates Are Impossible

The Agent Teams protocol requires:
- Reading from `~/.claude/teams/{team}/inboxes/{member}.json`
- Writing to other members' inboxes
- Understanding the message envelope format
- TeamCreate, SendMessage tool availability

**Problem**: External LLMs (GPT-4, Gemini, etc.) are accessed via HTTP APIs or CLI tools. They cannot:
- Access local filesystem directly
- Use Claude CLI's internal tools (SendMessage, TeamCreate, etc.)
- Participate in the tmux-based process management

**Solution**: The Haiku proxy wraps the external LLM, providing the necessary protocol adapter layer while keeping the wrapper logic minimal.

## The Haiku Proxy Solution

**Why Haiku?**
- Cheapest Claude model (~$0.25/MTok input, ~$1.25/MTok output as of 2025)
- Fast response time for simple relay logic
- Sufficient for parsing messages and constructing CLI calls
- Full Agent Teams tool access

**Proxy responsibilities:**
1. Protocol compliance (inbox reading, SendMessage)
2. Message parsing and extraction
3. CLI invocation construction (shell escaping, quoting)
4. Timeout and error handling
5. Output formatting and delivery

**Not proxy responsibilities:**
- Complex reasoning (delegated to external LLM)
- Domain expertise (handled by external LLM)
- Multi-turn conversation state (stateless pattern)

## Message Reception Protocol

The proxy reads messages from:
```
~/.claude/teams/{team-name}/inboxes/{proxy-member-name}.json
```

**Message structure:**
```json
{
  "messages": [
    {
      "from": "coordinator@team-name",
      "to": "codex-proxy@team-name",
      "content": "Translate this Python code to Rust:\n\ndef fibonacci(n):\n    ...",
      "timestamp": "2026-02-16T10:30:00Z"
    }
  ]
}
```

**Extract the content field** and use it as the prompt for the external LLM.

## CLI Invocation Construction

### Simple Single-Line Prompt

```bash
codex --dangerously-bypass-approvals-and-sandbox "What is the capital of France?"
```

### Multi-Line Prompt (Heredoc Pattern)

```bash
codex --dangerously-bypass-approvals-and-sandbox <<'EOF'
Translate this Python code to Rust:

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

Provide idiomatic Rust with error handling.
EOF
```

**Why heredoc?**
- Avoids complex shell escaping
- Preserves newlines and formatting
- More readable for debugging
- Prevents quote-related errors

### Shell Escaping Rules (When Not Using Heredoc)

| Character | Escape As | Example |
|-----------|-----------|---------|
| `"` | `\"` | `"He said \"hello\""` |
| `\` | `\\` | `"Path: C:\\Users"` |
| `$` | `\$` | `"Price: \$100"` |
| `` ` `` | `` \` `` | ``"Command: \`ls\`"`` |
| `!` | `\!` (in `!!`) | `"Last command: \!\!"` |

**Recommendation**: Use heredoc for prompts >100 chars or containing newlines.

## Timeout Handling

Implement timeout to prevent hung CLI processes:

```bash
timeout 60s codex --dangerously-bypass-approvals-and-sandbox <<'EOF'
{prompt}
EOF
```

**Exit code handling:**
- `0` - Success
- `124` - Timeout (killed by timeout command)
- Other - CLI error

## Output Parsing and Formatting

Capture both stdout and stderr:

```bash
output=$(codex ... 2>&1)
exit_code=$?
```

Format response with clear attribution:

```markdown
## Codex Response

{stdout content}

---
*Generated by OpenAI Codex (GPT-4) via proxy teammate*
*Model: gpt-4*
*Timestamp: 2026-02-16T10:30:45Z*
```

## Mixed Teams: Claude-Native + Proxy Members

**Best practices:**

**✅ DO:**
- Use coordinator to route work appropriately
- Let Claude members handle complex reasoning
- Use proxy members for specialized tasks
- Aggregate results at coordinator level
- Handle proxy errors gracefully

**❌ DON'T:**
- Have proxy members communicate directly with each other
- Rely on proxy members for multi-turn conversations
- Use proxy members for tasks requiring tool access
- Assume proxy members have conversation state

**Example workflow:**

```
User: "Review this code and suggest optimizations"

1. Coordinator receives request
2. Coordinator → claude-reviewer: "Review this code for correctness"
3. Coordinator → gpt-proxy: "Review this code for optimization opportunities"
4. Both reviewers respond to coordinator
5. Coordinator synthesizes feedback
6. Coordinator → User: "Comprehensive review from Claude + GPT-4"
```

## See Also

- **`SKILL.md`** - Main skill documentation and quick start
- **`references/prompt-templates.md`** - Ready-to-use system prompts
- **`references/error-handling.md`** - Error scenarios and fallback strategies
- **`examples/codex-translator.md`** - Translation workflow example
