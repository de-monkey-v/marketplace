# Plugin Settings Security Guide

Security best practices for handling plugin settings and user configuration.

## Sanitize User Input

When writing settings files from user input:

```bash
# Escape quotes in user input
SAFE_VALUE=$(echo "$USER_INPUT" | sed 's/"/\\"/g')

# Write to file
cat > "$STATE_FILE" <<EOF
---
user_setting: "$SAFE_VALUE"
---
EOF
```

**Why it matters:** Unsanitized input can:
- Break YAML parsing
- Enable command injection in hook scripts
- Corrupt settings files

## Validate File Paths

If settings contain file paths:

```bash
FILE_PATH=$(echo "$FRONTMATTER" | grep '^data_file:' | sed 's/data_file: *//')

# Check for path traversal
if [[ "$FILE_PATH" == *".."* ]]; then
  echo "Invalid path in settings (path traversal)" >&2
  exit 2
fi

# Verify path is within expected directory
REAL_PATH=$(realpath -m "$FILE_PATH")
if [[ ! "$REAL_PATH" == "$PROJECT_ROOT"* ]]; then
  echo "Path escapes project directory" >&2
  exit 2
fi
```

## Permissions

Settings files should be:
- **Readable by user only** (`chmod 600`)
- **Not committed to git** (add to `.gitignore`)
- **Not shared between users** (per-project, per-user)

```bash
# Set restrictive permissions when creating settings
umask 077
cat > "$STATE_FILE" <<EOF
---
enabled: true
---
EOF
```

## Gitignore Requirements

Always add to `.gitignore`:

```gitignore
# Plugin settings (user-local, may contain sensitive data)
.claude/*.local.md
.claude/*.local.json

# Credentials (never commit)
.env
.env.local
**/secrets/**
```

Document this requirement in plugin README.

## Sensitive Data Handling

**Never store in settings files:**
- API keys or tokens
- Passwords or credentials
- Private keys

**Instead:**
- Use environment variables
- Reference credential storage systems
- Use secure credential managers

```markdown
---
# Good: Reference to env var
api_key_env: MY_PLUGIN_API_KEY

# Bad: Actual key value
api_key: sk-abc123...
---
```

## Validation Checklist

Before reading settings:
1. [ ] Verify file exists
2. [ ] Validate file permissions
3. [ ] Parse YAML safely (handle malformed input)
4. [ ] Validate field types and ranges
5. [ ] Sanitize paths before use

```bash
# Complete validation pattern
validate_settings() {
  local file="$1"

  # 1. Check existence
  [[ ! -f "$file" ]] && return 1

  # 2. Check permissions (warn if too open)
  perms=$(stat -c %a "$file" 2>/dev/null || stat -f %Lp "$file")
  [[ "$perms" != "600" ]] && echo "Warning: $file has loose permissions" >&2

  # 3. Validate YAML structure
  if ! grep -q '^---$' "$file"; then
    echo "Error: Missing YAML frontmatter" >&2
    return 2
  fi

  return 0
}
```

## Security Audit Checklist

For plugins using settings:

- [ ] Settings files excluded from git
- [ ] No credentials stored in settings
- [ ] Input sanitization implemented
- [ ] Path traversal prevention
- [ ] Appropriate file permissions
- [ ] Documented security requirements
