# Claude Code 서브에이전트 공식 문서

> 원본: https://code.claude.com/docs/ko/sub-agents
> 최종 업데이트: 2026-01-26

---

# 사용자 정의 서브에이전트 만들기

> Claude Code에서 작업별 워크플로우 및 향상된 컨텍스트 관리를 위해 특화된 AI 서브에이전트를 만들고 사용합니다.

서브에이전트는 특정 유형의 작업을 처리하는 특화된 AI 어시스턴트입니다. 각 서브에이전트는 자신의 컨텍스트 윈도우에서 실행되며 사용자 정의 시스템 프롬프트, 특정 도구 액세스 및 독립적인 권한을 가집니다.

서브에이전트는 다음을 도와줍니다:

* **컨텍스트 보존** - 탐색 및 구현을 주 대화에서 분리하여 유지
* **제약 조건 적용** - 서브에이전트가 사용할 수 있는 도구 제한
* **구성 재사용** - 사용자 수준 서브에이전트를 통해 프로젝트 간 재사용
* **동작 특화** - 특정 도메인을 위한 집중된 시스템 프롬프트
* **비용 제어** - Haiku와 같은 더 빠르고 저렴한 모델로 작업 라우팅

## 기본 제공 서브에이전트

### Explore

코드베이스 검색 및 분석에 최적화된 빠른 읽기 전용 에이전트입니다.

* **모델**: Haiku (빠름, 낮은 지연시간)
* **도구**: 읽기 전용 도구 (Write 및 Edit 도구에 대한 액세스 거부)
* **목적**: 파일 검색, 코드 검색, 코드베이스 탐색

### Plan

계획 모드에서 계획을 제시하기 전에 컨텍스트를 수집하는 데 사용되는 연구 에이전트입니다.

* **모델**: 주 대화에서 상속
* **도구**: 읽기 전용 도구
* **목적**: 계획을 위한 코드베이스 연구

### General-purpose

탐색과 작업 모두를 필요로 하는 복잡한 다단계 작업을 위한 유능한 에이전트입니다.

* **모델**: 주 대화에서 상속
* **도구**: 모든 도구
* **목적**: 복잡한 연구, 다단계 작업, 코드 수정

## 빠른 시작: 첫 번째 서브에이전트 만들기

서브에이전트는 YAML 프론트매터가 있는 마크다운 파일로 정의됩니다.

### 1. 서브에이전트 인터페이스 열기

```
/agents
```

### 2. 새 사용자 수준 에이전트 만들기

**Create new agent**를 선택한 다음 **User-level**을 선택합니다.

### 3. Claude로 생성

**Generate with Claude**를 선택하고 서브에이전트를 설명합니다:

```
A code improvement agent that scans files and suggests improvements
for readability, performance, and best practices. It should explain
each issue, show the current code, and provide an improved version.
```

### 4. 도구 선택

읽기 전용 검토자의 경우 **Read-only tools**를 제외한 모든 항목을 선택 해제합니다.

### 5. 모델 선택

**Sonnet**을 선택합니다.

### 6. 저장 및 시도

```
Use the code-improver agent to suggest improvements in this project
```

## 서브에이전트 구성

### 서브에이전트 범위 선택

| 위치                   | 범위            | 우선순위   |
| :------------------- | :------------ | :----- |
| `--agents` CLI 플래그   | 현재 세션         | 1 (최고) |
| `.claude/agents/`    | 현재 프로젝트       | 2      |
| `~/.claude/agents/`  | 모든 프로젝트       | 3      |
| 플러그인의 `agents/` 디렉토리 | 플러그인이 활성화된 위치 | 4 (최저) |

### 서브에이전트 파일 작성

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

### 지원되는 프론트매터 필드

| 필드                | 필수  | 설명                                                                                                           |
| :---------------- | :-- | :----------------------------------------------------------------------------------------------------------- |
| `name`            | 예   | 소문자 및 하이픈을 사용한 고유 식별자                                                                                        |
| `description`     | 예   | Claude가 이 서브에이전트에 위임해야 할 때                                                                                   |
| `tools`           | 아니오 | 서브에이전트가 사용할 수 있는 도구. 생략하면 모든 도구 상속                                                                           |
| `disallowedTools` | 아니오 | 거부할 도구                                                                                                       |
| `model`           | 아니오 | 사용할 모델: `sonnet`, `opus`, `haiku`, 또는 `inherit`. 기본값은 `sonnet`                                               |
| `permissionMode`  | 아니오 | 권한 모드: `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, 또는 `plan`                                   |
| `skills`          | 아니오 | 시작 시 서브에이전트의 컨텍스트에 로드할 스킬                                                                                    |
| `hooks`           | 아니오 | 이 서브에이전트로 범위가 지정된 라이프사이클 훅                                                                                   |

### 모델 선택

* **모델 별칭**: `sonnet`, `opus`, 또는 `haiku`
* **inherit**: 주 대화와 동일한 모델 사용
* **생략됨**: 기본 모델 사용 (`sonnet`)

### 권한 모드

| 모드                  | 동작                                   |
| :------------------ | :----------------------------------- |
| `default`           | 프롬프트를 사용한 표준 권한 확인                   |
| `acceptEdits`       | 파일 편집 자동 수락                          |
| `dontAsk`           | 권한 프롬프트 자동 거부                        |
| `bypassPermissions` | 모든 권한 확인 건너뛰기                        |
| `plan`              | 계획 모드 (읽기 전용 탐색)                     |

### 서브에이전트에 스킬 미리 로드

```yaml
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---

