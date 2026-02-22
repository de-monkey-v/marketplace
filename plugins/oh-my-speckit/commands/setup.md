---
name: setup
description: "oh-my-speckit 대화형 설정 위자드. 전제조건 확인, 스폰 모드, 윈도우 모드 설정."
argument-hint: ""
allowed-tools: Bash, Read, Write, Glob, AskUserQuestion
---

# /oh-my-speckit:setup - Setup Wizard

oh-my-speckit 플러그인 대화형 설정 위자드.

---

## Step 1: 프로젝트 루트 탐색

cwd부터 상위로 올라가며 탐색:
1. `.specify/` - 기존 폴더가 있으면 **최우선**
2. `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`
3. `.git/` - 최후의 fallback

```
AskUserQuestion:
- question: "프로젝트 루트가 [탐색 경로]이 맞나요?"
- header: "프로젝트"
- options:
  - label: "예, 맞습니다 (권장)"
    description: "이 경로를 프로젝트 루트로 사용합니다"
  - label: "다른 경로 지정"
    description: "직접 프로젝트 루트 경로를 입력합니다"
```

탐색된 경로를 `PROJECT_ROOT`로 저장.

---

## Step 2: 전제조건 확인

아래 항목을 **순서대로 Bash로 확인**하고, 결과를 내부적으로 기록합니다.

### 2-1. tmux 설치

```
Bash: which tmux
```

- 찾으면 → `Bash: tmux -V` → 버전 기록, 상태 = OK
- 못 찾으면 → 상태 = FAIL

### 2-2. tmux 세션 확인

```
Bash: echo "$TMUX"
```

- 출력 있음 → 상태 = OK (tmux 세션 안에서 실행 중)
- 출력 없음 → 상태 = WARN (tmux 세션 밖에서 실행 중 — 경고만, 차단 아님)

### 2-3. Claude CLI 확인

```
Bash: which claude
```

- 찾으면 → 상태 = OK
- 못 찾으면 → 상태 = FAIL

### 2-4. Agent Teams 환경변수 확인

```
Bash: echo "$CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"
```

- `1`이면 → 상태 = OK
- 아니면 → 상태 = WARN

### 전제조건 결과 표시

```markdown
## 전제조건 확인

| 항목 | 상태 | 비고 |
|------|------|------|
| tmux | {OK/FAIL} | {버전 또는 "미설치 — `brew install tmux` 또는 `apt install tmux`"} |
| tmux 세션 | {OK/WARN} | {세션 안/밖} |
| Claude CLI | {OK/FAIL} | {경로 또는 "미설치"} |
| Agent Teams | {OK/WARN} | {"활성화" 또는 "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 설정 필요"} |
```

<instructions>
- FAIL 항목이 있으면 해결 방법을 안내합니다.
- tmux FAIL: OS에 맞는 설치 명령을 안내합니다 (`brew install tmux`, `sudo apt install tmux` 등).
- Claude CLI FAIL: `npm install -g @anthropic-ai/claude-code` 안내.
- Agent Teams WARN: `~/.claude/settings.json`의 `env`에 `"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"` 추가 안내.
- WARN만 있고 FAIL이 없으면 계속 진행합니다.
- FAIL이 있어도 계속 진행은 가능하지만, 해당 기능 사용 시 문제가 될 수 있음을 알립니다.
</instructions>

---

## Step 3: 기존 설정 확인

```
Read tool: ${PROJECT_ROOT}/.specify/config.json
```

<instructions>
- 파일이 존재하면 기존 값을 파싱하여 현재 설정으로 표시합니다:
  ```markdown
  기존 설정이 발견되었습니다:
  - 스폰 모드: {spawnGpt ? "GPT 모드" : "Claude 모드"}
  - 배치 모드: {spawnWindow ? "별도 윈도우" : "같은 윈도우"}
  ```
  이 값들을 아래 Step 4, 5에서 기본 선택(권장)으로 반영합니다.
- 파일이 없으면 기본값(`spawnGpt: false`, `spawnWindow: false`)으로 진행합니다.
</instructions>

---

## Step 4: 스폰 모드 설정 (spawnGpt)

```
AskUserQuestion:
- question: "팀메이트를 어떤 모델로 실행할까요?"
- header: "스폰 모드"
- options:
  - label: "Claude 모드 (권장)"
    description: "Claude CLI 네이티브 에이전트. 별도 설정 없이 바로 사용 가능"
  - label: "GPT 모드"
    description: "cli-proxy-api를 통해 GPT 모델 사용 (별도 설정 필요)"
```

<instructions>
- 기존 config에 `spawnGpt: true`가 설정되어 있으면, "GPT 모드"를 권장 옵션으로 변경합니다.
- Claude 선택 → `spawnGpt = false`
- GPT 선택 → `spawnGpt = true`

