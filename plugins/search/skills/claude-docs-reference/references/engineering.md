# Anthropic Engineering Blog

## 검색 키워드
`best practices`, `베스트 프랙티스`, `샌드박싱`, `도구 작성`, `평가`, `evals`, `컨텍스트 엔지니어링`, `멀티 에이전트`

---

## [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

**포함 주제**: 컨텍스트 관리, 멀티 에이전트 패턴, 워크플로우 최적화

### 컨텍스트 윈도우 관리
- Claude의 컨텍스트 윈도우는 빠르게 채워짐 → 적극적 관리 필요
- CLAUDE.md와 폴더별 오버라이드 활용
- 자주 `/clear` 명령으로 컨텍스트 초기화

### 멀티 에이전트 패턴
- 한 Claude가 코드 작성, 다른 Claude가 검토
- 신선한 컨텍스트에서 더 객관적인 검토 가능

### 워크플로우 팁
```
1. 계획 → 작은 변경 → 테스트 → 검토 순서 준수
2. 검증 기준 명확히 설정 (테스트, 스크린샷)
3. 탐색(explore) → 계획(plan) → 구현(code) 단계 분리
4. @파일 참조, 이미지 붙여넣기로 풍부한 정보 제공
```

---

## [Claude Code Sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)

**포함 주제**: OS 수준 보안 격리, 권한 요청 감소, 샌드박스 런타임

### 샌드박싱의 목적
- 사전 정의된 경계 내에서 Claude가 자유롭게 작동
- 매 작업마다 권한 승인 요청 불필요 → **권한 프롬프트 84% 감소**

### 보안 아키텍처
| 격리 유형 | 설명 |
|----------|------|
| 파일시스템 격리 | 현재 작업 디렉토리 읽기/쓰기 허용, 외부 차단 |
| 네트워크 격리 | Unix socket 프록시, 도메인별 접근 제어 |

### 명령어
```bash
/sandbox       # OS 레벨 격리 활성화
/permissions   # 안전한 명령어 사전 승인
```

---

## [Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents)

**포함 주제**: 에이전트용 도구 설계, 평가 프레임워크, 도구 최적화

### 도구란?
- 결정론적 시스템과 비결정론적 에이전트 간의 **계약(contract)**
- 에이전트의 "인체공학성(ergonomics)" 고려 필요

### 효과적인 도구 작성 원칙

| 원칙 | 설명 |
|------|------|
| 올바른 도구 선택 | `list_contacts` 대신 `search_contacts` |
| 네임스페이싱 | `asana_search`, `asana_projects_search` |
| 의미 있는 응답 | uuid 대신 name, image_url 사용 |
| 토큰 효율성 | 페이지네이션, 필터링 (기본 25,000토큰 제한) |

### 평가 기반 개선
```
프로토타입 → 평가 실행 → 결과 분석 → 에이전트와 협력하여 개선
```

---

## [Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use)

**포함 주제**: 동적 도구 발견, 프로그래매틱 도구 호출, 확장 가능한 도구 라이브러리

### 세 가지 핵심 기능

**Tool Search Tool**
- 동적이고 온디맨드 도구 발견
- 모든 도구를 사전 로드하지 않음

**프로그래매틱 도구 호출**
- Claude가 여러 도구를 호출하는 코드 작성
- 중간 결과로 컨텍스트 채우지 않음

**도구 활용 예시**
- 도구 스키마만으로는 부족
- 실제 호출 예시로 올바른 사용법 시연

---

## [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

**포함 주제**: 평가 정의 및 설계, 단일/멀티 턴 평가, 자동화된 그래이딩

### 평가란?
- 입력 제공 → 그래이딩 로직으로 출력 측정
- 문제와 행동 변화를 사용자에게 영향 주기 전에 가시화

### 평가 유형
| 유형 | 특징 |
|------|------|
| 단일 턴 평가 | 프롬프트 → 응답 → 그래이딩 |
| 멀티 턴 평가 | 여러 턴의 상호작용 |
| 대화형 평가 | LLM 기반 사용자 시뮬레이션 |

### 메트릭 추적
- 정확도 + 런타임 + 도구 호출 수 + 토큰 소비량

---

## [Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**포함 주제**: 컨텍스트 부패, 장기 작업 전략, 동적 컨텍스트 검색

### 컨텍스트 엔지니어링이란?
- 프롬프트 엔지니어링의 자연스러운 진화
- 추론 중 **최적 토큰 세트 선택 및 유지**

### 컨텍스트 부패 (Context Rot)
- 컨텍스트 윈도우가 커질수록 정보 정확도 저하
- 트랜스포머 아키텍처의 n² 쌍 관계로 인한 주의력 분산

### 효과적인 컨텍스트 구성

| 요소 | 전략 |
|------|------|
| 시스템 프롬프트 | 명확하고 직접적, 적절한 추상화 수준 |
| 도구 | 최소 실행 가능 세트, 중복 제거 |
| 예시 | 정제된 정경(canonical) 예시 |
| 메시지 히스토리 | 동적 관리, 관련성 높은 정보만 유지 |

### 장기 작업 전략

| 전략 | 적합한 상황 |
|------|------------|
| 컴팩션 | 대화형 워크플로우 |
| 구조화된 노트 작성 | 명확한 마일스톤이 있는 반복 개발 |
| 서브 에이전트 아키텍처 | 복잡한 연구/분석 병렬 처리 |

### Just-in-Time 컨텍스트
- 사전 처리가 아닌 **런타임 동적 로드**
- 파일 경로, 쿼리, 링크 등 경량 식별자 유지
- Claude Code: bash 명령어(head, tail, grep)로 대용량 데이터 분석

---

## 종합 비교표

| 문서 | 초점 | 핵심 해결책 |
|------|------|------------|
| Best Practices | 개발 워크플로우 | CLAUDE.md, /clear, 멀티에이전트 |
| Sandboxing | 보안 및 자동화 | OS 레벨 격리, 사전 승인 |
| Writing Tools | 도구 설계 | 명확한 설명, 평가 기반 최적화 |
| Advanced Tool Use | 확장성 | 동적 발견, 프로그래매틱 호출 |
| Evals | 품질 보증 | 멀티 턴 평가, 자동 그래이딩 |
| Context Engineering | 장기 작업 | 컴팩션, 노트 작성, 서브에이전트 |
