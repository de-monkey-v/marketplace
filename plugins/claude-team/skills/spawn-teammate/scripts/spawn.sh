#!/bin/bash
# spawn.sh - Teammate spawn orchestration script
# Part of claude-team plugin's spawn-teammate skill
#
# Handles: prerequisite checks, pane creation, config registration, health check
# Outputs: key=value pairs on stdout for caller to parse
# Errors: human-readable Korean messages on stderr + exit 1

set -euo pipefail

##############################################################################
# Section 1: Usage
##############################################################################

usage() {
    cat << 'EOF'
Usage: spawn.sh --name NAME --team TEAM [OPTIONS]

Options:
    --name NAME           팀메이트 이름 (필수)
    --team TEAM           팀 이름 (필수)
    --agent-type TYPE     에이전트 타입 (예: claude-team:implementer). 지정 시 Claude 모드
    --model MODEL         모델 오버라이드
    --color COLOR         색상 오버라이드
    --window              별도 윈도우 모드
    -h, --help            도움말 표시

Examples:
    spawn.sh --name pm --team specify-001
    spawn.sh --name developer --team impl-003 --agent-type claude-team:implementer
    spawn.sh --name developer --team impl-003 --agent-type claude-team:implementer --window
EOF
}

##############################################################################
# Section 2: Argument Parsing
##############################################################################

NAME=""
TEAM=""
AGENT_TYPE=""
MODEL=""
COLOR=""
WINDOW_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --name)       NAME="$2"; shift 2 ;;
        --team)       TEAM="$2"; shift 2 ;;
        --agent-type) AGENT_TYPE="$2"; shift 2 ;;
        --model)      MODEL="$2"; shift 2 ;;
        --color)      COLOR="$2"; shift 2 ;;
        --window)     WINDOW_MODE=true; shift ;;
        -h|--help)    usage; exit 0 ;;
        *)            echo "ERROR: 알 수 없는 옵션: $1" >&2; usage >&2; exit 1 ;;
    esac
done

if [[ -z "$NAME" ]]; then echo "ERROR: --name 필수" >&2; exit 1; fi
if [[ -z "$TEAM" ]]; then echo "ERROR: --team 필수" >&2; exit 1; fi

# Mode detection
if [[ -n "$AGENT_TYPE" ]]; then
    MODE="claude"
else
    MODE="gpt"
fi

##############################################################################
# Section 3: Helper Functions
##############################################################################

_resolve_color() {
    # User-specified --color takes precedence
    if [[ -n "$COLOR" ]]; then return; fi

    if [[ "$MODE" == "gpt" ]]; then
        COLOR="#10A37F"
        return
    fi

    case "$AGENT_TYPE" in
        # 읽기 전용 -- 분석/설계
        *:architect)            COLOR="#CC6600" ;;
        *:reviewer)             COLOR="#8800CC" ;;
        *:a11y-auditor)         COLOR="#3498DB" ;;
        *:api-designer)         COLOR="#1E90FF" ;;
        *:db-architect)         COLOR="#2E8B57" ;;
        *:ddd-strategist)       COLOR="#8B0000" ;;
        *:fe-performance)       COLOR="#F39C12" ;;
        *:security-architect)   COLOR="#DC143C" ;;
        *:side-effect-analyzer) COLOR="#FF4500" ;;
        *:state-designer)       COLOR="#E67E22" ;;
        *:test-strategist)      COLOR="#32CD32" ;;
        *:ui-architect)         COLOR="#9B59B6" ;;
        # 읽기 전용 -- 웹 검색/태스크/특수
        *:planner)              COLOR="#FF6699" ;;
        *:researcher)           COLOR="#00AACC" ;;
        *:coordinator)          COLOR="#FFAA00" ;;
        *:team-architect)       COLOR="cyan" ;;
        # 읽기+쓰기 -- 구현
        *:implementer)          COLOR="#0066CC" ;;
        *:backend)              COLOR="#0066CC" ;;
        *:frontend)             COLOR="#FF6600" ;;
        *:tester)               COLOR="#00AA44" ;;
        *:css-architect)        COLOR="#A855F7" ;;
        *:domain-modeler)       COLOR="#B22222" ;;
        *:event-architect)      COLOR="#FF6347" ;;
        *:fastapi-expert)       COLOR="#009688" ;;
        *:fe-tester)            COLOR="#16A34A" ;;
        *:i18n-specialist)      COLOR="#0EA5E9" ;;
        *:integration-tester)   COLOR="#228B22" ;;
        *:migration-strategist) COLOR="#DAA520" ;;
        *:nestjs-expert)        COLOR="#E0234E" ;;
        *:nextjs-expert)        COLOR="#EDEDED" ;;
        *:nuxt-expert)          COLOR="#00DC82" ;;
        *:react-expert)         COLOR="#61DAFB" ;;
        *:spring-expert)        COLOR="#6DB33F" ;;
        *:vue-expert)           COLOR="#42B883" ;;
        # 특수 -- 외부 LLM 프록시
        *:codex)                COLOR="#10A37F" ;;
        *:gemini)               COLOR="#4285F4" ;;
        *)                      COLOR="#0066CC" ;;
    esac
}

