---
name: brave
description: "Brave Search API skill. 활성화: brave 검색, brave search, 웹 검색, 뉴스 검색, 검색어 추천, 맞춤법 검사"
version: 1.0.0
---

# Brave Search API Skill

Guide for web search, news search, query suggestions, and spell checking using the Brave Search API.

## Tool Selection Guide

```
+-------------------------------------------------------------+
|                      Task Start                              |
|                         |                                    |
|              News/latest articles?                           |
|                    /    \                                     |
|                  YES     NO                                  |
|                   |       |                                  |
|            * News *    General web search?                    |
|                              /    \                           |
|                            YES     NO                        |
|                             |       |                        |
|                        Search    Query suggestions?           |
|                                     /    \                   |
|                                   YES     NO                 |
|                                    |       |                 |
|                               Suggest   Spell check          |
|                                          |                   |
|                                     Spellcheck               |
+-------------------------------------------------------------+
```

---

## Environment Setup

**API Key Setup:**
```bash
export BRAVE_API_KEY="your-api-key-here"
```

Get an API key from [Brave Search API Dashboard](https://api.search.brave.com/).

---

## Core Tools

### 1. Search - Web Search

General web search. Uses Brave's independent index.

```bash
# Basic search
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-search.py "React 19 new features"

# Specify result count
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-search.py "TypeScript tutorial" --count 20

# Past week search
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-search.py "AI news" --freshness pw

# Specific country/language
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-search.py "local events" --country US --lang en

# Turn off safe search
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-search.py "tech news" --safesearch off
```

**Options:**
| Option | Description | Default |
|--------|------------|---------|
| `--count` | Result count (1-20) | 10 |
| `--offset` | Pagination (0-9) | 0 |
| `--country` | Country code (US, KR, etc.) | - |
| `--lang` | Search language | - |
| `--freshness` | Time filter (pd/pw/pm/py) | - |
| `--safesearch` | off / moderate / strict | moderate |
| `--output` | Save results to file | - |

**freshness values:**
- `pd`: Past day (24 hours)
- `pw`: Past week (1 week)
- `pm`: Past month (1 month)
- `py`: Past year (1 year)

---

### 2. News - News Search

For searching latest news articles.

```bash
# Basic news search
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-news.py "climate change"

# Past week news
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-news.py "tech industry" --freshness pw

# Country-specific news
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-news.py "politics" --country KR --lang ko

# Include extra snippets
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-news.py "AI" --extra-snippets
```

**Options:**
| Option | Description | Default |
|--------|------------|---------|
| `--count` | Result count (1-20) | 10 |
| `--offset` | Pagination | 0 |
| `--country` | Country code | - |
| `--lang` | Search language | - |
| `--freshness` | Time filter | - |
| `--safesearch` | off / moderate / strict | moderate |
| `--extra-snippets` | Include extra excerpts | false |
| `--output` | Save results to file | - |

---

### 3. Suggest - Query Suggestions

Query autocomplete/suggestion feature.

```bash
# Basic suggestions
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-suggest.py "how to"

# More suggestions
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-suggest.py "python" --count 10

# Rich results (descriptions, images, etc.)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-suggest.py "react" --rich

# Specific language/country
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-suggest.py "restaurants" --lang ko --country KR
```

**Options:**
| Option | Description | Default |
|--------|------------|---------|
| `--count` | Suggestion count (1-20) | 5 |
| `--lang` | Language | en |
| `--country` | Country code | US |
| `--rich` | Include rich results | false |
| `--output` | Save results to file | - |

---

### 4. Spellcheck - Spell Checking

Query spell correction.

```bash
# Spell check
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-spellcheck.py "artifical inteligence"

# Specific language
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-spellcheck.py "programming" --lang ko
```

**Options:**
| Option | Description | Default |
|--------|------------|---------|
| `--lang` | Language | en |
| `--country` | Country code | US |
| `--output` | Save results to file | - |

---

## Workflow Patterns

### Optimize Query Then Search

```bash
# 1. Spell check
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-spellcheck.py "artifical inteligence"
# -> "artificial intelligence"

# 2. Expand with query suggestions
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-suggest.py "artificial intelligence" --rich

# 3. Web search
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-search.py "artificial intelligence trends 2026"
```

### Latest News Monitoring

```bash
# Latest news on specific topic
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-news.py "OpenAI" --freshness pd --count 20
```

### Multi-language Search

```bash
# Korean news
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-news.py "Samsung" --country KR --lang ko

# Japanese search
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/brave-search.py "Toyota" --country JP --lang ja
```

---

## Brave vs Other Search API Comparison

| Item | Brave | WebSearch | Tavily |
|------|-------|-----------|--------|
| Index | Independent | Bing-based | AI-optimized |
| Free tier | 2,000/month | None | 1,000/month |
| News search | Yes | No | No |
| Query suggestions | Yes | No | No |
| Spell check | Yes | No | No |
| Privacy | Highest | Medium | Medium |

**Recommended:**
- Privacy-focused -> Brave
- Quick general search -> WebSearch
- AI-optimized results -> Tavily

---

## Response Structure

### Web/News Search Response

```json
{
  "query": { "original": "search query" },
  "web": {
    "results": [
      {
        "title": "Title",
        "url": "URL",
        "description": "Description",
        "age": "Publication time"
      }
    ]
  }
}
```

### Suggest Response

```json
{
  "query": { "original": "search query" },
  "results": [
    {
      "query": "Suggested query",
      "is_entity": false
    }
  ]
}
```

### Spellcheck Response

```json
{
  "query": { "original": "original" },
  "results": [
    { "query": "Corrected query" }
  ]
}
```

---

## Limitations

- **Rate Limit**: Free tier 1 QPS, paid plans higher
- **Result count**: Max 20 per request
- **Pagination**: Max offset 9 (total 200)
- **Query length**: Max 400 characters, 50 words

### API Support by Plan

| API | Free | Base | Pro |
|-----|------|------|-----|
| Web Search | Yes | Yes | Yes |
| News Search | Yes | Yes | Yes |
| Suggest | No | Yes | Yes |
| Spellcheck | No | Yes | Yes |

Only **Web Search** and **News Search** are available on the free plan.

---

## Reference Links

- [Brave Search API Dashboard](https://api.search.brave.com/)
- [Web Search API Docs](https://api-dashboard.search.brave.com/app/documentation/web-search/query)
- [News Search API Docs](https://api-dashboard.search.brave.com/app/documentation/news-search/query)
