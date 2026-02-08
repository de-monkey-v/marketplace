# Plugin Creator Scripts

Utility scripts for plugin development and validation.

## Scripts

### test-plugin.sh

Comprehensive plugin validation test suite.

```bash
# Validate plugin in current directory
./test-plugin.sh

# Validate specific plugin
./test-plugin.sh /path/to/my-plugin

# Exit codes:
#   0 - All tests passed
#   1 - Critical errors found
#   2 - Warnings found (no critical errors)
```

**Checks performed:**
- Plugin structure and manifest
- Commands (frontmatter, description)
- Agents (frontmatter, single-line description, name)
- Skills (SKILL.md, description, word count)
- Hooks (JSON validity, wrapper format, portable paths)
- MCP configuration (JSON validity, HTTPS, portable paths)
- Security (hardcoded paths, credentials)
- Documentation (README.md)

### quick-check.sh

Fast sanity check for development.

```bash
# Quick check current plugin
./quick-check.sh

# Quick check specific plugin
./quick-check.sh /path/to/my-plugin
```

**Checks performed:**
- plugin.json exists and is valid
- Component counts
- JSON validity of hooks.json and .mcp.json

## Usage in CI/CD

```yaml
# GitHub Actions example
- name: Validate Plugin
  run: |
    chmod +x ./scripts/test-plugin.sh
    ./scripts/test-plugin.sh ./my-plugin
```

## Component-Specific Scripts

For detailed component validation, see scripts in skill directories:

- `skills/agent-development/scripts/validate-agent.sh` - Validate agent files
- `skills/hook-development/scripts/validate-hook-schema.sh` - Validate hooks.json
- `skills/hook-development/scripts/test-hook.sh` - Test hook scripts
- `skills/hook-development/scripts/hook-linter.sh` - Lint hook scripts
- `skills/plugin-settings/scripts/validate-settings.sh` - Validate settings files
- `skills/plugin-settings/scripts/parse-frontmatter.sh` - Parse YAML frontmatter
