# Security and Best Practices Reference

Security considerations, API key management, input sanitization, and guidance on when NOT to use the proxy pattern.

## --dangerously-bypass-approvals-and-sandbox Implications

**What this flag does:**
- Bypasses user approval for tool use
- Disables sandboxing for bash execution
- Allows automated, unattended execution

**Security risks:**
1. **Code execution without review** - External LLM output executed directly
2. **Prompt injection** - User input passed to external LLM could be malicious
3. **Data exfiltration** - External LLM sees all prompt content
4. **API abuse** - Malicious prompts could trigger expensive API calls

**Mitigation strategies:**

```bash
# 1. Input validation (before sending to proxy)
if echo "$prompt" | grep -E "(rm -rf|sudo|eval)" > /dev/null; then
  echo "Error: Potentially dangerous command in prompt"
  exit 1
fi

# 2. Output sanitization (after receiving from external LLM)
# Review external LLM response before execution

# 3. Rate limiting
# Track API calls, enforce daily/hourly limits

# 4. Audit logging
echo "$(date): Codex proxy called with prompt: $prompt" >> /var/log/llm-proxy.log
```

## API Key Management

**Best practices:**

**✅ DO:**
- Store API keys in environment variables
- Use `.env` files (not committed to git)
- Rotate keys regularly
- Use separate keys for dev/prod
- Monitor API usage for anomalies

**❌ DON'T:**
- Hard-code API keys in prompts or scripts
- Commit API keys to version control
- Share API keys across team members
- Use production keys for testing

**Secure setup:**

```bash
# .env file (add to .gitignore)
OPENAI_API_KEY="sk-..."
GEMINI_API_KEY="..."

# Load in shell
source .env

# Verify (should show key prefix)
echo $OPENAI_API_KEY | head -c 10

# Proxy teammate reads from environment
# No keys in config.json or prompts
```

## Input Sanitization

**Threat model**: User provides malicious input that exploits:
1. Shell command injection
2. Prompt injection in external LLM
3. Resource exhaustion

**Sanitization strategies:**

**1. Shell command injection prevention:**
```bash
# BAD - vulnerable to injection
codex "$user_input"

# GOOD - use heredoc to avoid shell interpretation
codex <<'EOF'
$user_input
EOF
```

**2. Prompt injection detection:**
```python
dangerous_patterns = [
    r"ignore previous instructions",
    r"system prompt",
    r"you are now",
    r"disregard.*above",
]

for pattern in dangerous_patterns:
    if re.search(pattern, user_input, re.IGNORECASE):
        warn("Potential prompt injection detected")
```

**3. Size limits:**
```bash
max_prompt_size=50000  # characters
if [ ${#prompt} -gt $max_prompt_size ]; then
  echo "Error: Prompt exceeds size limit"
  exit 1
fi
```

## When NOT to Use Proxy Pattern

**Avoid proxy pattern when:**

1. **Task requires tool use** - External LLMs cannot use Agent Teams tools
   ```
   ❌ "Use the Grep tool to search for patterns"
   ✅ Have Claude member use tools, send results to external LLM for analysis
   ```

2. **Multi-turn conversation needed** - Proxy teammates are stateless
   ```
   ❌ User: "Review this code" → GPT: "Found issues" → User: "Fix them"
   ✅ Include all context in each message
   ```

3. **Real-time collaboration** - Latency of external API calls
   ```
   ❌ Interactive pair programming
   ✅ Batch code review
   ```

4. **Sensitive data** - External LLM APIs see all prompt content
   ```
   ❌ Private customer data, API keys, credentials
   ✅ Public code, general knowledge queries
   ```

5. **Cost-insensitive, quality-critical** - Claude Opus may be superior
   ```
   ❌ Production system architecture design
   ✅ Quick code snippet generation
   ```

## See Also

- **`SKILL.md`** - Main skill documentation
- **`references/error-handling.md`** - Error scenarios and fallback strategies
- **`references/provider-catalog.md`** - Provider-specific API key setup
