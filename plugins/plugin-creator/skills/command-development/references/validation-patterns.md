# Validation Patterns for Commands

This reference provides detailed validation patterns for Claude Code slash commands.

## Argument Validation

Commands should validate inputs before processing.

### Basic Argument Check

```markdown
---
description: Deploy with validation
argument-hint: [environment]
---

Validate environment: !\`echo "$1" | grep -E "^(dev|staging|prod)$" || echo "INVALID"\`

If $1 is valid environment:
  Deploy to $1
Otherwise:
  Explain valid environments: dev, staging, prod
  Show usage: /deploy [environment]
```

### File Existence Checks

```markdown
---
description: Process configuration
argument-hint: [config-file]
---

Check file exists: !\`test -f $1 && echo "EXISTS" || echo "MISSING"\`

If file exists:
  Process configuration: @$1
Otherwise:
  Explain where to place config file
  Show expected format
  Provide example configuration
```

### Plugin Resource Validation

```markdown
---
description: Run plugin analyzer
allowed-tools: Bash(test:*)
---

Validate plugin setup:
- Script: !\`test -x ${CLAUDE_PLUGIN_ROOT}/bin/analyze && echo "✓" || echo "✗"\`
- Config: !\`test -f ${CLAUDE_PLUGIN_ROOT}/config.json && echo "✓" || echo "✗"\`

If all checks pass, run analysis.
Otherwise, report missing components.
```

## Error Handling

### Build with Error Handling

```markdown
---
description: Build with error handling
allowed-tools: Bash(*)
---

Execute build: !\`bash ${CLAUDE_PLUGIN_ROOT}/scripts/build.sh 2>&1 || echo "BUILD_FAILED"\`

If build succeeded:
  Report success and output location
If build failed:
  Analyze error output
  Suggest likely causes
  Provide troubleshooting steps
```

### Graceful Degradation

```markdown
---
description: Analyze with fallback
allowed-tools: Read, Bash
---

Try primary analysis: !\`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/analyze.py 2>&1\`

If analysis succeeded:
  Present results
If python not available:
  Fall back to manual analysis
  Use Read tool to examine files
  Provide basic findings
```

## Conditional Logic

### If-Then-Else Pattern

```markdown
---
argument-hint: [pr-number]
---

$IF($1,
  Review PR #$1,
  Please provide a PR number. Usage: /review-pr [number]
)
```

### Multi-Condition Validation

```markdown
---
description: Deploy to environment
argument-hint: [env] [version]
---

# Validation checks
Env check: !\`echo "$1" | grep -E "^(staging|production)$" || echo "INVALID_ENV"\`
Version check: !\`echo "$2" | grep -E "^v[0-9]+\.[0-9]+\.[0-9]+$" || echo "INVALID_VERSION"\`

If both valid:
  Deploy $2 to $1
If env invalid:
  Valid environments: staging, production
If version invalid:
  Version format: v1.2.3 (semantic versioning)
```

## Best Practices

### Validate Early

```markdown
# Good: Validate before main logic
Check: !\`validate-input.sh $1\`

If valid:
  [main logic]

# Bad: Validate after work started
[start work]
Check: !\`validate-input.sh $1\`  # Too late!
```

### Provide Helpful Errors

```markdown
If validation fails:
  - Explain what went wrong
  - Show correct usage
  - Provide example
  - Suggest next steps
```

### Handle Missing Arguments

```markdown
If $1 is empty:
  Show usage: /command [required-arg] [optional-arg]
  Describe each argument
  Provide example: /command foo --flag
```

## Input Sanitization

### Quote Arguments

```bash
# In bash execution
!\`process.sh "$1"\`  # Quoted - safe
!\`process.sh $1\`    # Unquoted - injection risk
```

### Escape Special Characters

```markdown
If input contains special characters:
  Sanitize before processing
  Or reject with clear error message
```

### Path Validation

```markdown
Check for path traversal: !\`echo "$1" | grep -q '\.\.' && echo "INVALID_PATH" || echo "OK"\`

If path contains ..:
  Reject with "Path traversal not allowed"
```
