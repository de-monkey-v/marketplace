# Security Best Practices for Hooks

This reference provides comprehensive security guidance for Claude Code plugin hooks.

## Input Validation

Always validate inputs in command hooks:

```bash
#!/bin/bash
set -euo pipefail

input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')

# Validate tool name format
if [[ ! "$tool_name" =~ ^[a-zA-Z0-9_]+$ ]]; then
  echo '{"decision": "deny", "reason": "Invalid tool name"}' >&2
  exit 2
fi
```

### JSON Parsing Safety

```bash
# Safe: Use jq with proper error handling
tool_name=$(echo "$input" | jq -r '.tool_name // empty')
if [[ -z "$tool_name" ]]; then
  echo "Missing tool_name" >&2
  exit 2
fi

# Unsafe: Direct string manipulation
# tool_name=$(echo "$input" | grep -o '"tool_name":"[^"]*"')
```

## Path Safety

Check for path traversal and sensitive files:

```bash
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

# Deny path traversal
if [[ "$file_path" == *".."* ]]; then
  echo '{"decision": "deny", "reason": "Path traversal detected"}' >&2
  exit 2
fi

# Deny sensitive files
if [[ "$file_path" == *".env"* ]] || \
   [[ "$file_path" == *"credentials"* ]] || \
   [[ "$file_path" == *"secrets"* ]]; then
  echo '{"decision": "deny", "reason": "Sensitive file access blocked"}' >&2
  exit 2
fi

# Deny system paths
if [[ "$file_path" == /etc/* ]] || \
   [[ "$file_path" == /usr/* ]] || \
   [[ "$file_path" == /var/* ]]; then
  echo '{"decision": "deny", "reason": "System path access blocked"}' >&2
  exit 2
fi
```

### Sensitive File Patterns

Block these patterns:

```bash
SENSITIVE_PATTERNS=(
  ".env"
  ".env.*"
  "*.pem"
  "*.key"
  "*credentials*"
  "*secrets*"
  "*password*"
  "id_rsa*"
  "*.p12"
  "*.pfx"
)

for pattern in "${SENSITIVE_PATTERNS[@]}"; do
  if [[ "$file_path" == $pattern ]]; then
    echo '{"decision": "deny", "reason": "Sensitive file pattern"}' >&2
    exit 2
  fi
done
```

## Variable Quoting

Always quote variables to prevent injection:

```bash
# GOOD: Quoted variables
echo "$file_path"
cd "$CLAUDE_PROJECT_DIR"
test -f "$file_path" && cat "$file_path"

# BAD: Unquoted variables (injection risk)
echo $file_path
cd $CLAUDE_PROJECT_DIR
test -f $file_path && cat $file_path
```

### Why Quoting Matters

```bash
# If file_path contains spaces or special chars:
file_path="/path/with spaces/file.txt"

# Unquoted: splits into multiple arguments
cat $file_path  # Tries: cat /path/with spaces/file.txt
                # Becomes: cat /path/with spaces/file.txt (3 args)

# Quoted: treated as single argument
cat "$file_path"  # Correctly: cat "/path/with spaces/file.txt"
```

## Command Injection Prevention

### Dangerous Patterns

```bash
# DANGEROUS: Direct command substitution
command=$(echo "$input" | jq -r '.tool_input.command')
eval "$command"  # Never do this!

# DANGEROUS: Unquoted in command
bash -c "process $file_path"  # Injection possible

# SAFE: Use arrays and proper quoting
args=("$file_path")
process "${args[@]}"
```

### Safe Subprocess Execution

```bash
# Safe: Explicit arguments, no shell expansion
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate.py" "$file_path"

# Safe: Use -- to separate options from arguments
grep -- "$pattern" "$file_path"

# Unsafe: Shell interpretation
bash -c "grep $pattern $file_path"
```

## Timeout Configuration

Set appropriate timeouts to prevent hanging:

```json
{
  "type": "command",
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh",
  "timeout": 10
}
```

### Default Timeouts

| Hook Type | Default | Recommended Max |
|-----------|---------|-----------------|
| Command hooks | 60s | 30s |
| Prompt hooks | 30s | 30s |

### Handling Long Operations

```bash
#!/bin/bash
set -euo pipefail

# Set internal timeout
timeout 5 expensive_operation || {
  echo '{"continue": true, "systemMessage": "Validation timed out, skipping"}'
  exit 0
}
```

## Environment Variable Safety

### Don't Log Sensitive Data

```bash
# BAD: Logs all environment
env > /tmp/debug.log

# BAD: Logs potentially sensitive vars
echo "API_KEY=$API_KEY" >> /tmp/debug.log

# GOOD: Log only safe information
echo "CLAUDE_PROJECT_DIR=$CLAUDE_PROJECT_DIR" >> /tmp/debug.log
```

### Use Environment Variables Safely

```bash
# Safe: Reference but don't echo sensitive vars
if [[ -z "${API_KEY:-}" ]]; then
  echo "API_KEY not set" >&2
  exit 2
fi

# Use in command without echoing
curl -H "Authorization: Bearer $API_KEY" "$url" > /dev/null
```

## Output Safety

### Sanitize Output

```bash
# Sanitize output before returning
sanitize_output() {
  local output="$1"
  # Remove potential control characters
  echo "$output" | tr -d '\000-\011\013-\037'
}

result=$(sanitize_output "$raw_result")
```

### Return Valid JSON

```bash
# Always return valid JSON
output_json() {
  local decision="$1"
  local reason="$2"
  # Use jq to ensure valid JSON
  jq -n --arg d "$decision" --arg r "$reason" \
    '{"decision": $d, "reason": $r}'
}

output_json "deny" "Path traversal detected"
```

## File System Safety

### Safe Temporary Files

```bash
# Use mktemp for temporary files
TEMP_FILE=$(mktemp)
trap "rm -f $TEMP_FILE" EXIT

# Process in temp file
echo "$input" > "$TEMP_FILE"
```

### Check File Ownership

```bash
# Verify file is in expected location
real_path=$(realpath "$file_path")
if [[ "$real_path" != "$CLAUDE_PROJECT_DIR"/* ]]; then
  echo '{"decision": "deny", "reason": "File outside project directory"}' >&2
  exit 2
fi
```

## Bash Safety Settings

Always start hook scripts with:

```bash
#!/bin/bash
set -euo pipefail

# -e: Exit on error
# -u: Error on undefined variables
# -o pipefail: Fail on pipe errors
```

### Error Handling

```bash
#!/bin/bash
set -euo pipefail

# Trap errors
trap 'echo "{\"continue\": true, \"systemMessage\": \"Hook error: $?\"}"' ERR

# Your hook logic here
```

## Checklist

Before deploying a hook:

- [ ] All variables quoted
- [ ] Input validated before use
- [ ] Path traversal checked
- [ ] Sensitive files blocked
- [ ] Appropriate timeout set
- [ ] No command injection vulnerabilities
- [ ] No sensitive data in logs
- [ ] Valid JSON output
- [ ] Error handling in place
- [ ] `set -euo pipefail` at start
