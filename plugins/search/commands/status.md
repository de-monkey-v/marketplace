---
name: search:status
description: "Check API keys, service status, and load balancing state for the search plugin. 활성화: 상태 체크, 검색 상태, search status"
argument-hint: ""
allowed-tools: Bash, Read
---

# /search:status

Checks the status of all search services and load balancing state used by the search plugin.

## Language Resolution

1. Check `$ARGUMENTS` for `--language=eng` or `--language=kor` → use if present
2. Read `.hyper-team/metadata.json` → use `language` field if file exists
3. Default: `eng`

Produce all user-facing output in the resolved language.

## Arguments

This command requires no arguments.

---

## Workflow Overview

```
Status Check Start
        |
+-------+-------+----------+----------+
|       |       |          |          |
Tavily  Brave   Context7   WebSearch  Load
API     API     MCP        (built-in) Balancing
Check   Check   Check      Always OK  State
+-------+-------+----------+----------+
        |
   Print Results
```

---

## Execution

### Step 1: Check Load Balancing State

**Check state file:**

```bash
# Read state file
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/search-state.py status
```

**Interpret results:**
- `lastUsedApi`: Last API used (brave/tavily)
- `braveAvailable`: Whether Brave API is available
- `tavilyAvailable`: Whether Tavily API is available
- `usageCount`: Cumulative usage count per API

**Check next API:**

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/search-state.py next
```

---

### Step 2: Tavily API Status Check

1. **Check environment variable**

   ```bash
   # Check if TAVILY_API_KEY environment variable exists
   if [ -n "$TAVILY_API_KEY" ]; then
       echo "TAVILY_API_KEY: configured"
   else
       echo "TAVILY_API_KEY: not set"
   fi
   ```

2. **API connection test** (only if API key exists)

   Run Tavily API test script:
   ```bash
   bash ${CLAUDE_PLUGIN_ROOT}/scripts/check-tavily.sh
   ```

   **Interpret results:**
   - Response contains `results` field: OK
   - Contains `error` field: API error
   - No response: Network error

---

### Step 3: Brave API Status Check

1. **Check environment variable**

   ```bash
   # Check if BRAVE_API_KEY environment variable exists
   if [ -n "$BRAVE_API_KEY" ]; then
       echo "BRAVE_API_KEY: configured"
   else
       echo "BRAVE_API_KEY: not set"
   fi
   ```

---

### Step 4: Context7 MCP Status Check

Context7 operates as an MCP server and does not require an API key.

**How to check:**

1. Look for `mcp__context7__resolve-library-id` or `mcp__plugin_context7_context7__resolve-library-id` in the available MCP tools list
2. If the tool is in the list, it is available

**Criteria:**
- If Context7 MCP tools are available in the current session: Available
- If tools are not found: Not connected (MCP server setup required)

---

### Step 5: WebSearch Status Check

WebSearch is a built-in Claude tool and is always available.

---

### Step 6: Output Results

Output in the following format:

```
[search] Status Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Load Balancing State
- Last used API: [brave/tavily]
- Next API: [brave/tavily]
- Brave usage count: [N]
- Tavily usage count: [N]
- Brave available: [Yes/No]
- Tavily available: [Yes/No]

## Tavily API
- API Key: [status]
- Connection test: [status]

## Brave API
- API Key: [status]

## Context7 MCP
- Status: [status]

## WebSearch
- Status: Built-in tool (always available)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Status Indicators

| Service | Check Method | Normal | Error |
|---------|-------------|--------|-------|
| Load Balancing | State file check | Status displayed | File missing (init required) |
| Tavily API Key | Environment variable | Configured | Not set |
| Tavily Connection | API call test | OK | Error (detailed message) |
| Brave API Key | Environment variable | Configured | Not set |
| Context7 MCP | MCP tool availability | Available | Not connected |
| WebSearch | Built-in tool | Always available | - |

---

## Load Balancing Commands

### Reset State

To reset state after monthly credit reset:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/search-state.py reset
```

### Mark API as Unavailable

When a specific API's credits are depleted:

```bash
# Mark Brave as unavailable
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/search-state.py unavailable brave

# Mark Tavily as unavailable
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/search-state.py unavailable tavily
```

---

## Troubleshooting

### Tavily API Key Not Set

```bash
# Add to .bashrc or .zshrc
export TAVILY_API_KEY="your-api-key"

# Or use .env file
echo 'TAVILY_API_KEY=your-api-key' >> ~/.env
```

Get a Tavily API key at https://app.tavily.com

### Brave API Key Not Set

```bash
# Add to .bashrc or .zshrc
export BRAVE_API_KEY="your-api-key"
```

Get a Brave API key at https://brave.com/search/api/

### Context7 MCP Not Connected

Add Context7 MCP server configuration to `.mcp.json` or `.claude/settings.json`:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

### Load Balancing State File Missing

The state file is auto-created on first use. To manually initialize:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/search-state.py reset
```

---

## Examples

```bash
# Run status check
/search:status
```
