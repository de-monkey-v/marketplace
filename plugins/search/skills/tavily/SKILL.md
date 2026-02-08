---
name: tavily
description: "Tavily web search skill. 활성화: tavily, 웹 검색, 실시간 검색, 문서 추출, 사이트 크롤링, 웹 정보 수집"
version: 2.0.0
---

# Tavily Web Search Skill

Guide for AI-optimized web search and data collection using the Tavily API.

## Tool Selection Guide

```
+-------------------------------------------------------------+
|                      Task Start                              |
|                         |                                    |
|              Complex topic research?                         |
|                    /    \                                     |
|                  YES     NO                                  |
|                   |       |                                  |
|         * Research *    Quick info lookup?                    |
|         (recommended)       /    \                            |
|                           YES     NO                         |
|                            |       |                         |
|                       Search    Specific URL?                |
|                                   /    \                     |
|                                 YES     NO                   |
|                                  |       |                   |
|                              Extract   Entire site?          |
|                                           /    \             |
|                                         YES     NO           |
|                                          |       |           |
|                                    Crawl-Save   Crawl        |
|                                   (markdown)    (JSON)       |
+-------------------------------------------------------------+
```

---

## Core Tools

### 1. Research (recommended) - AI Comprehensive Research

The most powerful feature. Use for complex topic research.

**Features:**
- AI synthesizes multiple sources for deep analysis
- Automatic citation inclusion
- Model selection: mini (fast), pro (deep), auto (automatic)

```bash
# Basic usage
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-research.sh "React Server Components architecture"

# Specify model
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-research.sh "Python async patterns" --model pro

# Save results
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-research.sh "Next.js 15" --output result.json
```

**Options:**
| Option | Description | Default |
|--------|------------|---------|
| `--model` | mini / pro / auto | auto |
| `--max-results` | Maximum result count | 10 |
| `--no-citations` | Exclude citations | false |
| `--output FILE` | Save results to file | - |

---

### 2. Search - Quick Web Search

For simple info lookups. Returns results quickly.

```bash
# Basic search
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-search.sh "React 19 new features"

# Search specific domains only
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-search.sh "Python tutorial" \
    --include-domains python.org,realpython.com

# Exclude specific domains
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-search.sh "JavaScript best practices" \
    --exclude-domains medium.com

# Past week search
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-search.sh "Claude API updates" --time week

# Include AI summary answer
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-search.sh "TypeScript 5.0" --include-answer
```

**Options:**
| Option | Description | Default |
|--------|------------|---------|
| `--depth` | basic / advanced | advanced |
| `--time` | day / week / month / year | - |
| `--max-results` | Maximum result count | 10 |
| `--include-domains` | Specific domains only (comma-separated) | - |
| `--exclude-domains` | Exclude specific domains (comma-separated) | - |
| `--include-answer` | Include AI summary answer | false |
| `--output FILE` | Save results to file | - |

**Backward compatibility:** Positional arguments also supported
```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-search.sh "query" advanced week
```

---

### 3. Extract - URL Content Extraction

Use when specific page content is needed.

```bash
# Single URL
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-extract.sh "https://react.dev/blog"

# Multiple URLs simultaneously
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-extract.sh \
    "https://docs.python.org/3/library/asyncio.html" \
    "https://realpython.com/async-io-python/"
```

---

### 4. Crawl-Save - Save as Markdown (recommended)

Crawls documentation sites and saves as markdown files.

**Features:**
- Saves each page as individual `.md` file
- Includes source URL and timestamp in frontmatter
- Generates `_crawl_summary.json` summary file

```bash
# Basic usage
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-crawl-save.sh "https://docs.nextjs.org"

# Specify output directory
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-crawl-save.sh "https://react.dev" \
    --output-dir ./react-docs

# Adjust crawl scope
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-crawl-save.sh "https://vitejs.dev" \
    --max-depth 3 --limit 100
```

**Output structure:**
```
crawled_context/
└── docs.nextjs.org/
    ├── _crawl_summary.json
    ├── index.md
    ├── app_building-your-application.md
    └── ...
```

**Options:**
| Option | Description | Default |
|--------|------------|---------|
| `--output-dir` | Output directory | ./crawled_context |
| `--max-depth` | Crawl depth | 2 |
| `--max-breadth` | Links per page | 10 |
| `--limit` | Maximum pages | 50 |
| `--extract-depth` | basic / advanced | advanced |

---

### 5. Crawl - JSON Output

Outputs crawl results as JSON. For programmatic processing.

```bash
# Basic crawl
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-crawl.sh "https://docs.nextjs.org"

# With options
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-crawl.sh "https://react.dev" \
    --max-depth 3 --limit 100 --output crawl.json
```

**Options:**
| Option | Description | Default |
|--------|------------|---------|
| `--extract-depth` | basic / advanced | advanced |
| `--max-depth` | Crawl depth | 2 |
| `--max-breadth` | Links per page | 10 |
| `--limit` | Maximum pages | 50 |
| `--output FILE` | Save results to file | - |

---

## Workflow Patterns

### Error Deep Investigation

```bash
# 1. Comprehensive analysis via Research (recommended)
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-research.sh \
    "Next.js hydration mismatch error solution"

# Or step-by-step approach:
# 2. Search for overview
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-search.sh \
    "Next.js hydration mismatch error solution"

# 3. Extract official docs
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-extract.sh \
    "https://nextjs.org/docs/messages/react-hydration-error"
```

### Library Documentation Collection

```bash
# 1. Crawl documentation site (save as markdown)
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-crawl-save.sh \
    "https://docs.nextjs.org/app/building-your-application" \
    --output-dir ./nextjs-docs

# 2. Analyze saved files
ls ./nextjs-docs/docs.nextjs.org/
```

### Latest Technology Trend Research

```bash
# Comprehensive analysis via Research
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-research.sh \
    "2026 frontend framework trends" --model pro

# Or time-filtered search
bash ${CLAUDE_PLUGIN_ROOT}/scripts/tavily-search.sh \
    "React 19 release" --time month
```

---

## Tavily vs WebSearch Comparison

| Item | WebSearch | Tavily |
|------|-----------|--------|
| Purpose | General web search | AI-optimized search |
| Result quality | Search engine results | LLM-ready structured |
| Extra features | None | research, extract, crawl |
| Use case | Quick info lookup | Deep research, data collection |

**Recommended:**
- Quick search -> WebSearch
- Deep research -> Tavily Research
- Data extraction/collection -> Tavily Extract/Crawl

---

## Script Requirements

**Shell (recommended):**
- Requires `curl`, `jq` (pre-installed on most systems)
- No Python version dependency

**Python (alternative):**
- Requires Python 3.9+ (3.8 and below not supported)
- Requires `tavily-python` package: `pip install tavily-python`

---

## Limitations

- API call limits may apply (rate limiting)
- Some sites may block crawling
- Dynamic content (SPA) may have extraction limitations
- Research API requires latest tavily-python