**GPT 모드 선택 시 추가 확인:**

```
Bash: which cli-proxy-api 2>/dev/null; echo "---"; which gpt-claude-code 2>/dev/null
```

확인 결과를 안내:
- cli-proxy-api 미설치 → `npm install -g cli-proxy-api` 안내
- gpt-claude-code 미설치 → `npm install -g gpt-claude-code` 안내
- 둘 다 설치됨 → "GPT 모드 전제조건 확인 완료" 표시
</instructions>

---

## Step 5: 윈도우 모드 설정 (spawnWindow)

```
AskUserQuestion:
- question: "팀메이트 배치 방식을 선택해주세요."
- header: "배치 모드"
- options:
  - label: "같은 윈도우 (권장)"
    description: "리더 윈도우에 pane 분할로 배치. 한 화면에서 모든 팀메이트 확인"
  - label: "별도 윈도우"
    description: "팀메이트를 별도 tmux 윈도우에 배치. 화면이 넓을 때 유용"
```

<instructions>
- 기존 config에 `spawnWindow: true`가 설정되어 있으면, "별도 윈도우"를 권장 옵션으로 변경합니다.
- 같은 윈도우 선택 → `spawnWindow = false`
- 별도 윈도우 선택 → `spawnWindow = true`
</instructions>

---

## Step 5.5: Subagent 활용 가이드 Rules 생성

팀메이트가 자동으로 subagent 활용 가이드를 참조하도록 `.claude/rules/` 파일을 생성합니다.

```
AskUserQuestion:
- question: "팀메이트용 subagent 활용 가이드를 생성할까요? (.claude/rules/에 저장되어 모든 팀메이트가 자동으로 참조합니다)"
- header: "Subagent 가이드"
- options:
  - label: "생성 (권장)"
    description: ".claude/rules/oh-my-speckit-subagent-guide.md 생성. 팀메이트가 복잡한 작업에서 전문 subagent를 적극 활용합니다."
  - label: "건너뛰기"
    description: "Rules 파일을 생성하지 않습니다. 팀메이트가 에이전트 정의의 subagents 섹션만 참조합니다."
```

<instructions>

**"생성" 선택 시:**

1. 프로젝트 스택을 감지합니다 (Phase 1의 Step 2.7 프레임워크 감지와 동일한 로직):

```
Glob: pom.xml, build.gradle, build.gradle.kts → Java/Spring 프로젝트
Glob: next.config.*, nuxt.config.* → 메타프레임워크
Grep: package.json → "@nestjs/core", "react", "vue", "fastapi"
Grep: requirements.txt, pyproject.toml → "fastapi", "django", "flask"
```

2. 감지 결과에 따라 **프로젝트에 관련된 subagent만 포함**한 Rules 파일을 생성합니다.

**Rules 파일 템플릿:**

```markdown
# Subagent 활용 가이드

이 프로젝트의 팀메이트는 복잡한 작업에서 Task tool로 전문 subagent를 스폰하여 분석을 위임할 수 있습니다.

## 활용 원칙

- **복잡한 작업에서만 사용**: 단순 CRUD, 기본 스타일링, 기본 유닛 테스트에는 subagent 없이 직접 수행
- **병렬 스폰 권장**: 독립적인 분석 작업이 여러 개면 Task tool을 병렬로 호출
- **결과 통합**: subagent 분석 결과를 참고하되, 최종 코드 작성은 본인이 수행

## 역할별 사용 가능 Subagent

### 구현 담당 (developer / implementer)
| Subagent | Agent Type | 활용 시점 |
|----------|-----------|----------|
| DB Architect | `claude-team:db-architect` | DB 스키마 설계, 쿼리 최적화, 마이그레이션 |
| API Designer | `claude-team:api-designer` | REST/GraphQL API 계약 설계, 엔드포인트 구조 |
| Security Architect | `claude-team:security-architect` | 인증/인가 플로우, 보안 감사 |
| Domain Modeler | `claude-team:domain-modeler` | DDD 모델링, Aggregate 설계, Bounded Context |

{FRONTEND_SECTION}

{BACKEND_SECTION}

### 테스트 담당 (qa / tester)
| Subagent | Agent Type | 활용 시점 |
|----------|-----------|----------|
| Test Strategist | `claude-team:test-strategist` | 테스트 아키텍처, 커버리지 전략 |
| Integration Tester | `claude-team:integration-tester` | API 통합 테스트, 계약 테스트 |
| FE Tester | `claude-team:fe-tester` | 컴포넌트 테스트, E2E, 비주얼 리그레션 |
| Side Effect Analyzer | `claude-team:side-effect-analyzer` | 변경 영향 분석, 리그레션 위험 평가 |

## 스폰 예시

```
Task tool:
- subagent_type: "claude-team:db-architect"
- description: "스키마 설계 분석"
- prompt: "현재 스키마를 분석하고 {구체적 질문}에 대해 권장 사항을 제시해주세요."
```

**병렬 스폰 예시 (독립적인 분석 여러 개):**
하나의 메시지에서 여러 Task tool을 동시에 호출하세요.
```