_spawn_rollback() {
    local config="$1" name="$2" team="$3"
    local lockfile="$HOME/.claude/teams/${team}/.config.lock"
    (
        flock -w 5 200
        jq --arg name "$name" '.members = [.members[] | select(.name != $name)]' \
            "$config" > "${config}.tmp" && mv "${config}.tmp" "$config"
    ) 200>"$lockfile"
    rm -f "$HOME/.claude/teams/${team}/inboxes/${name}.json"
}

_discover_plugin_dir() {
    jq -r '."claude-team@marketplace"[0].installPath' \
        ~/.claude/plugins/installed_plugins.json 2>/dev/null || echo ""
}

##############################################################################
# Section 4: check_prerequisites()
##############################################################################

check_prerequisites() {
    # 1-1. tmux 확인
    if ! which tmux > /dev/null 2>&1; then
        echo "ERROR: tmux가 설치되어 있지 않습니다. \`sudo apt install tmux\` 또는 \`brew install tmux\`로 설치하세요." >&2
        exit 1
    fi

    # 1-2. tmux 세션 내 실행 확인
    if [[ -z "${TMUX:-}" ]]; then
        echo "ERROR: tmux 세션 내에서 Claude Code를 실행하세요." >&2
        exit 1
    fi

    if [[ "$MODE" == "gpt" ]]; then
        # 1-3g. cli-proxy-api 확인
        if ! curl -s --connect-timeout 3 http://localhost:8317/ > /dev/null 2>&1; then
            echo "ERROR: cli-proxy-api가 실행 중이지 않습니다." >&2
            echo "" >&2
            echo "시작 방법:" >&2
            echo "1. cli-proxy-api 서버를 시작하세요 (localhost:8317)" >&2
            echo "2. 인증 토큰이 설정되어 있는지 확인하세요" >&2
            exit 1
        fi

        # 1-4g. gpt-claude-code 함수 확인
        if ! zsh -c 'source ~/.zshrc && type gpt-claude-code' > /dev/null 2>&1; then
            echo "ERROR: gpt-claude-code 함수를 찾을 수 없습니다." >&2
            echo "" >&2
            echo "~/.zshrc에 gpt-claude-code 함수가 정의되어 있는지 확인하세요." >&2
            echo "이 함수는 cli-proxy-api 환경변수를 설정하여 claude CLI를 GPT 모델로 실행합니다." >&2
            exit 1
        fi
    else
        # 1-3c. claude CLI 확인
        if ! which claude > /dev/null 2>&1; then
            echo "ERROR: claude CLI가 설치되어 있지 않습니다. \`npm install -g @anthropic-ai/claude-code\`로 설치하세요." >&2
            exit 1
        fi
    fi
}

##############################################################################
# Section 4.5: check_duplicate_name()
##############################################################################

check_duplicate_name() {
    local config="$HOME/.claude/teams/${TEAM}/config.json"
    if [[ ! -f "$config" ]]; then return; fi

    local existing
    existing=$(jq -r --arg name "$NAME" \
        '.members[] | select(.name == $name and .isActive == true) | .name' \
        "$config" 2>/dev/null)

    if [[ -n "$existing" ]]; then
        echo "ERROR: 팀 '${TEAM}'에 이미 '${NAME}' 멤버가 존재합니다." >&2
        echo "번호를 붙여 스폰하세요 (예: ${NAME}-1, ${NAME}-2)" >&2
        exit 1
    fi
}

##############################################################################
# Section 5: setup()
##############################################################################

