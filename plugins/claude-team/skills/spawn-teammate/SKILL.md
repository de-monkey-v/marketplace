---
name: spawn-teammate
description: "팀메이트 스폰. GPT 모드(cli-proxy-api) 또는 Claude 네이티브 모드(--agent-type)로 팀메이트를 생성합니다."
version: 3.0.0
---

# Teammate Spawn Skill

팀메이트를 tmux pane으로 스폰하는 절차를 제공합니다.
이 스킬을 로드한 커맨드(specify, implement, verify 등)가 절차에 따라 팀메이트를 스폰합니다.

**두 가지 모드를 지원합니다:**
- **GPT 모드** (기존): `--agent-type` 없이 호출 → cli-proxy-api를 통해 GPT-5.3 Codex로 실행
- **Claude 모드** (신규): `--agent-type {plugin}:{agent}` 지정 → Claude CLI 네이티브로 실행

## 인자 형식

```
{member-name} --team {team-name} [--agent-type {plugin}:{agent}] [--model {model}] [--color {color}] [--window]
```

- `member-name`: 팀메이트 이름 (예: `pm`, `developer`, `qa`) — **필수**
- `--team`: 팀 이름 — **필수**
- `--agent-type`: 에이전트 타입 (예: `claude-team:implementer`) — 지정 시 Claude 모드
- `--model`: 모델 오버라이드 (기본값: 에이전트별 기본 모델)
- `--color`: 색상 오버라이드 (기본값: 에이전트별 기본 색상)
- `--window`: 별도 윈도우 모드. 리더 윈도우가 아닌 별도 tmux 윈도우에 배치 (윈도우당 최대 2명, 수평 분할)

**모드 감지**: `--agent-type` 있으면 **Claude 모드**, 없으면 **GPT 모드**

파싱 예시:
```
"pm --team specify-001"
→ GPT 모드: NAME="pm", TEAM="specify-001"

"developer --team impl-003 --agent-type claude-team:implementer"
→ Claude 모드: NAME="developer", TEAM="impl-003", AGENT_TYPE="claude-team:implementer"

"developer --team impl-003 --agent-type claude-team:implementer --model sonnet --color #0066CC"
→ Claude 모드 + 오버라이드: NAME="developer", TEAM="impl-003", AGENT_TYPE="claude-team:implementer", MODEL="sonnet", COLOR="#0066CC"

"developer --team impl-003 --agent-type claude-team:implementer --window"
→ Claude 모드 + 윈도우 모드: NAME="developer", TEAM="impl-003", AGENT_TYPE="claude-team:implementer", WINDOW_MODE=true
```

## 에이전트별 기본값 테이블

`--model` 또는 `--color` 미지정 시 에이전트 파일의 기본값을 사용합니다:

