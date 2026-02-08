# Search Plugin 사용 예시

다양한 사용 시나리오와 예상 응답 패턴입니다.

---

## 1. Claude 관련 검색

### 예시 1-1: Claude Code 플러그인 개발

**질문**:
```bash
/search Claude Code 플러그인 hooks.json 작성법
```

**예상 응답**:
```markdown
## Search Results: Claude Code 플러그인 hooks.json 작성법

### 핵심 답변

hooks.json 파일은 플러그인의 이벤트 기반 자동화를 정의합니다...

---

### 📚 Claude 공식 문서 (claude-code-guide)

hooks.json은 다음과 같은 구조를 가집니다:

```json
{
  "hooks": {
    "PreToolUse": [...],
    "PostToolUse": [...],
    "UserPromptSubmit": [...]
  }
}
```

**지원 이벤트**:
- PreToolUse: 도구 사용 전
- PostToolUse: 도구 사용 후
- SessionEnd: 세션 종료 시
...

**Source**: Claude Code 공식 문서

---

### 🌐 웹 검색 결과 (web-searcher)

최근 커뮤니티에서 공유된 hooks.json 패턴...

**Sources:**
- [Claude Code Plugin Guide](URL)
- [GitHub Example](URL)
```

---

### 예시 1-2: Claude API tool use

**질문**:
```bash
/search Claude API에서 tool use 사용법
```

**예상 응답**:
```markdown
## Search Results: Claude API tool use 사용법

### 핵심 답변

Claude API의 tool use 기능은 함수 호출을 통해...

---

### 📚 Claude 공식 문서 (claude-code-guide)

#### Tool Definition

```python
tools = [{
    "name": "get_weather",
    "description": "Get weather information",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        }
    }
}]

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    tools=tools,
    messages=[...]
)
```

**Source**: Claude API 공식 문서

---

### 🌐 웹 검색 결과

실전 예시 및 베스트 프랙티스...
```

---

## 2. 일반 라이브러리 검색

### 예시 2-1: React 새 기능

**질문**:
```bash
/search React 19 새로운 기능
```

**예상 응답**:
```markdown
## Search Results: React 19 새로운 기능

### 핵심 답변

React 19는 다음과 같은 주요 기능을 도입했습니다...

---

### 📚 공식 문서 (context7-searcher)

#### React 19 주요 변경사항

1. **Actions**: 폼 처리 개선
2. **use() Hook**: 비동기 데이터 로딩
3. **Server Components**: 향상된 서버 컴포넌트

```jsx
// use() hook 예시
function Component() {
  const data = use(fetchData());
  return <div>{data}</div>;
}
```

**Source**: Context7 - `/facebook/react`

---

### 🌐 웹 검색 결과

React 19 릴리즈 노트 및 커뮤니티 반응...

**Sources:**
- [React Blog: React 19](https://react.dev/blog/2024/04/25/react-19)
- [Developer Guide](URL)
```

---

### 예시 2-2: FastAPI WebSocket

**질문**:
```bash
/search FastAPI WebSocket 구현 방법
```

**예상 응답**:
```markdown
## Search Results: FastAPI WebSocket 구현 방법

### 핵심 답변

FastAPI는 websocket 데코레이터를 통해...

---

### 📚 공식 문서 (context7-searcher)

#### WebSocket 기본 구현

```python
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message: {data}")
```

**Source**: Context7 - `/fastapi/fastapi`

---

### 🌐 웹 검색 결과

실전 WebSocket 패턴 및 에러 처리...

**Sources:**
- [FastAPI WebSocket Tutorial](URL)
- [Stack Overflow Best Practices](URL)
```

---

## 3. 일반 정보 검색

### 예시 3-1: JavaScript 트렌드

**질문**:
```bash
/search 2026 JavaScript 트렌드
```

**예상 응답**:
```markdown
## Search Results: 2026 JavaScript 트렌드

### 🌐 웹 검색 결과

#### 주요 트렌드

1. **TypeScript 우세**: 점유율 80% 돌파
2. **Server-First Frameworks**: Next.js, Astro 성장
3. **Edge Computing**: Vercel Edge, Cloudflare Workers

**Sources:**
- [State of JS 2026](URL)
- [Tech Trends Report](URL)
- [Developer Survey](URL)
```

---

## 4. 에러 해결

### 예시 4-1: Module not found 에러

**질문**:
```bash
/search "Module not found: @anthropic-ai/sdk" 에러 해결
```