setup() {
    # Inbox 생성
    mkdir -p "$HOME/.claude/teams/${TEAM}/inboxes"
    echo '[]' > "$HOME/.claude/teams/${TEAM}/inboxes/${NAME}.json"

    # Leader Session ID 추출
    CONFIG="$HOME/.claude/teams/${TEAM}/config.json"
    LEAD_SESSION_ID=$(jq -r '.leadSessionId' "$CONFIG")

    # tmux 세션 감지
    TMUX_SESSION=$(tmux display-message -p '#S')
    LEADER_PANE_ID="$TMUX_PANE"
    LEADER_WINDOW=$(tmux display-message -t "$LEADER_PANE_ID" -p '#{window_index}')

    # TMUX_PANE 환경변수 확인
    if [[ -z "${TMUX_PANE:-}" ]]; then
        echo "ERROR: TMUX_PANE 환경변수가 설정되지 않았습니다. tmux 세션 내에서 실행하세요." >&2
        exit 1
    fi

    # 터미널 너비 체크 (리더 window 기준)
    TERM_WIDTH=$(tmux display-message -t "$LEADER_PANE_ID" -p '#{window_width}')
    if [[ "$TERM_WIDTH" -lt 120 ]]; then
        echo "WARN: 터미널 너비가 ${TERM_WIDTH}열입니다 (권장: 120열 이상). pane이 좁을 수 있습니다." >&2
    fi

    # Pane 높이 (환경변수로 오버라이드 가능)
    PANE_HEIGHT=${SPAWN_PANE_HEIGHT:-15}

    # Plugin dir 발견
    CLAUDE_TEAM_PLUGIN_DIR=$(_discover_plugin_dir)
}

##############################################################################
# Section 6: spawn_pane()
##############################################################################

_build_spawn_command() {
    if [[ "$MODE" == "gpt" ]]; then
        echo "env CLAUDE_TEAM_PLUGIN_DIR=\"${CLAUDE_TEAM_PLUGIN_DIR}\" \
zsh -c 'source ~/.zshrc && gpt-claude-code \
--agent-id ${NAME}@${TEAM} \
--agent-name ${NAME} \
--team-name ${TEAM} \
--agent-color \"#10A37F\" \
--parent-session-id ${LEAD_SESSION_ID} \
--model opus \
--dangerously-skip-permissions'"
    else
        echo "env CLAUDECODE=1 CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 \
CLAUDE_TEAM_PLUGIN_DIR=\"${CLAUDE_TEAM_PLUGIN_DIR}\" \
claude \
--agent-id ${NAME}@${TEAM} \
--agent-name ${NAME} \
--team-name ${TEAM} \
--agent-color '${COLOR}' \
--parent-session-id ${LEAD_SESSION_ID} \
--agent-type ${AGENT_TYPE} \
--model ${MODEL} \
--dangerously-skip-permissions"
    fi
}

spawn_pane() {
    local SPAWN_CMD
    SPAWN_CMD=$(_build_spawn_command)

    if [[ "$WINDOW_MODE" == true ]]; then
        _spawn_window_mode "$SPAWN_CMD"
    else
        _spawn_basic_mode "$SPAWN_CMD"
    fi

    tmux set-option -p -t "$PANE_ID" @agent_label "${NAME}"
    tmux set-option -p -t "$PANE_ID" @agent_color "${COLOR}"
    tmux set-option -p -t "$PANE_ID" @styled_label "#[fg=${COLOR},bold]${NAME}#[default]"
}

_spawn_basic_mode() {
    local cmd="$1"
    PANE_ID=$(tmux split-window -t "${TMUX_SESSION}:${LEADER_WINDOW}" \
        -l $PANE_HEIGHT -c "$PWD" -dP -F '#{pane_id}' "$cmd")
}

_spawn_window_mode() {
    local cmd="$1"
    local WINDOW_LOCKFILE="$HOME/.claude/teams/${TEAM}/.window.lock"

    SPAWN_RESULT=$(
    (
        flock -w 30 200 || { echo "LOCK_FAIL"; exit 1; }

        # @team_name 윈도우 옵션으로 팀 윈도우 조회
        LAST_LINE=$(tmux list-windows -t "${TMUX_SESSION}" \
            -F '#{window_index}|#{window_name}|#{window_panes}|#{@team_name}' 2>/dev/null \
            | awk -F'|' -v team="${TEAM}" '$4 == team {print $1, $2, $3}' \
            | sort -n | tail -1)

        if [ -z "$LAST_LINE" ]; then
            WIN_NAME="${NAME}"; POS=0
        else
            LAST_WIN_NAME=$(echo "$LAST_LINE" | awk '{print $2}')
            LAST_PANES=$(echo "$LAST_LINE" | awk '{print $3}')
            if [ "$LAST_PANES" -ge 2 ]; then
                WIN_NAME="${NAME}"; POS=0
            else
                WIN_NAME="$LAST_WIN_NAME"; POS=1
            fi
        fi

        if [ "$POS" -eq 0 ]; then
            PANE_ID=$(tmux new-window -t "${TMUX_SESSION}" -n "${WIN_NAME}" \
                -c "$PWD" -dP -F '#{pane_id}' "$cmd")
            tmux set-option -w -t "${TMUX_SESSION}:${WIN_NAME}" @team_name "${TEAM}"
        else
            TARGET=$(tmux list-panes -t "${TMUX_SESSION}:${WIN_NAME}" -F '#{pane_id}' | head -1)
            PANE_ID=$(tmux split-window -h -t "$TARGET" \
                -c "$PWD" -dP -F '#{pane_id}' "$cmd")
            NEW_WIN_NAME="${WIN_NAME}+${NAME}"
            tmux rename-window -t "${TMUX_SESSION}:${WIN_NAME}" "$NEW_WIN_NAME"
            WIN_NAME="$NEW_WIN_NAME"
        fi

        echo "${PANE_ID}|${WIN_NAME}"
    ) 200>"$WINDOW_LOCKFILE"
    )

    PANE_ID=$(echo "$SPAWN_RESULT" | head -1 | cut -d'|' -f1)
    WINDOW_NAME=$(echo "$SPAWN_RESULT" | head -1 | cut -d'|' -f2)
}

