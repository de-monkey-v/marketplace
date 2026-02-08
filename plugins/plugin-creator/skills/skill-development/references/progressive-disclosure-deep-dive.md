# Progressive Disclosure Deep Dive

Anthropic의 Agent Skills 설계 철학을 기반으로 한 심화 가이드입니다.

## 핵심 원리

### 왜 Progressive Disclosure인가?

**문제**: LLM의 컨텍스트 윈도우는 제한적입니다.

```
┌─────────────────────────────────────────┐
│         컨텍스트 윈도우 (예: 128K)        │
├─────────────────────────────────────────┤
│ 시스템 프롬프트                          │
│ 사용자 대화 기록                         │
│ 도구 정의 (MCP 등)                       │
│ 스킬 정보                               │
│ ...                                     │
│ 🚨 포화 시 성능 저하, 정보 손실 발생      │
└─────────────────────────────────────────┘
```

**기존 방식의 문제** (MCP 등):
- 모든 도구/정보를 사전 로드
- 사용하지 않는 정보도 컨텍스트 점유
- 컨텍스트 윈도우 빠르게 포화

**Skills 방식의 해결책**:
- 필요한 정보만 단계적 로드
- 컨텍스트 효율성 극대화
- 더 많은 스킬을 더 효과적으로 사용 가능

## Two-Message Pattern 상세

Claude가 스킬을 사용하는 내부 메커니즘:

### Message 1: 발견 (Discovery)

```
시스템 프롬프트에 포함되는 내용:

Available Skills:
- skill-a: "데이터베이스 마이그레이션 요청 시 사용..."
- skill-b: "API 설계 질문에 답변..."
- skill-c: "Docker 워크플로우 안내..."
```

**이 단계에서 Claude는**:
- 모든 스킬의 name + description만 알고 있음
- 각 스킬당 ~100 단어 정도
- 50개 스킬이 있어도 ~5,000 단어만 사용

### Message 2: 선택 및 로드 (Selection & Loading)

```
사용자: "Docker 컨테이너 최적화 방법 알려줘"

Claude의 내부 판단:
1. 사용자 요청 분석
2. description과 매칭
3. skill-c가 관련 있음 판단
4. skill-c의 SKILL.md 본문 로드
```

**이 단계에서**:
- 관련 스킬의 본문만 로드 (~2,000 단어)
- 다른 스킬 본문은 로드하지 않음
- references/는 아직 로드하지 않음

### Message 3+: 필요 시 추가 로드

```
Claude가 SKILL.md를 읽은 후:
"상세한 최적화 패턴은 references/optimization.md 참조"

→ 필요하다고 판단하면 해당 파일 로드
→ 필요 없으면 로드하지 않음
```

## 컨텍스트 효율성 비교

### 시나리오: 50개 스킬, 각 평균 3,000 단어

**MCP 방식 (사전 로드)**:
```
50 스킬 × 3,000 단어 = 150,000 단어
→ 컨텍스트 윈도우 초과 가능
→ 정보 손실, 성능 저하
```

**Skills 방식 (Progressive Disclosure)**:
```
발견 단계: 50 × 100 = 5,000 단어
선택 단계: 1-2 × 2,000 = 4,000 단어
필요 시: references 일부 = 2,000 단어
─────────────────────────────
총: ~11,000 단어 (93% 절약)
```

## Description의 중요성

### 왜 description이 핵심인가?

```
발견 단계에서 Claude가 볼 수 있는 것:
┌──────────────────────────────────┐
│ name: my-skill                   │
│ description: [이 부분만 보임]      │
└──────────────────────────────────┘
         ↓
   "이 스킬이 필요한가?"
         ↓
    Yes → SKILL.md 로드
    No  → 스킬 무시
```

**description이 모호하면**:
- Claude가 관련성 판단 불가
- 스킬이 선택되지 않음
- 좋은 스킬도 사용되지 않음

### 좋은 description 패턴