3. 템플릿의 `{FRONTEND_SECTION}`, `{BACKEND_SECTION}`은 감지 결과에 따라:

**프론트엔드 감지됨 → FRONTEND_SECTION:**
```markdown
### 프론트엔드 담당 (frontend-dev / frontend)
| Subagent | Agent Type | 활용 시점 |
|----------|-----------|----------|
| CSS Architect | `claude-team:css-architect` | 디자인 시스템, 복잡한 레이아웃, CSS 전략 |
| A11y Auditor | `claude-team:a11y-auditor` | WCAG 접근성 감사, 스크린 리더 호환 |
| State Designer | `claude-team:state-designer` | 복잡한 상태 관리 아키텍처, 스토어 설계 |
| FE Performance | `claude-team:fe-performance` | 번들 분석, 렌더링 최적화, Core Web Vitals |
| FE Tester | `claude-team:fe-tester` | 컴포넌트 테스트 전략, 비주얼 리그레션 |
```

**프론트엔드 미감지 → FRONTEND_SECTION 제거**

**백엔드 감지됨 → BACKEND_SECTION:**
```markdown
### 백엔드 담당 (backend-dev / backend)
| Subagent | Agent Type | 활용 시점 |
|----------|-----------|----------|
| DB Architect | `claude-team:db-architect` | DB 스키마 설계, 쿼리 최적화, 마이그레이션 |
| API Designer | `claude-team:api-designer` | REST/GraphQL API 계약 설계, 엔드포인트 구조 |
| Security Architect | `claude-team:security-architect` | 인증/인가 아키텍처, 보안 감사 |
| Integration Tester | `claude-team:integration-tester` | API 통합 테스트 전략, 계약 테스트 |
```

**백엔드 미감지 → BACKEND_SECTION 제거**

**둘 다 미감지 → "구현 담당" 섹션만 유지 (범용)**

4. `GENERATE_RULES = true` 기록

**"건너뛰기" 선택 시:**
- `GENERATE_RULES = false` 기록
- 아무 파일도 생성하지 않음

</instructions>

---

## Step 6: 저장

<instructions>

**디렉토리 생성:**

```
Bash: mkdir -p ${PROJECT_ROOT}/.specify/memory && mkdir -p ${PROJECT_ROOT}/.specify/specs
```

**config.json 저장:**

```
Write tool:
- file_path: ${PROJECT_ROOT}/.specify/config.json
- content: {spawnGpt, spawnWindow 값을 포함한 JSON}
```

JSON 형식:
```json
{
  "spawnGpt": false,
  "spawnWindow": false
}
```

- 기존 config.json이 있고 추가 필드가 있었다면, 해당 필드를 유지하면서 `spawnGpt`와 `spawnWindow`만 업데이트합니다.

**Rules 파일 저장 (GENERATE_RULES = true인 경우만):**

```
Bash: mkdir -p ${PROJECT_ROOT}/.claude/rules
Write tool:
- file_path: ${PROJECT_ROOT}/.claude/rules/oh-my-speckit-subagent-guide.md
- content: {Step 5.5에서 조립한 Rules 템플릿}
```

</instructions>

---

## Step 7: 요약 + 다음 단계 안내

```markdown
## oh-my-speckit Setup 완료

| 항목 | 상태 |
|------|------|
| 프로젝트 루트 | {PROJECT_ROOT} |
| tmux | {OK — 버전 / FAIL — 미설치} |
| tmux 세션 | {OK / WARN — 세션 밖} |
| Claude CLI | {OK / FAIL — 미설치} |
| Agent Teams | {OK / WARN — 미설정} |
| 스폰 모드 | {Claude 모드 / GPT 모드} |
| 배치 모드 | {같은 윈도우 / 별도 윈도우} |
| Subagent 가이드 | {생성됨 / 건너뜀} |

### 설정 파일
- `{PROJECT_ROOT}/.specify/config.json`
- `{PROJECT_ROOT}/.claude/rules/oh-my-speckit-subagent-guide.md` (Subagent 가이드 생성 시)

### 다음 단계
1. 프로젝트 원칙 분석: `/oh-my-speckit:constitution`
2. 기능 스펙 작성: `/oh-my-speckit:specify [기능 설명]`
3. 설정 변경: `/oh-my-speckit:setup`
```