##############################################################################
# Section 7: setup_borders()
##############################################################################

setup_borders() {
    local MEMBER_COUNT
    MEMBER_COUNT=$(jq '.members | length' "$CONFIG" 2>/dev/null || echo 0)
    local LEADER_COLOR="#FFD700"
    local BORDER_FMT="#{?@agent_label, #{@styled_label} | #{pane_title}, #{pane_title}}"

    if [[ "$WINDOW_MODE" == true ]]; then
        # Window mode: border on team window
        tmux set-option -w -t "${TMUX_SESSION}:${WINDOW_NAME}" pane-border-status bottom
        tmux set-option -w -t "${TMUX_SESSION}:${WINDOW_NAME}" pane-border-format "$BORDER_FMT"
        tmux set-option -w -t "${TMUX_SESSION}:${WINDOW_NAME}" pane-border-style "fg=#585858"
        tmux set-option -w -t "${TMUX_SESSION}:${WINDOW_NAME}" pane-active-border-style "fg=#AAAAAA,bold"
    else
        # Basic mode: configure border (idempotent — safe to set every spawn)
        tmux set-option -w pane-border-status bottom
        tmux set-option -w pane-border-format "$BORDER_FMT"
        tmux set-option -w pane-border-style "fg=#585858"
        tmux set-option -w pane-active-border-style "fg=#AAAAAA,bold"
        tmux set-option -p -t "$LEADER_PANE_ID" @agent_label "LEADER"
        tmux set-option -p -t "$LEADER_PANE_ID" @agent_color "${LEADER_COLOR}"
        tmux set-option -p -t "$LEADER_PANE_ID" @styled_label "#[fg=${LEADER_COLOR},bold]LEADER#[default]"

        # 팀메이트 2개 이상일 때만 레이아웃 재배치 (flickering 방지)
        if [[ "$MEMBER_COUNT" -ge 2 ]]; then
            tmux select-layout -t "${TMUX_SESSION}:${LEADER_WINDOW}" main-vertical
        fi
    fi
}

##############################################################################
# Section 8: register_config()
##############################################################################

register_config() {
    local LOCKFILE="$HOME/.claude/teams/${TEAM}/.config.lock"

    if [[ "$MODE" == "gpt" ]]; then
        (
            flock -w 10 200 || { echo "ERROR: Config lock 획득 실패" >&2; exit 1; }
            jq --arg name "$NAME" --arg agentId "${NAME}@${TEAM}" --arg paneId "$PANE_ID" \
                '.members += [{
                    "agentId": $agentId, "name": $name,
                    "agentType": "claude-team:gpt", "model": "gpt-5.3-codex(xhigh)",
                    "color": "#10A37F", "tmuxPaneId": $paneId,
                    "backendType": "tmux", "isActive": true,
                    "joinedAt": (now * 1000 | floor), "cwd": env.PWD, "subscriptions": []
                }]' "$CONFIG" > "${CONFIG}.tmp" && mv "${CONFIG}.tmp" "$CONFIG"
        ) 200>"$LOCKFILE"
    else
        (
            flock -w 10 200 || { echo "ERROR: Config lock 획득 실패" >&2; exit 1; }
            jq --arg name "$NAME" --arg agentId "${NAME}@${TEAM}" --arg paneId "$PANE_ID" \
                --arg agentType "$AGENT_TYPE" --arg model "$MODEL" --arg color "$COLOR" \
                '.members += [{
                    "agentId": $agentId, "name": $name,
                    "agentType": $agentType, "model": $model,
                    "color": $color, "tmuxPaneId": $paneId,
                    "backendType": "tmux", "isActive": true,
                    "joinedAt": (now * 1000 | floor), "cwd": env.PWD, "subscriptions": []
                }]' "$CONFIG" > "${CONFIG}.tmp" && mv "${CONFIG}.tmp" "$CONFIG"
        ) 200>"$LOCKFILE"
    fi

    # Window mode: tmuxWindowName 필드 추가
    if [[ "$WINDOW_MODE" == true ]]; then
        (
            flock -w 10 200 || { echo "ERROR: Config lock 획득 실패" >&2; exit 1; }
            jq --arg name "$NAME" --arg windowName "$WINDOW_NAME" \
                '(.members[] | select(.name == $name)) += {"tmuxWindowName": $windowName}' \
                "$CONFIG" > "${CONFIG}.tmp" && mv "${CONFIG}.tmp" "$CONFIG"
        ) 200>"$LOCKFILE"
    fi

    # 쓰기 후 검증
    local REGISTERED
    REGISTERED=$(jq --arg name "$NAME" '.members[] | select(.name == $name) | .name' "$CONFIG")
    if [[ -z "$REGISTERED" ]]; then
        echo "ERROR: ${NAME} 등록 실패" >&2
        tmux kill-pane -t "$PANE_ID" 2>/dev/null
        exit 1
    fi
}

