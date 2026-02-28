#!/usr/bin/env bash
# validate-model.sh
# PreToolUse hook: gemini/codex CLI 직접 호출을 전면 차단한다.
# 반드시 llm-invoke.sh 스크립트를 통해서만 호출해야 한다.
# 스크립트 내부의 서브프로세스 호출은 훅이 감지하지 않으므로 안전하다.
#
# "command -v gemini", "which gemini" 등 CLI를 직접 실행하지 않는
# 명령어는 차단하지 않는다.

set -euo pipefail

INPUT=$(cat)

# jq가 있으면 jq, 없으면 python3으로 command 추출
if command -v jq &>/dev/null; then
  COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
else
  COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null || true)
fi

# command가 비어있으면 통과
[[ -z "$COMMAND" ]] && exit 0

# is_cli_invocation: 주어진 도구명이 실제 CLI 인보케이션인지 확인
# 1) 따옴표 내부 제거 → grep/find 인자 등 문자열로 전달된 경우 무시
# 2) 비-인보케이션 패턴 제거 (command -v, which, type)
# 3) 정리된 명령어에서 tool이 독립 단어로 남아있으면 인보케이션
is_cli_invocation() {
  local tool="$1"

  # Step 1: 따옴표 내부 제거 (grep/find 인자 등 무시)
  local stripped
  stripped=$(echo "$COMMAND" | sed "s/'[^']*'//g; s/\"[^\"]*\"//g")

  # Step 2: 비-인보케이션 패턴 제거 (command -v, which, type)
  stripped=$(echo "$stripped" | sed -E "s/(command\s+-v|which|type(\s+-p)?)\s+${tool}//g")

  # Step 3: 커맨드 위치에서 tool이 존재하는지 확인
  # 커맨드 위치 = 줄 시작 또는 셸 구분자(|, ;, &&, ||) 뒤
  echo "$stripped" | grep -qE "(^\s*|[|;&]+\s+)(sudo\s+|timeout\s+\S+\s+)*${tool}(\s|$)"
}

# gemini CLI 직접 호출 차단
if is_cli_invocation "gemini"; then
  cat >&2 <<'MSG'
BLOCKED: gemini CLI를 직접 호출할 수 없습니다. llm-invoke.sh 스크립트를 사용하세요.
사용법: $INVOKE gemini "prompt"
사용법: cat file | $INVOKE gemini "prompt"
MSG
  exit 2
fi

# codex CLI 직접 호출 차단
if is_cli_invocation "codex"; then
  cat >&2 <<'MSG'
BLOCKED: codex CLI를 직접 호출할 수 없습니다. llm-invoke.sh 스크립트를 사용하세요.
사용법: $INVOKE codex exec "prompt"
사용법: $INVOKE codex review --uncommitted "prompt"
MSG
  exit 2
fi

exit 0
