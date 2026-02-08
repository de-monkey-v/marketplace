# Sub-agents (서브에이전트)

## 검색 키워드
`subagent`, `서브에이전트`, `Task tool`, `병렬 실행`, `에이전트 오케스트레이션`, `harness`, `컨텍스트 격리`

---

## [Create custom subagents](https://code.claude.com/docs/en/sub-agents)

**포함 주제**: Sub-agent 개념, Task 도구, 병렬 실행, 컨텍스트 격리

### Sub-agents 개념
- 특정 작업에 대해 **격리된 컨텍스트**를 유지하며 동작하는 독립적인 에이전트
- 여러 sub-agent를 **병렬로 실행**하여 복잡한 워크플로우 처리 속도 향상
- 각 sub-agent는 독립적인 컨텍스트로 정보 과부하 방지

### Task 도구를 통한 호출
- Sub-agents는 **Task 도구**를 통해 호출
- Claude가 작업과 각 sub-agent의 설명을 기반으로 **자동 선택**
- 프롬프트에서 특정 sub-agent 이름을 명시하여 호출 가능

### 병렬 실행
- Task 도구는 **최대 7개**의 agent를 동시에 실행 가능
- 커스텀 시스템 프롬프트로 각 sub-agent에 특화된 지식/제약 부여

### 제약사항
- **에이전트는 다른 에이전트를 직접 호출할 수 없음**
- Task tool은 allowedTools에 포함되어야 sub-agents 호출 가능
- 오케스트레이션은 메인 세션 또는 커맨드에서만 가능

---

## [Building agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)

**포함 주제**: SDK 설계 원리, 에이전트 루프 패턴, 도구 생태계

### 핵심 설계 원리
- 에이전트에게 "컴퓨터"를 제공하여 **인간처럼 작업**하도록 함
- Bash 명령어 실행, 파일 편집, CSV 읽기, 웹 검색 등 범용 디지털 작업 수행

### 에이전트 루프 패턴
```
컨텍스트 수집 → 행동 실행 → 작업 검증 → 반복
```
- 금융 자문, 여행 예약, 고객 지원 등 다양한 사용 사례 구현

### 자동 컴팩션
- 컨텍스트 한계에 접근할 때 이전 메시지들을 **자동으로 요약**
- 컨텍스트 부족 현상 방지

### 세션 관리 API
- 대화 상태 유지
- 이전 세션에서 정확히 중단된 지점에서 재개 가능

---

## [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

**포함 주제**: Agent Harness 개념, 장시간 실행 도전, 세션 연속성

### Agent Harness 개념
- AI 모델을 감싸는 인프라로서 **장시간 작업을 관리**
- OS처럼 작동:
  - 컨텍스트 정리
  - 부팅 시퀀스 (프롬프트, 훅) 처리
  - 표준 드라이버 (도구 처리) 제공

### 장시간 실행의 핵심 도전
- **문제**: 별도 세션으로 작동하며 각 새 세션은 이전 작업에 대한 메모리 없음
- **Anthropic 솔루션**: 초기화 에이전트 + 코딩 에이전트 이층 구조
- **상태 전달**: `claude-progress.txt` 로그로 세션 간 상태 관리

### 2026년 Agent Harness의 역할
- 2024년: 복잡한 수동 파이프라인 필요
- 2026년: 단일 컨텍스트 윈도우 프롬프트로 처리
- **새로운 병목**: 컨텍스트 내구성
- Harness가 **모델 드리프트 해결**의 주요 도구

---

## Task 도구 사용 예시

```typescript
// Task 도구로 sub-agent 호출
{
  "subagent_type": "Explore",
  "description": "코드베이스 구조 분석",
  "prompt": "src/ 폴더의 아키텍처를 분석해줘",
  "model": "haiku",  // 선택: haiku, sonnet, opus
  "run_in_background": true  // 선택: 백그라운드 실행
}
```

### 주요 파라미터
| 파라미터 | 설명 |
|----------|------|
| `subagent_type` | 에이전트 유형 선택 |
| `prompt` | 작업 지시 |
| `model` | haiku, sonnet, opus 선택 |
| `run_in_background` | 백그라운드 실행 여부 |
| `resume` | 이전 에이전트 재개용 ID |
