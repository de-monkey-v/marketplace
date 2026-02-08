---
name: setup
description: Interactive setup wizard for the search plugin. Checks prerequisites, installs dependencies, and configures API keys for Tavily, Brave Search, and Context7.
argument-hint: "[--language=eng|kor]"
allowed-tools: Bash, Read, Write, Edit, AskUserQuestion
---

# /search:setup - Setup Wizard

Interactive setup wizard for the search plugin.

## Language Resolution

1. Check `$ARGUMENTS` for `--language=eng` or `--language=kor` → use if present
2. Read `.hyper-team/metadata.json` → use `language` field if file exists
3. Default: `eng`

Produce all user-facing output in the resolved language.

---

## Step 1: Detect Shell Environment

```
Bash: echo $SHELL
```

Determine if the user uses bash or zsh:
- If contains "zsh": RC_FILE=~/.zshrc
- If contains "bash": RC_FILE=~/.bashrc
- Otherwise: Ask the user which shell config file they use.

---

## Step 2: Check Prerequisites

### 2.1: Check Python3

```
Bash: python3 --version
```

- If Python3 is found: report the version and continue.
- If Python3 is NOT found: warn the user that Python3 is required for Tavily integration. Suggest installing Python3 via their package manager. Ask if they want to continue without Tavily support.

### 2.2: Check Node.js/npm (for Context7 MCP)

```
Bash: node --version && npm --version
```

- If Node.js is found: report the version.
- If NOT found: note that Context7 MCP requires Node.js. It can still be skipped.

---

## Step 3: Choose Search Services

<instructions>
All search services are optional. The plugin works with just the free built-in WebSearch + Context7.

Ask the user which premium search services they want to configure:
</instructions>

```
AskUserQuestion:
- question: "Which search services do you want to configure? All are optional - the plugin works with free WebSearch + Context7 even without any API keys."
- header: "Services"
- multiSelect: true
- options:
  - label: "Tavily Search"
    description: "Deep web search & data extraction. Requires API key from https://app.tavily.com"
  - label: "Brave Search"
    description: "Fast web & news search. Requires API key from https://brave.com/search/api/"
  - label: "Context7 MCP"
    description: "Library documentation search via MCP server. Free, no API key needed."
  - label: "Skip all"
    description: "Use only the built-in free WebSearch tool"
```

---

## Step 4: Configure Tavily (if selected)

<instructions>
Only execute this step if the user selected "Tavily Search" in Step 3. Otherwise skip to Step 5.
</instructions>

### 4.1: Guide API Key Setup

Display to the user:

```
To get your Tavily API key:
1. Go to https://app.tavily.com
2. Sign up for a free account (or log in)
3. Navigate to the "API Keys" page
4. Copy your API key
```

### 4.2: Get the API Key

```
AskUserQuestion:
- question: "Paste your Tavily API key:"
- header: "Tavily Key"
- options:
  - label: "I have my key ready"
    description: "I'll paste it in the 'Other' field below"
  - label: "Skip for now"
    description: "I'll configure Tavily later"
```

### 4.3: Add to Shell RC File

<instructions>
If the user provided a key (via "Other" input), add it to the RC file.

First check if TAVILY_API_KEY already exists:
</instructions>

```
Bash: grep -c 'TAVILY_API_KEY' $RC_FILE 2>/dev/null || echo "0"
```

- If it already exists: Ask the user if they want to replace the existing value.
  - If yes: Use Edit to replace the existing export line.
  - If no: Skip.
- If it does not exist: Append the export line:

```
Bash: echo '' >> $RC_FILE && echo '# Tavily Search API Key (search plugin)' >> $RC_FILE && echo 'export TAVILY_API_KEY="<USER_KEY>"' >> $RC_FILE
```

### 4.4: Install tavily-python Package

```
Bash: pip install tavily-python 2>&1 || pip3 install tavily-python 2>&1
```

- If installation succeeds: report success.
- If it fails: warn the user and suggest `pip install --user tavily-python` or using a virtual environment.

---

## Step 5: Configure Brave Search (if selected)

<instructions>
Only execute this step if the user selected "Brave Search" in Step 3. Otherwise skip to Step 6.
</instructions>

### 5.1: Guide API Key Setup

Display to the user:

```
To get your Brave Search API key:
1. Go to https://brave.com/search/api/
2. Create an account (or log in)
3. Subscribe to the Free tier (2,000 queries/month)
4. Go to your dashboard and copy the API key
```

### 5.2: Get the API Key

```
AskUserQuestion:
- question: "Paste your Brave Search API key:"
- header: "Brave Key"
- options:
  - label: "I have my key ready"
    description: "I'll paste it in the 'Other' field below"
  - label: "Skip for now"
    description: "I'll configure Brave Search later"
```

### 5.3: Add to Shell RC File

<instructions>
If the user provided a key (via "Other" input), add it to the RC file.

