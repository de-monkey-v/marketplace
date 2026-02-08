# Claude API

## 검색 키워드
`API`, `Messages API`, `Tool Use`, `Vision`, `Rate Limits`, `에러`, `모델`, `streaming`, `batch`

---

## [API Overview](https://docs.anthropic.com/en/api/overview)

**포함 주제**: API 구조, 주요 기능, SDK 지원

### Claude API란?
- https://api.anthropic.com의 **RESTful API**로 Claude 모델에 프로그래밍 방식 접근 제공
- 기본 API: 메시지 API (POST /v1/messages)로 대화 인터페이스 제공

### 주요 기능
| 기능 | 설명 |
|------|------|
| Prompt Caching | 프롬프트 캐싱으로 비용 절감 |
| Context Editing | 컨텍스트 편집 |
| Extended Thinking | 확장 사고 (깊은 추론) |
| Streaming | 실시간 응답 스트리밍 |
| Batch Processing | 배치 처리 |
| Vision | 이미지 처리 |
| Files API | 파일 업로드/관리 |

---

## [Messages API](https://docs.anthropic.com/en/api/messages)

**포함 주제**: 엔드포인트 구조, 파라미터, 요청/응답 형식

### 필수 파라미터
| 파라미터 | 설명 |
|----------|------|
| `model` | 모델 식별자 |
| `max_tokens` | 생성할 최대 토큰 수 |
| `messages` | 대화 턴의 순서 배열 |

### 메시지 구조
```json
{
  "role": "user",  // "user" 또는 "assistant"
  "content": "질문 내용"
}
```

### 요청 헤더
```
x-api-key: YOUR_API_KEY
anthropic-version: 2023-06-01
content-type: application/json
```

### 스트리밍
- `stream: true`로 설정하여 응답 스트리밍 활성화

---

## [Tool Use Overview](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview)

**포함 주제**: Agent Skills, Tool Search, MCP 통합

### Agent Skills
- 지침, 스크립트, 리소스의 정렬된 폴더
- 에이전트가 동적으로 로드하여 특정 작업 수행
- Anthropic이 **오픈 스탠다드**로 공표

### Tool Search
- 모든 도구 정의를 미리 로드하는 대신 **필요에 따라 동적 로드**
- **토큰 사용량 85% 감소**
- 특정 작업에 필요한 도구만 지연 로딩

---

## [Vision](https://docs.anthropic.com/en/docs/build-with-claude/vision)

**포함 주제**: 이미지 입력 지원, Vision 기능

### Vision 기능
- 모든 현재 Claude 모델은 **텍스트와 이미지 입력** 지원
- Claude 3.5 Sonnet: 가장 강력한 vision 모델
  - 차트 및 그래프 해석
  - 불완전한 이미지에서 텍스트 전사

### 이미지 처리 방법
- Files API로 업로드
- 메시지에서 `file_id` 사용

### 제한사항
- 이미지에서 사람 식별(명명) 불가

---

## [Errors](https://docs.anthropic.com/en/api/errors)

**포함 주제**: API 에러 코드, 예외 처리, 자동 재시도

### HTTP 에러 코드
| 코드 | 설명 |
|------|------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Unprocessable Entity |
| 429 | Too Many Requests (Rate Limit) |
| 500+ | Internal Server Error |

### API 특정 에러
| 코드 | 타입 | 설명 |
|------|------|------|
| 500 | `api_error` | 내부 오류 |
| 529 | `overloaded_error` | 임시 과부하 |

### 자동 재시도
- 429 Rate Limit와 500+ Internal 에러는 **기본적으로 자동 재시도**

---

## [Rate Limits](https://docs.anthropic.com/en/api/rate-limits)

**포함 주제**: 속도 제한 유형, 계층별 제한

### 측정 지표
| 지표 | 설명 |
|------|------|
| RPM | 분당 요청 수 |
| ITPM | 분당 입력 토큰 수 |
| OTPM | 분당 출력 토큰 수 |

### 계층 시스템
| 계층 | 보증금 | 특징 |
|------|--------|------|
| Tier 1 | $5 | 기본 |
| Tier 4 | $400+ | 1백만 토큰 컨텍스트 창 |

---

## [Models Overview](https://docs.anthropic.com/en/docs/about-claude/models)

**포함 주제**: Claude 4.5 시리즈, 모델별 특징

### Claude 4.5 시리즈

**Claude Opus 4.5**
- 가장 강력한 모델
- 복잡한 추론, 어려운 문제 해결, 에이전트 기반 워크플로우
- **effort 파라미터**로 응답 철저함 조정

**Claude Sonnet 4.5**
- 가장 강력한 **코딩 및 에이전트 성능**
- 1백만 토큰 컨텍스트 창 옵션 (베타)
- SWE-bench Verified 최첨단 성능

**Claude Haiku 4.5**
- 빠른 응답
- 고용량 사용 시 **비용 효율성**
- 강력한 도구 호환성
