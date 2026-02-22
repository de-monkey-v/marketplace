#!/bin/bash
# cleanup.sh - Team troubleshooting utility
# Part of claude-team plugin's spawn-teammate skill
#
# Actions: windows (clean empty windows), dead-members (find/remove dead), diagnose (spawn check)

set -euo pipefail

##############################################################################
# Usage
##############################################################################

usage() {
    cat << 'EOF'
Usage: cleanup.sh --team TEAM --action ACTION [OPTIONS]

Actions:
    windows         빈 윈도우 정리 (--window 모드)
    dead-members    죽은 멤버 확인 및 제거
    diagnose        동시 스폰 진단

Options:
    --team TEAM     팀 이름 (필수)
    --action ACT    수행할 작업 (필수)
    --name NAME     특정 멤버 제거 (dead-members에서 사용)
    -h, --help      도움말 표시

Examples:
    cleanup.sh --team impl-003 --action windows
    cleanup.sh --team impl-003 --action dead-members
    cleanup.sh --team impl-003 --action dead-members --name dead-member
    cleanup.sh --team impl-003 --action diagnose
EOF
}

##############################################################################
# Argument Parsing
##############################################################################

TEAM=""
ACTION=""
MEMBER_NAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --team)   TEAM="$2"; shift 2 ;;
        --action) ACTION="$2"; shift 2 ;;
        --name)   MEMBER_NAME="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "ERROR: 알 수 없는 옵션: $1" >&2; usage >&2; exit 1 ;;
    esac
done

if [[ -z "$TEAM" ]]; then echo "ERROR: --team 필수" >&2; exit 1; fi
if [[ -z "$ACTION" ]]; then echo "ERROR: --action 필수" >&2; exit 1; fi

CONFIG="$HOME/.claude/teams/${TEAM}/config.json"

##############################################################################
# Actions
##############################################################################

action_windows() {
    local TMUX_SESSION
    TMUX_SESSION=$(tmux display-message -p '#S' 2>/dev/null || true)
    if [[ -z "$TMUX_SESSION" ]]; then
        echo "ERROR: tmux 세션 내에서 실행하세요." >&2
        exit 1
    fi

    echo "팀 ${TEAM}의 윈도우 상태:"
    tmux list-windows -t "${TMUX_SESSION}" \
        -F '#{window_index}|#{window_name}|#{window_panes}|#{@team_name}' \
        | awk -F'|' -v team="${TEAM}" '$4 == team'

    echo ""
    echo "빈 윈도우 정리 중..."
    tmux list-windows -t "${TMUX_SESSION}" \
        -F '#{window_index}|#{window_name}|#{window_panes}|#{@team_name}' \
        | while IFS='|' read -r idx name panes team_tag; do
        if [[ "$team_tag" == "${TEAM}" ]] && [[ "$panes" -le 1 ]]; then
            PANE_CMD=$(tmux list-panes -t "${TMUX_SESSION}:${idx}" \
                -F '#{pane_current_command}' 2>/dev/null | head -1)
            if [[ -z "$PANE_CMD" ]] || echo "$PANE_CMD" | grep -qE '^(zsh|bash)$'; then
                tmux kill-window -t "${TMUX_SESSION}:${idx}" 2>/dev/null
                echo "Cleaned: ${name}"
            fi
        fi
    done
    echo "완료"
}

action_dead_members() {
    if [[ ! -f "$CONFIG" ]]; then
        echo "ERROR: Config 파일을 찾을 수 없습니다: ${CONFIG}" >&2
        exit 1
    fi

    echo "죽은 멤버 확인 중..."
    jq -r '.members[] | select(.isActive == true) | "\(.name)\t\(.tmuxPaneId)"' "$CONFIG" \
        | while IFS=$'\t' read -r name pane; do
        if ! tmux list-panes -a -F '#{pane_id}' 2>/dev/null | grep -q "$pane"; then
            echo "Dead member: ${name} (pane: ${pane})"
        else
            echo "OK: ${name} (pane: ${pane})"
        fi
    done

    if [[ -n "$MEMBER_NAME" ]]; then
        echo ""
        echo "멤버 ${MEMBER_NAME} 제거 중..."
        jq --arg name "$MEMBER_NAME" '.members = [.members[] | select(.name != $name)]' \
            "$CONFIG" > "${CONFIG}.tmp" && mv "${CONFIG}.tmp" "$CONFIG"
        echo "완료: ${MEMBER_NAME} 제거됨"
    fi
}

action_diagnose() {
    if [[ ! -f "$CONFIG" ]]; then
        echo "ERROR: Config 파일을 찾을 수 없습니다: ${CONFIG}" >&2
        exit 1
    fi

    echo "동시 스폰 진단:"
    echo ""
    echo "Config 등록 멤버 수: $(jq '.members | length' "$CONFIG")"
    echo ""
    echo "Pane 상태:"
    jq -r '.members[] | .tmuxPaneId' "$CONFIG" | while read -r pane; do
        if tmux list-panes -a -F '#{pane_id}' 2>/dev/null | grep -q "$pane"; then
            echo "  OK: $pane"
        else
            echo "  MISSING: $pane"
        fi
    done
}

##############################################################################
# Dispatch
##############################################################################

case "$ACTION" in
    windows)      action_windows ;;
    dead-members) action_dead_members ;;
    diagnose)     action_diagnose ;;
    *) echo "ERROR: 알 수 없는 action: $ACTION (windows|dead-members|diagnose)" >&2; exit 1 ;;
esac
