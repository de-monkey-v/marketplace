# Error Handling and Limitations Reference

Comprehensive error handling patterns, fallback strategies, and known limitations of the LLM proxy pattern.

## Error Scenarios

### CLI Not Found / API Key Missing

**Detection:**
```bash
which codex || echo "CLI not found"
echo $OPENAI_API_KEY || echo "API key not set"
```

**Error message template:**
```markdown
## {Provider} Configuration Error

**Issue**: {CLI tool} not found in PATH

**Required setup:**
1. Install {CLI tool}: {installation-command}
2. Verify installation: `which {cli-tool}`
3. Set API key: `export {ENV_VAR}="..."`
4. Test: `{cli-tool} "test prompt"`

**Current environment:**
- PATH: {$PATH}
- {ENV_VAR}: {set/unset}
```

### CLI Timeout

**Scenario**: External LLM takes >60s to respond.

**Handling:**
```bash
timeout 60s codex "prompt" || {
  exit_code=$?
  if [ $exit_code -eq 124 ]; then
    echo "Timeout after 60s"
  fi
}
```

**User-facing message:**
```markdown
## Request Timeout

The {Provider} CLI did not respond within 60 seconds.

**Possible causes:**
- Prompt too long (exceeds context window)
- API rate limiting
- Network connectivity issues
- Service outage

**Recommended actions:**
1. Check {Provider} status page
2. Simplify the prompt
3. Retry after 1-2 minutes
4. Contact {Provider} support if persistent
```

### Output Truncation

**Scenario**: External LLM response exceeds reasonable size.

**Detection:**
```bash
output=$(codex "prompt")
length=${#output}
if [ $length -gt 50000 ]; then
  echo "Warning: Large response ($length chars)"
fi
```

**Handling:**
- Warn user about large response
- Optionally truncate with summary
- Suggest breaking prompt into smaller chunks

### Non-Zero Exit Codes

**Common exit codes:**
- `1` - General error
- `2` - Misuse of shell command
- `126` - Command not executable
- `127` - Command not found
- `130` - Terminated by Ctrl+C
- `124` - Timeout

**Categorized handling:**
```bash
case $exit_code in
  0)   # Success
    ;;
  124) # Timeout
    report_timeout
    ;;
  127) # Command not found
    report_missing_cli
    ;;
  *)   # Other error
    report_generic_error $exit_code "$stderr"
    ;;
esac
```

## Fallback Strategies

**1. Retry with exponential backoff:**
```bash
max_retries=3
retry_count=0
while [ $retry_count -lt $max_retries ]; do
  output=$(codex "prompt" 2>&1)
  exit_code=$?
  if [ $exit_code -eq 0 ]; then
    break
  fi
  sleep $((2 ** retry_count))
  ((retry_count++))
done
```

**2. Fallback to alternative model:**
```
If Codex fails → Try Gemini
If all fail → Report error to coordinator
```

**3. Graceful degradation:**
```markdown
## Partial Response

{Provider} encountered an error but provided partial output:

{partial-output}

**Error details:**
{error-message}

Please review the partial result and re-submit if needed.
```

## Limitations

### Stateless, No Streaming, Single-Turn

**Stateless:**
- Each message is independent
- No conversation history
- Coordinator must include all context in each prompt

**No streaming:**
- External LLMs typically return complete response
- Cannot stream partial results to user
- Latency until first token is full API call time

**Single-turn:**
- One prompt → one response
- No back-and-forth refinement
- Multi-turn conversations must be orchestrated by coordinator

**Workaround (coordinator manages state):**
```
User: "Translate this code to Rust"
Coordinator → Codex proxy: "Translate: {code}"
Codex proxy → Coordinator: {rust_code}

User: "Now optimize it"
Coordinator → Codex proxy: "Optimize this Rust code: {rust_code}"
# Coordinator included previous result in new prompt
```

### External LLMs Cannot Use Agent Teams Tools

**Tools unavailable to external LLMs:**
- SendMessage (must go through proxy)
- TeamCreate (not applicable)
- Grep, Read, Write (filesystem access)
- LSP (code intelligence)
- Custom plugin tools

**Workaround:**
```
# Instead of:
User → GPT: "Read main.py and suggest improvements"
# (GPT cannot use Read tool)

# Do this:
User → Coordinator: "Review main.py"
Coordinator: Read(main.py) → {content}
Coordinator → GPT proxy: "Review this code: {content}"
GPT proxy → Coordinator: {feedback}
Coordinator → User: {feedback}
```

### Context Window Limits

**Limits by model:**
- GPT-4: 8K, 32K, 128K (varies by version)
- Gemini Pro: 32K
- Claude: 100K (Haiku/Sonnet), 200K (Opus)

**Mitigation:**
```
# Chunking strategy
If file >30K tokens:
  1. Split into logical sections
  2. Send to external LLM separately
  3. Coordinator aggregates results

# Summarization strategy
If codebase too large:
  1. Claude Sonnet reads and summarizes
  2. Send summary to external LLM
  3. External LLM provides high-level feedback
```

### Performance Characteristics

**Latency:**
- Proxy overhead: ~0.5-1s (Haiku wrapper)
- External LLM API: 2-30s (depends on model)
- Total: 3-31s per request

**Cost:**
- Haiku wrapper: ~$0.0001 per request (negligible)
- External LLM: varies ($0.001-$0.10+ per request)

**Reliability:**
- Depends on external API uptime
- Network connectivity required
- Rate limiting may apply

## See Also

- **`SKILL.md`** - Main skill documentation
- **`references/security-best-practices.md`** - Security considerations
- **`references/provider-catalog.md`** - Provider-specific troubleshooting