##############################################################################
# Section 9: health_check()
##############################################################################

health_check() {
    # Phase 1 (0.5s): Pane 즉시 사망 감지
    sleep 0.5
    if ! tmux list-panes -a -F '#{pane_id}' | grep -q "$PANE_ID"; then
        echo "ERROR: 팀메이트 pane이 즉시 종료되었습니다." >&2
        _spawn_rollback "$CONFIG" "$NAME" "$TEAM"
        echo "Rollback 완료: config에서 ${NAME} 제거됨" >&2
        echo "" >&2
        if [[ -n "$AGENT_TYPE" ]]; then
            echo "확인 사항 (Claude 모드):" >&2
            echo "1. claude CLI가 정상 동작하는지: claude --version" >&2
            echo "2. ANTHROPIC_API_KEY가 설정되어 있는지" >&2
            echo "3. 에이전트 타입이 유효한지: ${AGENT_TYPE}" >&2
            echo "4. tmux 세션에 여유 공간이 있는지" >&2
        else
            echo "확인 사항 (GPT 모드):" >&2
            echo "1. cli-proxy-api가 정상 동작하는지: curl http://localhost:8317/" >&2
            echo "2. gpt-claude-code 함수의 인증 토큰이 유효한지" >&2
            echo "3. tmux 세션에 여유 공간이 있는지" >&2
        fi
        exit 1
    fi

    # Phase 2 (최대 5s): Agent 프로세스 기동 확인
    local AGENT_READY=false
    local PANE_CMD=""
    for i in $(seq 1 10); do
        PANE_CMD=$(tmux list-panes -a -F '#{pane_id} #{pane_current_command}' \
            | grep "$PANE_ID" | awk '{print $2}')
        if [[ -z "$PANE_CMD" ]]; then
            echo "ERROR: Pane이 Phase 2에서 종료됨" >&2
            _spawn_rollback "$CONFIG" "$NAME" "$TEAM"
            exit 1
        fi
        if echo "$PANE_CMD" | grep -qE '^(claude|cc)$'; then
            AGENT_READY=true
            break
        fi
        sleep 0.5
    done

    if [[ "$AGENT_READY" != "true" ]]; then
        echo "WARN: Agent 프로세스(claude/cc)가 5초 내 감지되지 않음 (현재: ${PANE_CMD}). 계속 진행합니다." >&2
    fi
}

##############################################################################
# Section 10: Main
##############################################################################

# Resolve defaults
if [[ "$MODE" == "gpt" ]]; then
    MODEL="${MODEL:-opus}"
fi
if [[ "$MODE" == "claude" && -z "$MODEL" ]]; then
    MODEL="sonnet"
fi
_resolve_color

# Execute pipeline
check_prerequisites
setup
check_duplicate_name
spawn_pane
setup_borders
register_config
health_check

# Output key=value pairs on stdout
echo "MODE=${MODE}"
echo "PANE_ID=${PANE_ID}"
echo "NAME=${NAME}"
echo "TEAM=${TEAM}"
echo "MODEL=${MODEL}"
echo "COLOR=${COLOR}"
echo "STATUS=ok"
if [[ "$WINDOW_MODE" == true ]]; then
    echo "WINDOW_NAME=${WINDOW_NAME}"
fi
