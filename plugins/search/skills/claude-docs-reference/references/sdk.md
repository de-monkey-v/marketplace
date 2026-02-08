# Claude Agent SDK

## 검색 키워드
`Agent SDK`, `claude-agent-sdk`, `Python SDK`, `TypeScript SDK`, `커스텀 도구`, `MCP`, `에이전트 루프`

---

## [Agent SDK overview](https://docs.anthropic.com/en/docs/claude-code/sdk)

**포함 주제**: SDK 소개, 설치, 인증, 커스텀 도구, MCP 통합

### Claude Agent SDK란?
- Claude Code의 강력한 기능을 **프로그래매틱하게** 사용할 수 있는 라이브러리
- Python과 TypeScript로 제공
- Claude에게 "뇌"가 아닌 **"몸"**을 주는 것과 같음

### 핵심 기능
- 파일 읽기/쓰기, 명령 실행, 웹 검색, 코드 편집 등 **내장 도구**
- 자동 컨텍스트 관리 및 압축
- MCP를 통한 외부 도구 확장성
- 빌트인 에러 처리 및 세션 관리
- 자동 프롬프트 캐싱

### 인증 방식
| 방식 | 설명 |
|------|------|
| API 키 | `ANTHROPIC_API_KEY` 환경변수 |
| AWS Bedrock | AWS 자격증명 |
| Google Vertex AI | GCP 자격증명 |

---

## [SDK Python](https://docs.anthropic.com/en/docs/claude-code/sdk/sdk-python)

**포함 주제**: Python 설치, API 인증, 커스텀 도구, MCP 서버

### 설치
```bash
pip install claude-agent-sdk
```

### 시스템 요구사항
- Python 3.10 이상
- Node.js 18 이상 (Claude Code CLI용)

### 기본 사용 예시
```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

client = ClaudeSDKClient(
    api_key="your-api-key",
    options=ClaudeAgentOptions(
        model="claude-sonnet-4-5-20250929"
    )
)

result = client.query("주어진 파일을 분석하고 개선사항을 제안해줘")
print(result)
```

### 커스텀 도구 (MCP)
```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("greet", "사용자 인사", {"name": str})
async def greet_user(args):
    return {
        "content": [
            {"type": "text", "text": f"안녕하세요, {args['name']}님!"}
        ]
    }

server = create_sdk_mcp_server(
    name="my-tools",
    version="1.0.0",
    tools=[greet_user]
)
```

---

## [SDK TypeScript](https://docs.anthropic.com/en/docs/claude-code/sdk/sdk-typescript)

**포함 주제**: TypeScript 설치, 비동기 제너레이터, V2 인터페이스

### 설치
```bash
npm install @anthropic-ai/claude-agent-sdk
npm install -D typescript @types/node tsx
```

### 기본 사용 예시 (V1)
```typescript
import { query } from '@anthropic-ai/claude-agent-sdk'

const q = query({
  prompt: '2 + 2는 얼마인가?',
  options: { model: 'claude-sonnet-4-5-20250929' }
})

for await (const msg of q) {
  if (msg.type === 'result') {
    console.log(msg.result)
  }
}
```

### V2 인터페이스 (미리보기)
- 비동기 제너레이터 제거
- `send()/stream()` 패턴으로 단순화
- 멀티턴 대화 더 쉽게 구현

---

## [Building agents with Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)

**포함 주제**: 설계 원칙, Agent Loop 패턴, 실제 활용 사례

### 핵심 설계 원칙
에이전트에게 **"컴퓨터를 주는 것"**
- 인간처럼 작동할 수 있도록 파일 읽기, 명령 실행, 웹 검색, 코드 편집 능력 부여

### Agent Loop 패턴 (4단계)
```
1. Gather Context - 필요한 정보와 문맥 수집
2. Take Action - 도구를 사용하여 작업 수행
3. Verify Work - 작업 결과 검증
4. Repeat - 목표 달성까지 반복
```

### 실제 활용 사례
| 유형 | 설명 |
|------|------|
| 금융 에이전트 | 포트폴리오 이해 및 투자 평가 |
| 개인 어시스턴트 | 여행 예약 및 일정 관리 |
| 고객 지원 | 사용자 요청 처리 및 외부 API 연결 |

---

## SDK 비교 표

| 구분 | Python SDK | TypeScript SDK |
|------|-----------|----------------|
| **설치** | `pip install claude-agent-sdk` | `npm install @anthropic-ai/claude-agent-sdk` |
| **최소 버전** | Python 3.10+ | Node.js 18+ |
| **커스텀 도구** | @tool 데코레이터 + SDK MCP | 함수 기반 |
| **인터페이스** | 동기/비동기 혼합 | 비동기 제너레이터 (V1) |
| **권장 사용처** | 백엔드/CLI 도구 | 웹 애플리케이션 |