**예상 응답**:
```markdown
## Search Results: Module not found 에러 해결

### 핵심 답변

이 에러는 @anthropic-ai/sdk 패키지가 설치되지 않았을 때 발생합니다.

---

### 📚 Claude 공식 문서 (claude-code-guide)

#### 설치 방법

```bash
# npm
npm install @anthropic-ai/sdk

# yarn
yarn add @anthropic-ai/sdk

# pnpm
pnpm add @anthropic-ai/sdk
```

**버전 확인**:
```bash
npm list @anthropic-ai/sdk
```

**Source**: Claude API 공식 문서

---

### 🌐 웹 검색 결과

#### 일반적인 해결 방법

1. 패키지 설치 확인
2. node_modules 삭제 후 재설치
3. package.json 확인

**Sources:**
- [GitHub Issue](URL)
- [Stack Overflow](URL)
```

---

### 예시 4-2: CORS 에러

**질문**:
```bash
/search React에서 CORS error 해결 방법
```

**예상 응답**:
```markdown
## Search Results: React CORS error 해결

### 핵심 답변

CORS 에러는 브라우저의 동일 출처 정책에 의해 발생합니다...

---

### 📚 공식 문서 (context7-searcher)

React 자체는 CORS를 직접 처리하지 않습니다.
서버 측 설정이 필요합니다.

**개발 환경 해결**:
```json
// package.json
{
  "proxy": "http://localhost:3001"
}
```

**Source**: Context7 - `/facebook/react`

---

### 🌐 웹 검색 결과

#### 서버 측 해결 방법

**Express.js**:
```javascript
const cors = require('cors');
app.use(cors());
```

**FastAPI**:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

**Sources:**
- [MDN CORS Guide](URL)
- [Express CORS](URL)
```

---

## 5. 프레임워크 비교

### 예시 5-1: Next.js 라우터 비교

**질문**:
```bash
/search Next.js App Router vs Pages Router 차이점
```

**예상 응답**:
```markdown
## Search Results: Next.js App Router vs Pages Router

### 핵심 답변

Next.js 13에서 도입된 App Router는...

---

### 📚 공식 문서 (context7-searcher)

| 기능 | App Router | Pages Router |
|------|-----------|-------------|
| 파일 위치 | app/ | pages/ |
| 서버 컴포넌트 | 기본값 | 지원 안 함 |
| 레이아웃 | 중첩 가능 | _app.js만 |
| 데이터 페칭 | fetch() | getServerSideProps |

**마이그레이션 가이드**:
- 점진적 마이그레이션 가능
- 두 라우터 동시 사용 가능

**Source**: Context7 - `/vercel/next.js`

---

### 🌐 웹 검색 결과

커뮤니티 경험 및 마이그레이션 팁...

**Sources:**
- [Next.js Blog](URL)
- [Migration Guide](URL)
```

---

## 6. 복합 질문

### 예시 6-1: MCP 서버 + FastAPI

**질문**:
```bash
/search MCP 서버를 FastAPI로 구현하는 방법
```

**예상 응답**:
```markdown
## Search Results: MCP 서버 FastAPI 구현

### 핵심 답변

MCP(Model Context Protocol) 서버를 FastAPI로 구현...

---

### 📚 Claude 공식 문서 (claude-code-guide)

#### MCP 서버 구조

MCP 서버는 다음 기능을 제공해야 합니다:
- Tools: 함수 정의
- Resources: 리소스 제공
- Prompts: 프롬프트 템플릿

**Source**: Claude Code 공식 문서

---

### 📚 공식 문서 (context7-searcher)

#### FastAPI 기본 구조

```python
from fastapi import FastAPI
app = FastAPI()

@app.post("/tools/{tool_name}")
async def execute_tool(tool_name: str, params: dict):
    # MCP tool 실행
    pass
```

**Source**: Context7 - `/fastapi/fastapi`

---

### 🌐 웹 검색 결과

실전 MCP 서버 구현 예시...

**Sources:**
- [MCP Server Examples](URL)
- [FastAPI + MCP Guide](URL)
```

---

## 팁

1. **구체적으로 질문**: "React" 보다 "React 19 새 hooks"
2. **버전 명시**: "Next.js 15 App Router"
3. **에러는 전문 인용**: "정확한 에러 메시지"
4. **영문 키워드 포함**: 공식 문서 검색 시 유리
