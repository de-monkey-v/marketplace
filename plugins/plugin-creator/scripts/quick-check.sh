#!/bin/bash
#
# quick-check.sh - Fast plugin sanity check
#
# Usage: ./quick-check.sh [plugin-path]
#
# Performs minimal validation for quick feedback during development.
# For comprehensive testing, use test-plugin.sh
#

set -euo pipefail

PLUGIN_PATH="${1:-.}"
PLUGIN_PATH=$(cd "$PLUGIN_PATH" && pwd)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "Quick Check: $PLUGIN_PATH"
echo "---"

# Check plugin.json
if [[ -f "${PLUGIN_PATH}/.claude-plugin/plugin.json" ]]; then
    if jq empty "${PLUGIN_PATH}/.claude-plugin/plugin.json" 2>/dev/null; then
        NAME=$(jq -r '.name' "${PLUGIN_PATH}/.claude-plugin/plugin.json")
        echo -e "${GREEN}✓${NC} plugin.json valid (name: $NAME)"
    else
        echo -e "${RED}✗${NC} plugin.json invalid JSON"
        exit 1
    fi
else
    echo -e "${RED}✗${NC} plugin.json not found"
    exit 1
fi

# Count components
CMD_COUNT=$(find "${PLUGIN_PATH}/commands" -name "*.md" -type f 2>/dev/null | wc -l || echo 0)
AGENT_COUNT=$(find "${PLUGIN_PATH}/agents" -name "*.md" -type f 2>/dev/null | wc -l || echo 0)
SKILL_COUNT=$(find "${PLUGIN_PATH}/skills" -name "SKILL.md" -type f 2>/dev/null | wc -l || echo 0)
HOOK_EXISTS=$([[ -f "${PLUGIN_PATH}/hooks/hooks.json" ]] && echo "yes" || echo "no")
MCP_EXISTS=$([[ -f "${PLUGIN_PATH}/.mcp.json" ]] && echo "yes" || echo "no")

echo ""
echo "Components:"
echo "  Commands: $CMD_COUNT"
echo "  Agents:   $AGENT_COUNT"
echo "  Skills:   $SKILL_COUNT"
echo "  Hooks:    $HOOK_EXISTS"
echo "  MCP:      $MCP_EXISTS"

# Check for obvious issues
ISSUES=0

# Check hooks.json if exists
if [[ -f "${PLUGIN_PATH}/hooks/hooks.json" ]]; then
    if ! jq empty "${PLUGIN_PATH}/hooks/hooks.json" 2>/dev/null; then
        echo -e "${RED}✗${NC} hooks.json invalid JSON"
        ((ISSUES++))
    fi
fi

# Check .mcp.json if exists
if [[ -f "${PLUGIN_PATH}/.mcp.json" ]]; then
    if ! jq empty "${PLUGIN_PATH}/.mcp.json" 2>/dev/null; then
        echo -e "${RED}✗${NC} .mcp.json invalid JSON"
        ((ISSUES++))
    fi
fi

echo ""
if [[ $ISSUES -eq 0 ]]; then
    echo -e "${GREEN}Quick check passed${NC}"
    exit 0
else
    echo -e "${RED}Found $ISSUES issue(s)${NC}"
    exit 1
fi
