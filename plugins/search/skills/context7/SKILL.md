---
name: context7
description: "Context7 MCP usage guide. 활성화: Context7, 라이브러리 문서, 공식 문서 검색, Library ID"
version: 1.0.0
---

# Context7 MCP Usage Guide

Guide for searching library official documentation using Context7 MCP.

## Core Tools

| Tool | Purpose |
|------|---------|
| `resolve-library-id` | Convert library name -> Library ID |
| `query-docs` | Query docs using Library ID |

---

## Workflow

### Case A: Library ID is Known

```
Use query-docs directly
-> query-docs(libraryId: "/facebook/react", query: "hooks")
```

### Case B: Library ID is Unknown

```
Step 1: resolve-library-id
  -> resolve-library-id(libraryName: "fastapi", query: "WebSocket usage")
  -> Result: "/fastapi/fastapi" (Benchmark Score: 95)

Step 2: query-docs
  -> query-docs(libraryId: "/fastapi/fastapi", query: "WebSocket implementation")
```

---

## Common Library ID List

### JavaScript/TypeScript

| Library | Library ID |
|---------|-----------|
| React | `/facebook/react` |
| Next.js | `/vercel/next.js` |
| Vue | `/vuejs/vue` |
| Svelte | `/sveltejs/svelte` |
| Astro | `/withastro/astro` |

### Python

| Library | Library ID |
|---------|-----------|
| FastAPI | `/fastapi/fastapi` |
| Django | `/django/django` |
| Flask | `/pallets/flask` |
| Pydantic | `/pydantic/pydantic` |

### Database

| Library | Library ID |
|---------|-----------|
| MongoDB | `/mongodb/docs` |
| Prisma | `/prisma/prisma` |
| Drizzle | `/drizzle-team/drizzle-orm` |

---

## resolve-library-id Usage Tips

### Good libraryName

```
"react" ✅
"fastapi" ✅
"next.js" ✅
"prisma" ✅
```

### Bad libraryName

```
"react hooks" ❌ (too specific)
"web framework" ❌ (too broad)
"best database" ❌ (vague)
```

### Good query

```
"How to use React hooks in functional components"
"FastAPI WebSocket implementation"
"Next.js App Router migration guide"
"Prisma schema relations"
```

---

## Output Format

```markdown
## Context7 Documentation: [topic]

### Official Docs-based Answer

[Summary of content from Context7]

### Key Information

1. **[Point 1]**
   - Description
   - Usage scenario

2. **[Point 2]**
   - Description
   - Caveats

### Code Examples

```[language]
[Code example from official docs]
```

---

**Source**: Context7 - `[Library ID]`
```

---

## Important Notes

### Must Follow

1. **Context7 first**: Always query official docs via Context7 MCP first
2. **Specify Library ID**: Cite information source
3. **Version awareness**: Note that differences may exist between versions
4. **No uncertain info**: If not in docs, state "Not confirmed in documentation"

### Excluded

**Claude Code, Claude API, Claude Agent SDK** are not searched with this tool.
-> Handled by built-in `claude-code-guide` agent

---

## API Call Limits

- `resolve-library-id`: Max 3 per question
- `query-docs`: Max 3 per question

If no results after 3 calls, use the best available result
