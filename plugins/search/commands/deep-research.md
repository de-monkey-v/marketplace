---
name: deep-research
description: "Generate in-depth research reports using Tavily Research API + smart-searcher. 활성화: 심층 조사, 연구, deep research, 보고서"
argument-hint: "<topic> [--model mini|pro|auto] [--no-citations] [--max-results N] [--save FILE]"
allowed-tools: Bash, Read, Write, Glob, Grep, Task
---

# /deep-research

Performs **AI comprehensive research** using Tavily Research API, supplemented by **smart-searcher** to generate an in-depth report.

## Language Resolution

1. Check `$ARGUMENTS` for `--language=eng` or `--language=kor` → use if present
2. Read `.hyper-team/metadata.json` → use `language` field if file exists
3. Default: `eng`

Produce all user-facing output in the resolved language.

## Arguments

| Argument | Usage | Description |
|----------|-------|-------------|
| `<topic>` | `/deep-research React 19 Server Components` | Topic to research |
| `--model` | `--model pro` | Tavily model: mini (fast), pro (deep), auto (automatic) |
| `--no-citations` | `--no-citations` | Exclude citations |
| `--max-results` | `--max-results 15` | Maximum number of results (default: 10) |
| `--save` | `--save report.md` | Save report to file |

---

## Workflow Overview

```
$ARGUMENTS (research topic)
          |
+----------------------------------+
|   Phase 1: Initial Research      |
|   Tavily Research API (core)     |
|   Run tavily-research.py         |
+--------------+-------------------+
               |
+----------------------------------+
|   Phase 2: Supplementary Search  |
|                                  |
|      smart-searcher              |
|   (Auto-selects Context7/        |
|    WebSearch/Brave/Tavily)       |
+--------------+-------------------+
               |
+----------------------------------+
|   Phase 3: Report Synthesis      |
|   Generate markdown report       |
+----------------------------------+
               |
         Final Report
```

---

## Phase Table

| Phase | Component | Task | Mode |
|-------|-----------|------|------|
| 1 | **Bash** (tavily-research.py) | AI comprehensive research | Sequential |
| 2 | **smart-searcher** agent | Supplementary search (auto tool selection) | Sequential |
| 3 | - | Result integration and report generation | Sequential |

---

## Execution

### Step 0: Parse Arguments

Parse `$ARGUMENTS` to extract:

1. **Topic (query)**: Quoted or first argument
2. **Options**:
   - `--model`: mini | pro | auto (default: auto)
   - `--no-citations`: Exclude citations flag
   - `--max-results`: Number (default: 10)
   - `--save`: File path

**Parsing example:**
```
Input: "React 19 architecture" --model pro --save report.md
-> query: "React 19 architecture"
-> model: "pro"
-> citations: true
-> max_results: 10
-> save_file: "report.md"
```

---

### Phase 1: Initial Research (Tavily Research API)

Performs **AI comprehensive research** using Tavily Research API. This is the core of the report.

**Execution:**

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-research.py "<query>" \
    --model <model> \
    [--no-citations] \
    --max-results <N>
```

**Store results:** Save JSON result to `tavily_result` variable

**Output structure:**
```json
{
  "topic": "Research topic",
  "summary": "Comprehensive summary",
  "content": "Detailed research content",
  "citations": [
    {"text": "Citation content", "source": "Source URL"}
  ],
  "sources": [
    {"title": "Title", "url": "URL"}
  ]
}
```

**After completion:** Proceed to Phase 2

---

### Phase 2: Supplementary Search (smart-searcher)

Performs additional search via **smart-searcher** to supplement Phase 1 results.

Use the **smart-searcher** agent:

```
Task tool:
- subagent_type: "search:smart-searcher"
- description: "Supplementary search"
- prompt: |
    Perform a supplementary search on the following topic:

    Topic: $QUERY

    Basic research has already been completed via Tavily Research.
    Focus on searching for:
    - Official documentation (using Context7)
    - Latest news/trends (if needed)
    - Practical examples and community tips

    Summarize the search results.
```

**smart-searcher auto-selection:**
- Library-related topics -> Context7 first
- General topics -> WebSearch
- News/trends included -> Brave/Tavily supplement

---

### Phase 3: Report Synthesis

Integrates all results into a **markdown research report**.

#### Report Structure

```markdown
# Deep Research Report: [topic]

> Generated: [date] | Model: [model] | Citations: [included/excluded]

---

## Executive Summary

[Phase 1 Tavily Research summary content]

---

## Detailed Research

### Core Findings (Tavily Research)

[Phase 1 content - AI comprehensive research results]

---

## Supplementary Research (smart-searcher)

[Phase 2 smart-searcher results]
- Official documentation
- Latest trends
- Practical examples

**Tools Used:** [Context7 / WebSearch / Brave / Tavily]

---

## Citations

[Phase 1 citations - omitted if --no-citations]

[1] "Citation content" - [Source](URL)
[2] "Citation content" - [Source](URL)

---

## All Sources

### Tavily Research
- [Title](URL)

### Supplementary
- [Title](URL)

---

*Generated by `/deep-research` | search plugin*
```

---

#### Save Option Handling

If `--save` option is present:

```bash
# Save report to file using Write tool
Write tool -> Save markdown report to specified file path
```

After saving:
```
Report saved: [file path]
```

---

## Examples

```bash
# Basic usage
/deep-research React 19 Server Components

# Use deep model
/deep-research "Next.js 15 new features" --model pro

# Save to file
/deep-research "Rust memory management" --save rust-research.md

# Exclude citations, increase results
/deep-research "AI development trends 2026" --no-citations --max-results 15

# All options combined
/deep-research "Claude API usage" --model pro --max-results 20 --save claude-api.md
```

---

## smart-searcher Usage

### Auto Tool Selection

| Topic Type | Selected Tool |
|-----------|---------------|
| Library/framework | Context7 (official docs) |
| General tech info | WebSearch |
| Latest news/trends | Brave |
| Deep analysis needed | Tavily (additional) |

### Cost Efficiency

- Phase 1: Tavily Research (credit)
- Phase 2: smart-searcher prioritizes free tools (Context7, WebSearch)
- Only uses Brave/Tavily additionally when needed

---

## Quality Standards

### Information Priority

| Rank | Source | Reliability |
|------|--------|------------|
| 1 | Tavily Research (AI comprehensive) | Highest |
| 2 | Context7 official docs | Highest |
| 3 | WebSearch / Brave / Tavily supplement | High |

### Quality Checklist

- [ ] Tavily Research results form the report core
- [ ] All information has sources cited
- [ ] Duplicate information removed
- [ ] Consistent markdown formatting
- [ ] File saved if --save option used

---

## Error Handling

| Error | Response |
|-------|----------|
| Tavily Research API failure | Show error message, execute Phase 2 only |
| smart-searcher timeout | Mark section as "No information available" |
| File save failure | Show error, output report to console |

---

## Comparison with /search

| Item | /search | /deep-research |
|------|---------|----------------|
| Speed | Fast | Slow (sequential) |
| Depth | Surface-level | In-depth |
| Output | Unified answer | Structured report |
| Core | smart-searcher | Tavily Research + smart-searcher |
| Credits | Situational | 1+ (Research required) |
| Use case | Quick info lookup | Comprehensive research/analysis |
