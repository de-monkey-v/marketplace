# Script Security Guidelines

## Secret Management

### Never Hardcode Secrets

```bash
# WRONG - hardcoded API key
API_KEY="sk-abc123..."
curl -H "Authorization: Bearer $API_KEY" "$URL"

# CORRECT - use environment variable
: "${API_KEY:?API_KEY environment variable is required}"
curl -H "Authorization: Bearer $API_KEY" "$URL"
```

```python
# WRONG
API_KEY = "sk-abc123..."

# CORRECT
api_key = os.environ.get("API_KEY")
if not api_key:
    print("ERROR: API_KEY required", file=sys.stderr)
    sys.exit(1)
```

### Secret Detection Patterns

Check for these patterns in scripts:
- Strings matching `(sk|api|key|token|secret|password)[-_]?[a-zA-Z0-9]{16,}`
- Base64-encoded credentials
- Hardcoded URLs with credentials (`https://user:pass@host`)

## Command Injection Prevention

### Bash

```bash
# WRONG - user input directly in command
eval "$USER_INPUT"
bash -c "$USER_INPUT"

# WRONG - unquoted variable expansion
grep $PATTERN $FILE

# CORRECT - always quote variables
grep -- "$PATTERN" "$FILE"

# CORRECT - use arrays for commands
cmd=("grep" "-r" "--" "$PATTERN" "$DIR")
"${cmd[@]}"
```

### Python

```python
# WRONG - shell=True with user input
subprocess.run(f"grep {pattern} {file}", shell=True)

# CORRECT - list arguments, no shell
subprocess.run(["grep", "-r", "--", pattern, file], check=True)

# WRONG - string formatting in SQL/commands
query = f"SELECT * FROM users WHERE name = '{name}'"

# CORRECT - parameterized queries
cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
```

## Input Validation

### Bash

```bash
# Validate expected format
if [[ ! "$COUNT" =~ ^[0-9]+$ ]]; then
  die "COUNT must be a number"
fi

# Validate file path (no traversal)
if [[ "$FILE_PATH" == *".."* ]]; then
  die "Path traversal not allowed"
fi

# Validate allowed values
case "$FORMAT" in
  json|text|csv) ;; # valid
  *) die "Invalid format: $FORMAT" ;;
esac
```

### Python

```python
# Validate numeric input
try:
    count = int(args.count)
    if count < 1 or count > 1000:
        raise ValueError("Count must be 1-1000")
except ValueError as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)

# Validate path safety
import os
def validate_path(path, allowed_base):
    resolved = os.path.realpath(path)
    if not resolved.startswith(os.path.realpath(allowed_base)):
        raise ValueError(f"Path outside allowed directory: {path}")
    return resolved
```

## Variable Quoting (Bash)

```bash
# ALWAYS quote variables - prevents word splitting and globbing
echo "$MESSAGE"          # not: echo $MESSAGE
FILE_PATH="$DIR/$NAME"  # not: FILE_PATH=$DIR/$NAME
[[ -f "$FILE" ]]        # not: [ -f $FILE ]

# Quote in command substitution
RESULT="$(some_command "$ARG")"

# Quote array elements
for item in "${ITEMS[@]}"; do
  process "$item"
done
```

## Temporary File Safety

### Bash

```bash
# WRONG - predictable temp file
TMPFILE="/tmp/myapp_output"

# CORRECT - mktemp with cleanup
TMPFILE=$(mktemp)
trap 'rm -f "$TMPFILE"' EXIT

# CORRECT - temp directory
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT
```

### Python

```python
# WRONG - predictable path
tmpfile = "/tmp/myapp_output"

# CORRECT - tempfile module
import tempfile
with tempfile.NamedTemporaryFile(delete=True) as f:
    f.write(data)
    f.flush()
    process(f.name)
```

## Python subprocess Safety

```python
# WRONG - shell=True allows injection
subprocess.run(f"ls {directory}", shell=True)

# CORRECT - list args, no shell interpretation
subprocess.run(["ls", directory])

# If shell features are absolutely needed, validate input first
import shlex
# Only for trusted, validated input
subprocess.run(shlex.split(f"command --arg {shlex.quote(user_input)}"))
```

## Checklist

- [ ] No hardcoded secrets (API keys, tokens, passwords)
- [ ] All variables quoted in Bash (`"$var"`)
- [ ] No `eval` or `bash -c` with untrusted input
- [ ] No `shell=True` in Python subprocess with untrusted input
- [ ] Input validated before use (type, range, format)
- [ ] File paths checked for traversal (`..`)
- [ ] Temporary files use `mktemp` / `tempfile`
- [ ] Sensitive data not logged to stdout/stderr
- [ ] `set -euo pipefail` in Bash scripts
- [ ] Error messages don't leak sensitive information
