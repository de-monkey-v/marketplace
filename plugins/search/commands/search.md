---
name: search
description: "Unified search via smart-searcher (auto-selects Context7/WebSearch/Brave/Tavily). 활성화: 검색해줘, 검색해, 찾아줘, 조사해줘, search for, look up, find info"
argument-hint: "<query>"
allowed-tools: Task
---

# /search

Performs an optimized search for your question using the **smart-searcher** agent.
The agent automatically selects the appropriate tool among Context7, WebSearch, Brave, and Tavily based on context.

## Language Resolution

1. Check `$ARGUMENTS` for `--language=eng` or `--language=kor` → use if present
2. Read `.hyper-team/metadata.json` → use `language` field if file exists
3. Default: `eng`

Produce all user-facing output in the resolved language.

## Arguments

| Argument | Usage | Description |
|----------|-------|-------------|
| `<query>` | `/search React 19 new features` | Question or keywords to search |

---

## Workflow Overview

```
$ARGUMENTS (user query)
           |
+------------------------------+
|     Query Analysis           |
|  (Classify question type)    |
+----------+-------------------+
           |
     Claude-related?
      /        \
    YES         NO
     |           |
+---------+  +-----------------+
| claude- |  |  smart-searcher |
| docs-   |  |                 |
|searcher |  | Auto tool pick: |
|         |  | - Context7      |
|         |  | - WebSearch     |
|         |  | - Brave         |
|         |  | - Tavily        |
+----+----+  +--------+--------+
     |                |
     +-------+--------+
             |
+------------------------------+
|     Result Synthesis         |
|  (Organize and respond)     |
+------------------------------+
             |
       Final Answer
```

---

## Phase Table

| Phase | Agent | Task | Mode |
|-------|-------|------|------|
| 1 | - | Analyze query and classify type | - |
| 2 | **smart-searcher** OR **claude-docs-searcher** | Unified search | Sequential |
| 3 | - | Organize results and generate answer | - |

---

## Execution

### Phase 1: Query Analysis

Parse `$ARGUMENTS` and classify question type:

**Question Type Classification:**

| Keywords | Type | Agent |
|----------|------|-------|
| Claude Code, Claude API, Claude SDK, MCP, plugin, hooks, Agent SDK | Claude-related | **claude-docs-searcher** |
| React, FastAPI, Next.js, Django, library names, etc. | General search | **smart-searcher** |
| Error messages, trends, news, general info | General search | **smart-searcher** |

---

### Phase 2: Search Execution

#### Case A: Claude-related Question

Use the **claude-docs-searcher** agent:

```
Task tool:
- subagent_type: "search:claude-docs-searcher"
- description: "Claude official docs search"
- prompt: |
    Search the Claude Code/API/SDK official documentation for:

    $ARGUMENTS

    Provide accurate information and code examples based on official docs.
```

#### Case B: General Search (most cases)

Use the **smart-searcher** agent:

```
Task tool:
- subagent_type: "search:smart-searcher"
- description: "Unified search"
- prompt: |
    Search for the following:

    $ARGUMENTS

    Select the optimal search tool for the situation and provide accurate information.
    - Library docs -> Context7
    - General info -> WebSearch
    - News/trends -> Brave
    - Deep research -> Tavily
```

---

### Phase 3: Result Synthesis

Organize agent results to generate the final answer:

**Quality Checklist:**
- [ ] Information sources cited
- [ ] Version/date info included
- [ ] Code examples verified (if applicable)

---

## Output Format

```markdown
## Search Results: [query summary]

### Key Answer

[Answer based on search results]

---

### Details

[Additional information and explanation]

### Code Examples (if applicable)

```[language]
[code]
```

---

**Sources:**
- [Title 1](URL1)
- [Title 2](URL2)

**Tools Used:** [Context7 / WebSearch / Brave / Tavily]
```

---

## Examples

```bash
# Claude Code related -> claude-docs-searcher
/search Claude Code plugin hooks.json guide
/search MCP server development guide

# General library -> smart-searcher (Context7 selected)
/search React 19 new features
/search FastAPI WebSocket implementation

# Error resolution -> smart-searcher (WebSearch + Brave/Tavily if needed)
/search "Module not found: @anthropic-ai/sdk" error fix
/search Next.js hydration error details

# Trends/news -> smart-searcher (Brave selected)
/search 2026 JavaScript trends
/search Latest AI industry news
```

---

## smart-searcher Tool Selection Criteria

| Request Type | Selected Tool | Cost |
|-------------|---------------|------|
| Library/framework docs | **Context7** | Free |
| General web search | **WebSearch** | Free |
| News/latest trends | **Brave** | Credit |
| Deep research/doc extraction | **Tavily** | Credit |

**Cost Optimization:** Prioritize free tools (Context7, WebSearch); use credit tools only when needed

---

## Quality Standards

### Reliability Priority

1. **Highest**: Claude official docs (claude-docs-searcher)
2. **Highest**: Library official docs (Context7)
3. **High**: WebSearch / Brave / Tavily results
4. **Medium**: Stack Overflow, tech blogs
5. **Low**: Personal blogs, outdated materials (2+ years)

### Source Citation Rules

- Cite sources for all information
- Include date/version info
- Flag outdated materials with warnings