| Agent | Icon | Model | Color | 특성 |
|-------|------|-------|-------|------|
| Leader | 👑 | - | - | 팀 리더 |
| | | | | **읽기 전용 — 분석/설계** |
| `architect` | 🔵 | sonnet | #CC6600 | 아키텍처 분석/설계 |
| `reviewer` | 🔵 | sonnet | #8800CC | 코드 리뷰 |
| `a11y-auditor` | 🔵 | sonnet | #3498DB | 접근성 감사 (WCAG 2.2) |
| `api-designer` | 🔵 | sonnet | #1E90FF | API 설계 (REST/GraphQL/gRPC) |
| `db-architect` | 🔵 | sonnet | #2E8B57 | DB 설계 |
| `ddd-strategist` | 🔵 | sonnet | #8B0000 | DDD 전략 설계 |
| `fe-performance` | 🔵 | sonnet | #F39C12 | 프론트엔드 성능 분석 |
| `security-architect` | 🔵 | sonnet | #DC143C | 보안 아키텍처 |
| `side-effect-analyzer` | 🔵 | sonnet | #FF4500 | 사이드이펙트/파급효과 분석 |
| `state-designer` | 🔵 | sonnet | #E67E22 | 상태 관리 설계 |
| `test-strategist` | 🔵 | sonnet | #32CD32 | 테스트 전략 수립 |
| `ui-architect` | 🔵 | sonnet | #9B59B6 | UI 아키텍처 설계 |
| | | | | **읽기 전용 — 웹 검색/태스크/특수** |
| `planner` | 🔵 | sonnet | #FF6699 | 제품 기획/요구사항 분석 (+ 웹 검색) |
| `researcher` | 🔵 | sonnet | #00AACC | 기술 리서치 (+ 웹 검색) |
| `coordinator` | 🔵 | sonnet | #FFAA00 | 태스크 조율 (+ 태스크 관리) |
| `team-architect` | 🔵 | sonnet | cyan | Teammates 구성 설계 (+ AskUserQuestion) |
| | | | | **읽기+쓰기 — 구현** |
| `implementer` | 🔵 | sonnet | #0066CC | 코드 구현 |
| `backend` | 🔵 | sonnet | #0066CC | 백엔드/API |
| `frontend` | 🔵 | sonnet | #FF6600 | 프론트엔드/UI |
| `tester` | 🔵 | sonnet | #00AA44 | 테스트/검증 |
| `css-architect` | 🔵 | sonnet | #A855F7 | CSS 아키텍처 구현 |
| `domain-modeler` | 🔵 | sonnet | #B22222 | 도메인 모델 구현 |
| `event-architect` | 🔵 | sonnet | #FF6347 | 이벤트 아키텍처 구현 |
| `fastapi-expert` | 🔵 | sonnet | #009688 | FastAPI 전문가 |
| `fe-tester` | 🔵 | sonnet | #16A34A | 프론트엔드 테스트 |
| `i18n-specialist` | 🔵 | sonnet | #0EA5E9 | 국제화 |
| `integration-tester` | 🔵 | sonnet | #228B22 | 통합/E2E 테스트 |
| `migration-strategist` | 🔵 | sonnet | #DAA520 | 마이그레이션 전문가 |
| `nestjs-expert` | 🔵 | sonnet | #E0234E | NestJS 전문가 |
| `nextjs-expert` | 🔵 | sonnet | #000000 | Next.js 전문가 |
| `nuxt-expert` | 🔵 | sonnet | #00DC82 | Nuxt 3 전문가 |
| `react-expert` | 🔵 | sonnet | #61DAFB | React 전문가 |
| `spring-expert` | 🔵 | sonnet | #6DB33F | Spring Boot 전문가 |
| `vue-expert` | 🔵 | sonnet | #42B883 | Vue 3 전문가 |
| | | | | **특수 — 외부 LLM 프록시** |
| `codex` | 🔵 | sonnet | #10A37F | Codex CLI 프록시 |
| `gemini` | 🔵 | sonnet | #4285F4 | Gemini CLI 프록시 |

GPT 모드 기본값: `model=opus` (→ gpt-5.3-codex(xhigh) 매핑), `color=#10A37F`, `icon=🤖`

## 스폰 절차

스폰은 단일 스크립트 호출로 수행됩니다. 스크립트가 전제조건 확인, pane 생성, config 등록, 헬스체크를 모두 처리합니다.

### 1. 인자 파싱

스킬 args에서 변수를 파싱합니다. 첫 번째 토큰이 `member-name`, 나머지는 `--key value` 형식입니다.

### 2. 스크립트 실행

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/spawn-teammate/scripts/spawn.sh" \
  --name "${NAME}" --team "${TEAM}" \
  --agent-type "${AGENT_TYPE}" \
  --model "${MODEL}" --color "${COLOR}" --window
