---
name: spawn-teammate
description: "GPT-5.3 Codex 네이티브 팀메이트 스폰. cli-proxy-api를 통해 GPT 모델로 직접 실행되는 팀메이트를 생성합니다."
version: 1.0.0
---

# GPT Native Teammate Spawn Skill

GPT-5.3 Codex 네이티브 팀메이트를 tmux pane으로 스폰하는 절차를 제공합니다.
이 스킬을 로드한 커맨드(specify, implement, verify 등)가 절차에 따라 GPT 팀메이트를 스폰합니다.

## 인자 형식

```
{member-name} --team {team-name}
```

- `member-name`: 팀메이트 이름 (예: `pm`, `developer`, `qa`)
- `--team`: 팀 이름 (필수)

파싱 예시:
```
"pm --team specify-001"
→ NAME: "pm", TEAM: "specify-001"

"developer --team implement-003"
→ NAME: "developer", TEAM: "implement-003"
```

## 스폰 절차

### Step 1: Prerequisite Check

모든 전제조건을 확인합니다. **하나라도 실패하면 즉시 중단하고 에러를 표시합니다.**

**1-1. tmux 확인:**
```bash
which tmux
```
실패 시: "tmux가 설치되어 있지 않습니다. `sudo apt install tmux` 또는 `brew install tmux`로 설치하세요."

**1-2. CLAUDE_CODE_TMUX_SESSION 확인:**
```bash
echo "$CLAUDE_CODE_TMUX_SESSION"
```
비어 있으면: "CLAUDE_CODE_TMUX_SESSION 환경변수가 설정되지 않았습니다. tmux 세션 내에서 Claude Code를 실행하세요."

**1-3. cli-proxy-api 확인:**
```bash
curl -s --connect-timeout 3 http://localhost:8317/ > /dev/null 2>&1
echo $?
```
exit code가 0이 아니면:
```
cli-proxy-api가 실행 중이지 않습니다.

시작 방법:
1. cli-proxy-api 서버를 시작하세요 (localhost:8317)
2. 인증 토큰이 설정되어 있는지 확인하세요
```

**1-4. gpt-claude-code 함수 확인:**
```bash
zsh -c 'source ~/.zshrc && type gpt-claude-code' 2>&1
```
함수를 찾을 수 없으면:
```
gpt-claude-code 함수를 찾을 수 없습니다.

~/.zshrc에 gpt-claude-code 함수가 정의되어 있는지 확인하세요.
이 함수는 cli-proxy-api 환경변수를 설정하여 claude CLI를 GPT 모델로 실행합니다.
```

### Step 2: Inbox 생성

```bash
mkdir -p ~/.claude/teams/${TEAM}/inboxes && echo '[]' > ~/.claude/teams/${TEAM}/inboxes/${NAME}.json
```

### Step 3: Leader Session ID 추출

```bash
CONFIG="$HOME/.claude/teams/${TEAM}/config.json"
LEAD_SESSION_ID=$(jq -r '.leadSessionId' "$CONFIG")
```

### Step 4: tmux Pane 스폰

```bash
PANE_ID=$(tmux split-window -t "$CLAUDE_CODE_TMUX_SESSION" -c "$PWD" -dP -F '#{pane_id}' \
  "zsh -c 'source ~/.zshrc && gpt-claude-code \
    --agent-id ${NAME}@${TEAM} \
    --agent-name ${NAME} \
    --team-name ${TEAM} \
    --agent-color \"#10A37F\" \
    --parent-session-id ${LEAD_SESSION_ID} \
    --agent-type claude-team:gpt \
    --model opus \
    --dangerously-skip-permissions'")
echo "$PANE_ID"
```

핵심 플래그 설명:
- `source ~/.zshrc`: `gpt-claude-code` 함수 및 환경변수 로드
- `--model opus`: cli-proxy-api의 환경변수에 의해 `gpt-5.3-codex(high)`로 매핑됨
- `--agent-type claude-team:gpt`: `agents/gpt.md` 에이전트 설정 로드
- `--parent-session-id`: 리더와의 메시지 라우팅 연결
- `--dangerously-skip-permissions`: 자율적 실행 허용

### Step 5: Config 등록

```bash
CONFIG="$HOME/.claude/teams/${TEAM}/config.json"
jq --arg name "$NAME" --arg agentId "${NAME}@${TEAM}" --arg paneId "$PANE_ID" \
  '.members += [{
    "agentId": $agentId, "name": $name,
    "agentType": "claude-team:gpt", "model": "gpt-5.3-codex(high)",
    "color": "#10A37F", "tmuxPaneId": $paneId,
    "backendType": "tmux", "isActive": true,
    "joinedAt": (now * 1000 | floor), "cwd": env.PWD, "subscriptions": []
  }]' "$CONFIG" > /tmp/config-tmp-${NAME}.json && mv /tmp/config-tmp-${NAME}.json "$CONFIG"
```

### Step 6: 스폰 확인

**6-1. Pane 생존 확인:**
```bash
tmux list-panes -t "$CLAUDE_CODE_TMUX_SESSION" -F '#{pane_id} #{pane_alive}' | grep "$PANE_ID"
```
pane이 없거나 dead이면:
```
GPT 팀메이트 pane이 즉시 종료되었습니다.

확인 사항:
1. cli-proxy-api가 정상 동작하는지: curl http://localhost:8317/
2. gpt-claude-code 함수의 인증 토큰이 유효한지
3. tmux 세션에 여유 공간이 있는지
```

**6-2. 잠시 대기:**
```bash
sleep 2
```

**6-3. 스폰 완료 메시지 표시:**
```markdown
GPT 팀메이트 스폰 완료: ${NAME} (Team: ${TEAM})
- Model: GPT-5.3 Codex (high) via cli-proxy-api
- Pane: ${PANE_ID}
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

| 에러 | 원인 | 해결 |
|------|------|------|
| tmux not found | tmux 미설치 | `sudo apt install tmux` 또는 `brew install tmux` |
| CLAUDE_CODE_TMUX_SESSION 미설정 | tmux 밖에서 실행 | tmux 세션 내에서 Claude Code 실행 |
| cli-proxy-api 미응답 | 서버 미실행 | cli-proxy-api 서버 시작 (localhost:8317) |
| gpt-claude-code 미발견 | 함수 미정의 | `~/.zshrc`에 함수 정의 |
| Pane 즉시 종료 | 인증/연결 실패 | 토큰, 서버 상태, 함수 수동 테스트 |

## 호출 패턴 (커맨드에서 사용)

커맨드의 GPT 모드 (`--gpt`) 섹션에서:

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