Implement API endpoints. Follow the conventions and patterns from the preloaded skills.
```

### 훅을 사용한 조건부 규칙

```yaml
---
name: db-reader
description: Execute read-only database queries
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---
```

### 특정 서브에이전트 비활성화

설정의 `deny` 배열에 서브에이전트를 추가:

```json
{
  "permissions": {
    "deny": ["Task(Explore)", "Task(my-custom-agent)"]
  }
}
```

## 서브에이전트에 대한 훅 정의

### 서브에이전트 프론트매터의 훅

```yaml
---
name: code-reviewer
description: Review code changes with automatic linting
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh $TOOL_INPUT"
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/run-linter.sh"
---
```

### 서브에이전트 이벤트에 대한 프로젝트 수준 훅

```json
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "db-agent",
        "hooks": [
          { "type": "command", "command": "./scripts/setup-db-connection.sh" }
        ]
      }
    ],
    "SubagentStop": [
      {
        "matcher": "db-agent",
        "hooks": [
          { "type": "command", "command": "./scripts/cleanup-db-connection.sh" }
        ]
      }
    ]
  }
}
```

## 서브에이전트 작업

### 자동 위임 이해

Claude는 요청의 작업 설명, 서브에이전트의 `description` 필드 및 현재 컨텍스트를 기반으로 자동으로 작업을 위임합니다.

### 서브에이전트를 포그라운드 또는 백그라운드에서 실행

* **포그라운드 서브에이전트**: 완료될 때까지 주 대화를 차단합니다.
* **백그라운드 서브에이전트**: 동시에 실행됩니다. MCP 도구는 백그라운드 서브에이전트에서 사용할 수 없습니다.

### 일반적인 패턴

#### 대량 작업 격리

```
Use a subagent to run the test suite and report only the failing tests with their error messages
```

#### 병렬 연구 실행

```
Research the authentication, database, and API modules in parallel using separate subagents
```

#### 서브에이전트 연결

```
Use the code-reviewer subagent to find performance issues, then use the optimizer subagent to fix them
```

### 서브에이전트와 주 대화 중 선택

**주 대화 사용**:
* 빈번한 왕복 또는 반복적 개선이 필요한 경우
* 여러 단계가 상당한 컨텍스트를 공유하는 경우
* 빠르고 대상이 지정된 변경을 수행하는 경우

**서브에이전트 사용**:
* 주 컨텍스트에 필요하지 않은 자세한 출력을 생성하는 경우
* 특정 도구 제한 또는 권한을 적용하려는 경우
* 작업이 자체 포함되어 있고 요약을 반환할 수 있는 경우

> **참고**: 서브에이전트는 다른 서브에이전트를 생성할 수 없습니다.

### 서브에이전트 재개

재개된 서브에이전트는 모든 이전 도구 호출, 결과 및 추론을 포함한 전체 대화 기록을 유지합니다:

```
Use the code-reviewer subagent to review the authentication module
[Agent completes]

Continue that code review and now analyze the authorization logic
[Claude resumes the subagent with full context from previous conversation]
```

## 예제 서브에이전트

### 코드 검토자

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented
- Good test coverage
- Performance considerations addressed
```

### 디버거

```markdown
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works
```

### 데이터 과학자

```markdown
---
name: data-scientist
description: Data analysis expert for SQL queries, BigQuery operations, and data insights.
tools: Bash, Read, Write
model: sonnet
---

You are a data scientist specializing in SQL and BigQuery analysis.

When invoked:
1. Understand the data analysis requirement
2. Write efficient SQL queries
3. Use BigQuery command line tools (bq) when appropriate
4. Analyze and summarize results
5. Present findings clearly
```

### 데이터베이스 쿼리 검증자

```markdown
---
name: db-reader
description: Execute read-only database queries. Use when analyzing data or generating reports.
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---

You are a database analyst with read-only access. Execute SELECT queries to answer questions about the data.
```

## 다음 단계

* **플러그인으로 서브에이전트 배포** - 팀 또는 프로젝트 간 서브에이전트 공유
* **Claude Code를 프로그래밍 방식으로 실행** - CI/CD 및 자동화를 위해 Agent SDK 사용
* **MCP 서버 사용** - 서브에이전트에 외부 도구 및 데이터에 대한 액세스 제공
