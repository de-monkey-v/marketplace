# Plugin Troubleshooting Guide

Common issues and solutions when developing Claude Code plugins.

## Component Not Loading

**Symptoms:** Skill/command/agent not appearing or not triggering.

**Checklist:**
- [ ] Verify file is in correct directory with correct extension
- [ ] Check YAML frontmatter syntax (commands, agents, skills)
- [ ] Ensure skill has `SKILL.md` (not `README.md` or other name)
- [ ] Confirm plugin is enabled in Claude Code settings
- [ ] Restart Claude Code after adding new components

**Common causes:**
- Wrong file extension (.md required)
- Missing or malformed frontmatter
- Skill file not named exactly `SKILL.md`
- Plugin not enabled

## Path Resolution Errors

**Symptoms:** Scripts not found, file not accessible.

**Checklist:**
- [ ] Replace all hardcoded paths with `${CLAUDE_PLUGIN_ROOT}`
- [ ] Verify paths are relative and start with `./` in manifest
- [ ] Check that referenced files exist at specified paths
- [ ] Test with `echo $CLAUDE_PLUGIN_ROOT` in hook scripts

**Common causes:**
- Hardcoded absolute paths
- Missing ${CLAUDE_PLUGIN_ROOT} prefix
- Typos in path names
- File moved but reference not updated

## Auto-Discovery Not Working

**Symptoms:** Components exist but not discovered.

**Checklist:**
- [ ] Confirm directories are at plugin root (not in `.claude-plugin/`)
- [ ] Check file naming follows conventions (kebab-case, correct extensions)
- [ ] Verify custom paths in manifest are correct
- [ ] Restart Claude Code to reload plugin configuration

**Common causes:**
- Components placed inside `.claude-plugin/` instead of plugin root
- Custom path configuration error
- File not following naming convention

## Conflicts Between Plugins

**Symptoms:** Wrong component activated, unexpected behavior.

**Solutions:**
- Use unique, descriptive component names
- Namespace commands with plugin name if needed
- Document potential conflicts in plugin README
- Consider command prefixes for related functionality

## Hooks Not Executing

**Symptoms:** Hook defined but never triggers.

**Checklist:**
- [ ] Verify hooks.json syntax is valid JSON
- [ ] Check matcher pattern matches intended events
- [ ] Ensure script has execute permissions
- [ ] Test script manually first
- [ ] Check `claude --debug` output for hook errors

**Common causes:**
- Invalid JSON syntax
- Incorrect matcher pattern
- Script not executable
- Script path incorrect

## MCP Server Not Connecting

**Symptoms:** MCP tools not available.

**Checklist:**
- [ ] Verify .mcp.json syntax
- [ ] Check server command/URL is correct
- [ ] Ensure required environment variables are set
- [ ] Test server command manually
- [ ] Check `/mcp` output for connection status

**Common causes:**
- Missing environment variables
- Server not installed/accessible
- Network connectivity issues
- Authentication problems

## Debugging Tips

1. **Use `claude --debug`**: See detailed hook execution and errors
2. **Check `/agents` output**: Verify agents are loaded
3. **Test scripts manually**: Run hook scripts directly to verify behavior
4. **Validate JSON**: Use `jq` or online validators for JSON files
5. **Incremental changes**: Add one component at a time and test