First check if BRAVE_API_KEY already exists:
</instructions>

```
Bash: grep -c 'BRAVE_API_KEY' $RC_FILE 2>/dev/null || echo "0"
```

- If it already exists: Ask the user if they want to replace the existing value.
  - If yes: Use Edit to replace the existing export line.
  - If no: Skip.
- If it does not exist: Append the export line:

```
Bash: echo '' >> $RC_FILE && echo '# Brave Search API Key (search plugin)' >> $RC_FILE && echo 'export BRAVE_API_KEY="<USER_KEY>"' >> $RC_FILE
```

---

## Step 6: Configure Context7 MCP (if selected)

<instructions>
Only execute this step if the user selected "Context7 MCP" in Step 3. Otherwise skip to Step 7.
</instructions>

### 6.1: Check Existing MCP Configuration

Check if Context7 is already configured:

```
Bash: cat ~/.claude/settings.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('found' if 'context7' in str(d.get('mcpServers',{})).lower() else 'not_found')" 2>/dev/null || echo "not_found"
```

Also check project-level:

```
Bash: cat .mcp.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('found' if 'context7' in str(d.get('mcpServers',{})).lower() else 'not_found')" 2>/dev/null || echo "not_found"
```

### 6.2: Add Context7 MCP Server

<instructions>
If Context7 is not found in either config, ask where to add it:
</instructions>

```
AskUserQuestion:
- question: "Where should Context7 MCP be configured?"
- header: "MCP Scope"
- options:
  - label: "User-level (Recommended)"
    description: "Available in all projects via ~/.claude/settings.json"
  - label: "Project-level"
    description: "Only for this project via .mcp.json"
  - label: "Skip"
    description: "I'll configure Context7 MCP manually later"
```

<instructions>
If user-level: Read ~/.claude/settings.json, merge the following into the mcpServers key:

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

If project-level: Read .mcp.json (create if needed), merge the same config.

Use Read + Edit/Write to safely merge without overwriting existing MCP servers.

If Context7 is already configured, inform the user and skip.
</instructions>

---

## Step 7: Verify Configuration

### 7.1: Source RC File and Verify Environment Variables

```
Bash: source $RC_FILE 2>/dev/null; echo "TAVILY=$([ -n \"$TAVILY_API_KEY\" ] && echo 'configured' || echo 'not set')"; echo "BRAVE=$([ -n \"$BRAVE_API_KEY\" ] && echo 'configured' || echo 'not set')"
```

### 7.2: Verify tavily-python Installation (if Tavily was configured)

```
Bash: python3 -c "import tavily; print('tavily-python installed')" 2>&1 || echo "tavily-python not installed"
```

### 7.3: Verify Context7 MCP (if configured)

```
Bash: npx -y @upstash/context7-mcp --help 2>&1 | head -5 || echo "Context7 MCP not available"
```

---

## Step 8: Summary

Display a formatted summary based on the resolved language:

### English Summary:

```markdown
## Search Plugin Setup Complete

| Service        | Status       | Details                          |
|----------------|--------------|----------------------------------|
| WebSearch      | Ready        | Built-in, always available       |
| Tavily Search  | {status}     | {configured/skipped/error}       |
| Brave Search   | {status}     | {configured/skipped/error}       |
| Context7 MCP   | {status}     | {configured/skipped/error}       |

### Configured Environment Variables
- TAVILY_API_KEY: {set in RC_FILE / not configured}
- BRAVE_API_KEY: {set in RC_FILE / not configured}

### Next Steps
1. Run `source {RC_FILE}` or restart your terminal to load new environment variables
2. Restart Claude Code to pick up MCP server changes (if Context7 was configured)
3. Use `/search:status` to verify all services are working
4. Try `/search:search your query` to test the search functionality
```

### Korean Summary:

```markdown
## Search 플러그인 설정 완료

| 서비스          | 상태         | 세부사항                         |
|----------------|--------------|----------------------------------|
| WebSearch      | 사용 가능     | 내장 기능, 항상 사용 가능          |
| Tavily Search  | {상태}       | {설정 완료/건너뜀/오류}            |
| Brave Search   | {상태}       | {설정 완료/건너뜀/오류}            |
| Context7 MCP   | {상태}       | {설정 완료/건너뜀/오류}            |

### 설정된 환경변수
- TAVILY_API_KEY: {RC_FILE에 설정됨 / 미설정}
- BRAVE_API_KEY: {RC_FILE에 설정됨 / 미설정}

### 다음 단계
1. `source {RC_FILE}` 실행 또는 터미널 재시작으로 환경변수 로드
2. MCP 서버 변경 적용을 위해 Claude Code 재시작 (Context7 설정한 경우)
3. `/search:status`로 모든 서비스 동작 확인
4. `/search:search 검색어`로 검색 기능 테스트
```