```

**옵션 전달 규칙:**
- `--name`과 `--team`은 항상 전달 (필수)
- `--agent-type`은 파싱된 값이 있을 때만 전달 (없으면 GPT 모드)
- `--model`, `--color`는 파싱된 값이 있을 때만 전달 (없으면 에이전트 기본값 사용)
- `--window`는 플래그이므로 값 없이 전달 (파싱되었을 때만)

### 3. 출력 해석

스크립트가 성공하면 stdout에 key=value 쌍을 출력합니다:

```
MODE=claude          # 또는 "gpt"
PANE_ID=%42          # tmux pane ID
NAME=developer       # 팀메이트 이름
TEAM=impl-003        # 팀 이름
MODEL=sonnet         # 사용된 모델
COLOR=#0066CC        # 사용된 색상
STATUS=ok            # 항상 "ok"
WINDOW_NAME=dev+test # --window일 때만 출력
```

**에러 시:** stderr에 한국어 에러 메시지가 출력되고 exit code 1로 종료됩니다. 에러 메시지를 사용자에게 그대로 전달하세요.

### 4. 스폰 완료 메시지 표시

스크립트 출력의 key=value를 사용하여 완료 메시지를 표시합니다:

GPT 모드:
```markdown
GPT 팀메이트 스폰 완료: ${NAME} (Team: ${TEAM})
- Model: GPT-5.3 Codex (xhigh) via cli-proxy-api
- Pane: ${PANE_ID}
```

Claude 모드:
```markdown
Claude 팀메이트 스폰 완료: ${NAME} (Team: ${TEAM})
- Agent Type: ${AGENT_TYPE}
- Model: ${MODEL}
- Pane: ${PANE_ID}
```

윈도우 모드일 때 추가 정보:
```markdown
- Window: ${WINDOW_NAME}
```

## 스폰 완료 후 작업

스폰 완료 후 호출한 커맨드가 **SendMessage로 초기 작업을 지시**합니다:

```
SendMessage tool:
- type: "message"
- recipient: "${NAME}"
- content: |
    [역할 템플릿 기반 프롬프트]
- summary: "${NAME} 초기 작업 지시"
```

## 에러 핸들링 요약

### 공통 에러

| 에러 | 원인 | 해결 |
|------|------|------|
| tmux not found | tmux 미설치 | `sudo apt install tmux` 또는 `brew install tmux` |
| `$TMUX` 비어있음 | tmux 밖에서 실행 | tmux 세션 내에서 Claude Code 실행 |
| Pane 즉시 종료 | 인증/연결 실패 | 모드별 진단 가이드 참조 |
| 리더 pane 너무 작음 | 반복 분할로 공간 부족 | `tmux select-layout main-vertical`로 재배치 |

### GPT 모드 전용 에러

| 에러 | 원인 | 해결 |
|------|------|------|
| cli-proxy-api 미응답 | 서버 미실행 | cli-proxy-api 서버 시작 (localhost:8317) |
| gpt-claude-code 미발견 | 함수 미정의 | `~/.zshrc`에 함수 정의 |

### Claude 모드 전용 에러

| 에러 | 원인 | 해결 |
|------|------|------|
| claude CLI 미발견 | CLI 미설치 | `npm install -g @anthropic-ai/claude-code` |
| 에이전트 타입 미인식 | 잘못된 에이전트명 | 에이전트별 기본값 테이블 참조 |

## 트러블슈팅

트러블슈팅 유틸리티 스크립트로 일괄 처리합니다.

### Pane 즉시 종료

| 원인 | 진단 방법 | 해결 |
|------|----------|------|
| cli-proxy-api 미실행 (GPT) | `curl http://localhost:8317/` | 서버 시작 |
| 인증 토큰 만료 (GPT) | `gpt-claude-code --help` 수동 실행 | 토큰 갱신 |
| `gpt-claude-code` 함수 오류 (GPT) | `zsh -c 'source ~/.zshrc && type gpt-claude-code'` | 함수 재정의 |
| claude CLI 미설치 (Claude) | `which claude` | `npm i -g @anthropic-ai/claude-code` |
| ANTHROPIC_API_KEY 미설정 (Claude) | `echo $ANTHROPIC_API_KEY` | 환경변수 설정 |
| 에이전트 타입 오류 (Claude) | 에이전트 파일 존재 여부 확인 | `plugins/claude-team/agents/` 확인 |
| tmux 공간 부족 | `tmux list-panes` 확인 | 불필요한 pane 정리 또는 터미널 확대 |
| 환경변수 미로드 | `source ~/.zshrc` 후 재시도 | `.zshrc` 내 함수/변수 확인 |

