---
name: web-search
description: "WebSearch tool usage guide. 활성화: 웹 검색, WebSearch, 최신 정보 검색, 트렌드 검색"
version: 1.0.0
---

# WebSearch Usage Guide

Guide for effectively using the WebSearch tool to search for the latest information.

## Core Principles

### 1. Year Inclusion Required

Before searching, always check **Today's date** from `<env>` context and include the current year in queries.

```
Good queries:
- "React 19 new features 2026"
- "TypeScript 5.8 breaking changes 2026"

Bad queries:
- "React new features" (no year -> risk of outdated results)
```

### 2. No WebFetch

When web search is needed, always use the **WebSearch** tool only.

---

## Query Optimization

### Effective Query Structure

```
[technology] [version] [keyword] [current year]
```

**Examples:**
```
- "Next.js 15 App Router authentication 2026"
- "Python 3.12 asyncio best practices 2026"
- "TypeScript 5.8 breaking changes 2026"
```

### Queries to Avoid

| Pattern | Problem |
|---------|---------|
| `react` | Too broad |
| `how to code` | Vague |
| `best framework` | Subjective |
| Queries without year | Risk of outdated results |

---

## Source Reliability

### Tier 1 (Highest Priority)

| Source Type | Examples |
|------------|---------|
| Official docs | docs.react.dev, nodejs.org, python.org |
| GitHub releases | github.com/{org}/{repo}/releases |
| Official blogs | blog.nextjs.org, devblogs.microsoft.com |
| RFC/Proposals | tc39.es, peps.python.org |

### Tier 2 (Caution Required)

| Source Type | Caution |
|------------|---------|
| Stack Overflow | Check answer date (watch for 2+ years old) |
| Medium/Dev.to | Check publish date, verify version specification |
| Personal blogs | Verify freshness needed |

---

## Output Format

```markdown
## Search Results: [topic]

> Reference version: [version] (as of [year])

### Key Information
- [Key finding 1]
- [Key finding 2]

### Details
[Detailed search results]

---

**Sources:**
- [Title 1](URL1)
- [Title 2](URL2)
```

---

## Outdated Material Warning

When citing materials 2+ years old:

```markdown
**Note**: This information is from [year].
It may have changed in the current version - please verify with official documentation.
```

---

## Version Mismatch Prevention

1. **Check current latest version**: npm/pypi or official site
2. **Specify version**: Include version in all code examples
3. **Breaking changes warning**: Warn on major version differences

---

## Requirements

**Sources section is mandatory:**
- Search result summary
- URLs in markdown link format