```yaml
# 패턴 1: 구체적인 행동 + 트리거 구문
description: This skill should be used when the user asks to
"create a Docker container", "optimize Dockerfile",
"debug container issues", or mentions container orchestration.

# 패턴 2: 시나리오 기반
description: Docker 컨테이너 생성, Dockerfile 최적화,
컨테이너 디버깅 요청 시 사용. 활성화 키워드:
"Docker", "컨테이너", "이미지 빌드"

# 패턴 3: 질문 유형
description: This skill answers questions like
"How do I reduce Docker image size?",
"Why is my container slow?",
"What's the best base image for Node.js?"
```

### 나쁜 description 패턴

```yaml
# 너무 모호
description: Docker 관련 가이드를 제공합니다.

# 너무 범용적
description: 개발 관련 모든 질문에 답변합니다.

# 트리거 없음
description: 컨테이너화 모범 사례.

# 2인칭 사용
description: Use this when you need Docker help.
```

## SKILL.md 최적화

### 컨텐츠 배치 원칙

```
SKILL.md (2,000 단어 이하)
├── 핵심 개념 요약
├── 필수 워크플로우
├── 빠른 참조 테이블
└── references/ 포인터

references/ (무제한)
├── 상세 패턴
├── 고급 기법
├── 엣지 케이스
└── 종합 예시
```

### 로드 시점별 컨텐츠

| 로드 시점 | 컨텐츠 유형 | 예시 |
|----------|-----------|------|
| 항상 (description) | 발견 단서 | 트리거 구문, 핵심 키워드 |
| 트리거 시 (SKILL.md) | 필수 지식 | 워크플로우, 핵심 개념 |
| 필요 시 (references/) | 심화 지식 | 상세 패턴, API 문서 |

## 팀 온보딩 관점

스킬을 "새 팀원을 위한 온보딩 문서"로 생각하세요.

### 온보딩 문서 구조

```
신입 개발자 온보딩 가이드
├── "이 가이드는 언제 보나요?" → description
├── "핵심만 빠르게 알려주세요" → SKILL.md
├── "더 자세히 알고 싶어요" → references/
└── "실제 예시 보여주세요" → examples/
```

### 질문으로 구조 결정

1. **이 스킬이 언제 필요한가?** → description
2. **반드시 알아야 할 것은?** → SKILL.md 본문
3. **깊이 알고 싶으면?** → references/
4. **실제로 어떻게 하나?** → examples/

## MCP vs Skills 비교

| 측면 | MCP Servers | Agent Skills |
|------|-------------|--------------|
| 로딩 | 사전 로드 | 동적 로드 |
| 컨텍스트 | 항상 점유 | 필요 시만 |
| 적합한 경우 | 외부 API 통합 | 도메인 지식 |
| 확장성 | 제한적 | 높음 |
| 복잡도 | 프로토콜 필요 | 파일만 |

### 언제 무엇을 사용하나?

```
외부 시스템 연동 (API, DB) → MCP Server
도메인 지식 전달 → Skill
복잡한 워크플로우 → Skill + Agent
자동화 트리거 → Hook
```

## 실전 체크리스트

### 발견 가능성 (Discoverability)

- [ ] description에 구체적 트리거 구문 3-5개?
- [ ] 한국어/영어 키워드 모두 포함?
- [ ] 다른 스킬과 명확히 구분?
- [ ] 너무 범용적이지 않은가?
- [ ] 너무 특수적이지 않은가?

### 컨텍스트 효율성

- [ ] SKILL.md가 2,000 단어 이하?
- [ ] 상세 내용이 references/로 분리?
- [ ] 불필요한 정보 제거?
- [ ] 빠른 참조 테이블 포함?

### 팀 온보딩 관점

- [ ] 새 팀원이 이해할 수 있는 구조?
- [ ] "언제 보나요?" 명확?
- [ ] "더 알고 싶으면?" 경로 제공?

## 출처

- Anthropic Engineering Blog: "Equipping agents for the real world with Agent Skills"
- Claude API Documentation: Agent Skills Overview
- Lee Hanchung: "Claude Agent Skills: A First Principles Deep Dive"