### 윈도우 모드 빈 윈도우 정리

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/spawn-teammate/scripts/cleanup.sh" \
  --team "${TEAM}" --action windows
```

> **참고**: tmux는 마지막 pane이 종료되면 윈도우를 자동 삭제합니다. 이 정리는 레이스 컨디션으로 인해 기본 shell만 남은 윈도우를 처리하는 방어적 안전장치입니다.

### Config 죽은 멤버 수동 정리

config에 `isActive: true`이지만 pane이 없는 멤버가 남아있을 때:

```bash
# 죽은 멤버 확인
bash "${CLAUDE_PLUGIN_ROOT}/skills/spawn-teammate/scripts/cleanup.sh" \
  --team "${TEAM}" --action dead-members

# 특정 멤버 제거
bash "${CLAUDE_PLUGIN_ROOT}/skills/spawn-teammate/scripts/cleanup.sh" \
  --team "${TEAM}" --action dead-members --name "dead-member"
```

### 동시 스폰 시 멤버 누락 진단

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/spawn-teammate/scripts/cleanup.sh" \
  --team "${TEAM}" --action diagnose
```

### 보안 참고

**GPT 모드**: `gpt-claude-code` 함수는 cli-proxy-api를 통해 GPT 모델에 접근합니다:
- cli-proxy-api의 인증 토큰은 환경변수로 관리됩니다
- 팀메이트 pane에서 토큰이 노출되지 않도록 `~/.zshrc`에서 환경변수로 주입하세요

**Claude 모드**: Claude CLI는 ANTHROPIC_API_KEY를 사용합니다:
- API 키는 환경변수로 관리됩니다
- 프로덕션 환경에서는 credential을 별도 파일이나 시크릿 매니저로 분리하는 것을 권장합니다

## 호출 패턴 (커맨드에서 사용)

### GPT 모드 (`--gpt`)

```
Skill tool:
- skill: "claude-team:spawn-teammate"
- args: "{role-name} --team {team-name}"

→ 스폰 완료 후:
SendMessage tool:
- type: "message"
- recipient: "{role-name}"
- content: |
    [역할 템플릿 기반 프롬프트]
- summary: "{role-name} 초기 작업 지시"
```

### Claude 모드 (`--agent-type`)

```
Skill tool:
- skill: "claude-team:spawn-teammate"
- args: "{role-name} --team {team-name} --agent-type claude-team:{agent}"

→ 스폰 완료 후:
SendMessage tool:
- type: "message"
- recipient: "{role-name}"
- content: |
    [역할 템플릿 기반 프롬프트]
- summary: "{role-name} 초기 작업 지시"
```

### 윈도우 모드 (`--window`)

```
Skill tool:
- skill: "claude-team:spawn-teammate"
- args: "{role-name} --team {team-name} --agent-type claude-team:{agent} --window"

→ 별도 tmux 윈도우에 배치 (윈도우당 최대 2명, 수평 분할)
→ 리더 윈도우 포커스 유지
→ 5개 팀메이트 → 3개 윈도우 (name1, name2+name3, name4+name5)

→ 스폰 완료 후:
SendMessage tool:
- type: "message"
- recipient: "{role-name}"
- content: |
    [역할 템플릿 기반 프롬프트]
- summary: "{role-name} 초기 작업 지시"
```
