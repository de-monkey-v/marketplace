#!/bin/bash
#
# test-plugin.sh - Comprehensive plugin validation script
#
# Usage: ./test-plugin.sh [plugin-path]
#        If no path provided, uses current directory
#
# Exit codes:
#   0 - All tests passed
#   1 - Critical errors found
#   2 - Warnings found (no critical errors)
#

set -uo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
CRITICAL=0
WARNINGS=0
PASSED=0

# Plugin path
PLUGIN_PATH="${1:-.}"

# Resolve absolute path
PLUGIN_PATH=$(cd "$PLUGIN_PATH" && pwd)

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Plugin Validation Test Suite${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "Plugin path: ${PLUGIN_PATH}"
echo ""

# Helper functions
pass() {
    echo -e "  ${GREEN}✓${NC} $1"
    PASSED=$((PASSED + 1))
}

warn() {
    echo -e "  ${YELLOW}⚠${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

fail() {
    echo -e "  ${RED}✗${NC} $1"
    CRITICAL=$((CRITICAL + 1))
}

section() {
    echo ""
    echo -e "${BLUE}━━━ $1 ━━━${NC}"
}

# ============================================
# Test 1: Plugin Structure
# ============================================
section "Plugin Structure"

# Check plugin.json exists
if [[ -f "${PLUGIN_PATH}/.claude-plugin/plugin.json" ]]; then
    pass "plugin.json exists"
else
    fail "plugin.json not found at .claude-plugin/plugin.json"
fi

# Check plugin.json is valid JSON
if [[ -f "${PLUGIN_PATH}/.claude-plugin/plugin.json" ]]; then
    if jq empty "${PLUGIN_PATH}/.claude-plugin/plugin.json" 2>/dev/null; then
        pass "plugin.json is valid JSON"
    else
        fail "plugin.json is not valid JSON"
    fi
fi

# Check required fields
if [[ -f "${PLUGIN_PATH}/.claude-plugin/plugin.json" ]]; then
    NAME=$(jq -r '.name // empty' "${PLUGIN_PATH}/.claude-plugin/plugin.json" 2>/dev/null)
    VERSION=$(jq -r '.version // empty' "${PLUGIN_PATH}/.claude-plugin/plugin.json" 2>/dev/null)
    DESCRIPTION=$(jq -r '.description // empty' "${PLUGIN_PATH}/.claude-plugin/plugin.json" 2>/dev/null)

    if [[ -n "$NAME" ]]; then
        pass "name field present: $NAME"
    else
        fail "name field missing"
    fi

    if [[ -n "$VERSION" ]]; then
        pass "version field present: $VERSION"
    else
        warn "version field missing"
    fi

    if [[ -n "$DESCRIPTION" ]]; then
        pass "description field present"
    else
        warn "description field missing"
    fi
fi

# Check name format (kebab-case)
if [[ -n "${NAME:-}" ]]; then
    if [[ "$NAME" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
        pass "name follows kebab-case convention"
    else
        warn "name should be kebab-case (lowercase, hyphens only)"
    fi
fi

# ============================================
# Test 2: Commands
# ============================================
section "Commands"

if [[ -d "${PLUGIN_PATH}/commands" ]]; then
    CMD_COUNT=$(find "${PLUGIN_PATH}/commands" -name "*.md" -type f | wc -l)
    pass "commands/ directory found with $CMD_COUNT command(s)"

    # Check each command
    shopt -s nullglob
    for cmd in "${PLUGIN_PATH}"/commands/*.md; do
        if [[ -f "$cmd" ]]; then
            CMD_NAME=$(basename "$cmd")

            # Check for frontmatter
            if head -1 "$cmd" | grep -q "^---$"; then
                # Check for description in frontmatter
                if grep -q "^description:" "$cmd"; then
                    pass "$CMD_NAME has description"
                else
                    warn "$CMD_NAME missing description in frontmatter"
                fi
            else
                warn "$CMD_NAME missing YAML frontmatter"
            fi
        fi
    done
else
    echo "  (no commands/ directory)"
fi

# ============================================
# Test 3: Agents
# ============================================
section "Agents"

if [[ -d "${PLUGIN_PATH}/agents" ]]; then
    AGENT_COUNT=$(find "${PLUGIN_PATH}/agents" -name "*.md" -type f | wc -l)
    pass "agents/ directory found with $AGENT_COUNT agent(s)"

    # Check each agent
    for agent in "${PLUGIN_PATH}"/agents/*.md; do
        if [[ -f "$agent" ]]; then
            AGENT_NAME=$(basename "$agent")

            # Check for frontmatter
            if head -1 "$agent" | grep -q "^---$"; then
                # Check for description
                if grep -q "^description:" "$agent"; then
                    # Check if description is multiline (bad)
                    DESC_LINE=$(grep "^description:" "$agent" | head -1)
                    if echo "$DESC_LINE" | grep -q '|$'; then
                        warn "$AGENT_NAME uses multiline description (should be single-line)"
                    else
                        pass "$AGENT_NAME has single-line description"
                    fi
                else
                    fail "$AGENT_NAME missing description"
                fi

                # Check for name field
                if grep -q "^name:" "$agent"; then
                    pass "$AGENT_NAME has name field"
                else
                    warn "$AGENT_NAME missing name field"
                fi
            else
                fail "$AGENT_NAME missing YAML frontmatter"
            fi
        fi
    done
else
    echo "  (no agents/ directory)"
fi

# ============================================
# Test 4: Skills
# ============================================
section "Skills"

if [[ -d "${PLUGIN_PATH}/skills" ]]; then
    SKILL_COUNT=$(find "${PLUGIN_PATH}/skills" -name "SKILL.md" -type f | wc -l)
    pass "skills/ directory found with $SKILL_COUNT skill(s)"

    # Check each skill
    for skill_dir in "${PLUGIN_PATH}"/skills/*/; do
        if [[ -d "$skill_dir" ]]; then
            SKILL_NAME=$(basename "$skill_dir")
            SKILL_FILE="${skill_dir}SKILL.md"

            # Skip common/ directory (reference files, not a skill)
            if [[ "$SKILL_NAME" == "common" ]]; then
                echo "  (skipping common/ - reference files only)"
                continue
            fi

            if [[ -f "$SKILL_FILE" ]]; then
                pass "$SKILL_NAME has SKILL.md"

                # Check for frontmatter
                if head -1 "$SKILL_FILE" | grep -q "^---$"; then
                    # Check for description
                    if grep -q "^description:" "$SKILL_FILE"; then
                        # Check if description uses third person
                        DESC=$(grep "^description:" "$SKILL_FILE" | head -1)
                        if echo "$DESC" | grep -qi "this skill"; then
                            pass "$SKILL_NAME uses third-person description"
                        else
                            warn "$SKILL_NAME description should use third person ('This skill should be used when...')"
                        fi
                    else
                        fail "$SKILL_NAME missing description"
                    fi
                else
                    fail "$SKILL_NAME SKILL.md missing frontmatter"
                fi

                # Check word count
                WORD_COUNT=$(wc -w < "$SKILL_FILE")
                if [[ $WORD_COUNT -gt 5000 ]]; then
                    warn "$SKILL_NAME has $WORD_COUNT words (consider moving content to references/)"
                elif [[ $WORD_COUNT -lt 500 ]]; then
                    warn "$SKILL_NAME has only $WORD_COUNT words (may be too brief)"
                else
                    pass "$SKILL_NAME has appropriate length ($WORD_COUNT words)"
                fi
            else
                fail "$SKILL_NAME missing SKILL.md"
            fi
        fi
    done
else
    echo "  (no skills/ directory)"
fi

# ============================================
# Test 5: Hooks
# ============================================
section "Hooks"

HOOKS_FILE="${PLUGIN_PATH}/hooks/hooks.json"
if [[ -f "$HOOKS_FILE" ]]; then
    pass "hooks.json exists"

    # Check valid JSON
    if jq empty "$HOOKS_FILE" 2>/dev/null; then
        pass "hooks.json is valid JSON"

        # Check for plugin wrapper format
        if jq -e '.hooks' "$HOOKS_FILE" >/dev/null 2>&1; then
            pass "hooks.json uses plugin wrapper format"
        else
            warn "hooks.json should use wrapper format: {\"hooks\": {...}}"
        fi

        # Check for ${CLAUDE_PLUGIN_ROOT} usage
        if grep -q '\${CLAUDE_PLUGIN_ROOT}' "$HOOKS_FILE" 2>/dev/null || ! grep -q '"command"' "$HOOKS_FILE" 2>/dev/null; then
            pass "hooks.json uses portable paths"
        else
            if grep -q '"command"' "$HOOKS_FILE" && ! grep -q '\${CLAUDE_PLUGIN_ROOT}' "$HOOKS_FILE"; then
                warn "hooks.json has commands without \${CLAUDE_PLUGIN_ROOT}"
            fi
        fi
    else
        fail "hooks.json is not valid JSON"
    fi
else
    echo "  (no hooks/hooks.json)"
fi

# ============================================
# Test 6: MCP Configuration
# ============================================
section "MCP Configuration"

MCP_FILE="${PLUGIN_PATH}/.mcp.json"
if [[ -f "$MCP_FILE" ]]; then
    pass ".mcp.json exists"

    # Check valid JSON
    if jq empty "$MCP_FILE" 2>/dev/null; then
        pass ".mcp.json is valid JSON"

        # Check for HTTPS usage
        if grep -qi '"url"' "$MCP_FILE"; then
            if grep -qi 'http://' "$MCP_FILE"; then
                fail ".mcp.json uses HTTP (should use HTTPS)"
            else
                pass ".mcp.json uses secure connections"
            fi
        fi

        # Check for ${CLAUDE_PLUGIN_ROOT}
        if grep -q '"command"' "$MCP_FILE"; then
            if grep -q '\${CLAUDE_PLUGIN_ROOT}' "$MCP_FILE"; then
                pass ".mcp.json uses portable paths"
            else
                warn ".mcp.json commands should use \${CLAUDE_PLUGIN_ROOT}"
            fi
        fi
    else
        fail ".mcp.json is not valid JSON"
    fi
else
    echo "  (no .mcp.json)"
fi

# ============================================
# Test 7: Security Checks
# ============================================
section "Security Checks"

# Check for hardcoded paths
HARDCODED=$(grep -r '/home/\|/Users/' "${PLUGIN_PATH}" --include="*.md" --include="*.json" --include="*.sh" 2>/dev/null | grep -v 'test-plugin.sh' | head -5)
if [[ -n "$HARDCODED" ]]; then
    warn "Found hardcoded paths (use \${CLAUDE_PLUGIN_ROOT} instead)"
    echo "$HARDCODED" | while read -r line; do
        echo "      $line"
    done
else
    pass "No hardcoded paths found"
fi

# Check for potential credentials
CREDS=$(grep -ri 'password\|secret\|api_key\|apikey\|token' "${PLUGIN_PATH}" --include="*.json" 2>/dev/null | grep -v '\${' | head -3)
if [[ -n "$CREDS" ]]; then
    warn "Potential hardcoded credentials found"
else
    pass "No hardcoded credentials found"
fi

# Check .gitignore
if [[ -f "${PLUGIN_PATH}/.gitignore" ]]; then
    if grep -q '\.local\.md' "${PLUGIN_PATH}/.gitignore" 2>/dev/null; then
        pass ".gitignore excludes .local.md files"
    else
        warn ".gitignore should exclude .claude/*.local.md"
    fi
else
    echo "  (no .gitignore file)"
fi

# ============================================
# Test 8: Documentation
# ============================================
section "Documentation"

if [[ -f "${PLUGIN_PATH}/README.md" ]]; then
    pass "README.md exists"

    # Check README content
    README_CONTENT=$(cat "${PLUGIN_PATH}/README.md")

    if echo "$README_CONTENT" | grep -qi "install"; then
        pass "README includes installation info"
    else
        warn "README should include installation instructions"
    fi

    if echo "$README_CONTENT" | grep -qi "usage\|how to"; then
        pass "README includes usage info"
    else
        warn "README should include usage instructions"
    fi
else
    warn "README.md not found"
fi

# ============================================
# Summary
# ============================================
echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Summary${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "  ${GREEN}Passed:${NC}   $PASSED"
echo -e "  ${YELLOW}Warnings:${NC} $WARNINGS"
echo -e "  ${RED}Critical:${NC} $CRITICAL"
echo ""

if [[ $CRITICAL -gt 0 ]]; then
    echo -e "${RED}FAILED${NC} - Critical issues must be fixed"
    exit 1
elif [[ $WARNINGS -gt 0 ]]; then
    echo -e "${YELLOW}PASSED WITH WARNINGS${NC} - Consider fixing warnings"
    exit 2
else
    echo -e "${GREEN}ALL TESTS PASSED${NC}"
    exit 0
fi
