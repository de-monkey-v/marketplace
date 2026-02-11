# Search Plugin

A general-purpose search plugin that provides unified answers by searching web and official documentation in parallel.

## Features

### 5 Search Sources

1. **WebSearch** (web-searcher)
   - Latest information and trends
   - Uses WebSearch tool
   - Source filtering based on reliability

2. **Claude Official Docs** (claude-code-guide, built-in agent)
   - Claude Code CLI and plugins
   - Claude API usage
   - Claude Agent SDK (Python/TypeScript)
   - MCP server development

3. **General Library Docs** (context7-searcher)
   - React, Next.js, Vue, and other JavaScript libraries
   - FastAPI, Django, Flask, and other Python frameworks
   - MongoDB, PostgreSQL, and other databases
   - Other npm/PyPI packages

4. **Tavily Deep Search** (tavily-searcher)
   - AI-optimized web search
   - URL content extraction (multiple URLs simultaneously)
   - Website crawling
   - Research API (comprehensive research)

5. **Brave Search** (brave-searcher) - **NEW**
   - Latest news search
   - Web search
   - Spell checking and suggestions

### Core Features

- **Parallel Execution**: Fast responses via simultaneous agent execution
- **Intelligent Routing**: Selects appropriate agent combination based on question type
- **Load Balancing**: Even credit distribution by alternating Brave/Tavily API usage

---

## Load Balancing

### Problem Solved

Previously, only one of Brave or Tavily was called excessively, causing credits to deplete quickly.

### New Strategy

```
Search Request
    |
Phase 1: Free Search (always)
  |-- WebSearch (free)
  |-- context7 / claude-code-guide (free)
    |
Phase 2: Credit API Supplement (load balancing)
  |-- search-state.py next -> Check next API
  |-- brave-searcher or tavily-searcher (alternating)
    |
Result Integration
```

### How It Works

| Search # | API Used | lastUsedApi |
|----------|----------|-------------|
| 1st | Tavily | tavily |
| 2nd | Brave | brave |
| 3rd | Tavily | tavily |
| 4th | Brave | brave |
| ... | ... | ... |

### Credit Distribution Effect

| Scenario | Before | After |
|----------|--------|-------|
| 10 searches | 10 on one side | 5 each |
| One depleted | Manual switch | Auto fallback |

### State Management

```bash
# Check current state
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/search-state.py status

# Reset state (after monthly credit reset)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/search-state.py reset
```

---

## Installation

```bash
/plugin install search@de-monkey-v/marketplace
```

### Dependencies

```bash
# For Tavily
pip install tavily-python

# For Brave (set environment variable)
export BRAVE_API_KEY="your-api-key"
```

---

## Usage

### /search - Quick Search

```bash
/search <query>
```

**Workflow:**
1. Phase 1: Free search (WebSearch + official docs)
2. Phase 2: Credit API supplement (load balancing)
3. Result integration

#### Examples by Question Type

```bash
# Claude-related questions
/search Claude Code plugin hooks.json guide
/search How to create an MCP server

# General library questions
/search React 19 new features
/search FastAPI WebSocket implementation

# General information
/search 2026 JavaScript trends
```

### /deep-research - Deep Research

```bash
/deep-research <topic> [options]
```

**Options:**
- `--model`: mini | pro | auto (default: auto)
- `--no-citations`: Exclude citations
- `--max-results`: Maximum number of results (default: 10)
- `--save`: Save to file

**Workflow:**
1. Phase 1: Tavily Research API (core)
2. Phase 2: Free search (context7 + WebSearch)
3. Phase 3: Supplementary search (load balancing - typically Brave)
4. Report generation

```bash
# Basic usage
/deep-research React 19 Server Components

# Deep model + save to file
/deep-research "Next.js 15 new features" --model pro --save report.md
```

---

## Agent Details

### web-searcher
- **Role**: Provide latest information via web search
- **Tools**: WebSearch
- **Cost**: Free

### context7-searcher
- **Role**: Search general library docs via Context7 MCP
- **Tools**: resolve-library-id, query-docs
- **Cost**: Free

### claude-code-guide (built-in)
- **Role**: Claude Code/API/SDK specialist
- **Cost**: Free

### brave-searcher
- **Role**: News/web search via Brave Search
- **Tools**: brave-search.py, brave-news.py
- **Cost**: Credit-based

### tavily-searcher
- **Role**: Deep search and extraction via Tavily API
- **Tools**: tavily-search.py, tavily-extract.py
- **Cost**: Credit-based

---

## Tavily Scripts

```bash
# Web search (AI-optimized)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-search.py "query" advanced week

# URL content extraction
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-extract.py "url1" "url2"

# Website crawling
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-crawl.py "url"

# Comprehensive research (Research API)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-research.py "topic" --model pro
```

## Brave Scripts

```bash
# Web search
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-search.py "query"

# News search
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-news.py "query"

# Spell suggestions
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-suggest.py "query"
```

---

## Reliability Priority

1. **Highest**: Claude official docs (claude-code-guide)
2. **Highest**: General library official docs (context7-searcher)
3. **High**: WebSearch results
4. **High**: Brave/Tavily search results
5. **Medium**: Stack Overflow, verified tech blogs
6. **Low**: Personal blogs, outdated materials (2+ years)

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TAVILY_API_KEY` | Tavily API key | Optional |
| `BRAVE_API_KEY` | Brave Search API key | Optional |

---

## State File

Load balancing state is stored in `.search-state.json`:

```json
{
  "lastUsedApi": "brave",
  "braveAvailable": true,
  "tavilyAvailable": true,
  "usageCount": {"brave": 5, "tavily": 5}
}
```

---

## Troubleshooting

### Context7 Error
```
Error: Context7 MCP not found
```
-> Context7 MCP server installation required

### Tavily Error
```
ModuleNotFoundError: No module named 'tavily'
```
-> `pip install tavily-python`

### Credit Depletion
When one API's credits are depleted, it automatically falls back to the other API.
After monthly credit reset:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/search-state.py reset
```

### No Search Results
- Write more specific queries
- Include English keywords
- Try alternative phrasing

---

## License

MIT

> This plugin respects the language setting in `.hyper-team/metadata.json`. Run `/hyper-team:setup` to configure.
