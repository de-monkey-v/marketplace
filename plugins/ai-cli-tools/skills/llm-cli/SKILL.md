---
description: "LLM CLI (Gemini/Codex) 호출 래퍼. 직접 호출을 방지하고 스크립트를 통해 안전하게 CLI를 호출합니다."
---

# LLM CLI Invocation

외부 LLM CLI를 호출할 때 사용하는 스킬입니다.
`llm-invoke.sh` 스크립트를 통해 CLI를 호출합니다. CLI 기본 모델(최신)을 사용합니다.

> **직접 호출 금지**: `gemini` 또는 `codex` CLI를 직접 실행하면 훅에 의해 차단됩니다.
> 반드시 `$INVOKE`(llm-invoke.sh)를 통해서만 호출하세요.

## Setup

에이전트 시작 시 아래 명령으로 `$INVOKE` 변수를 설정하세요:

```bash
INVOKE="${AI_CLI_TOOLS_PLUGIN_DIR:-$(jq -r '."ai-cli-tools@marketplace"[0].installPath' ~/.claude/plugins/installed_plugins.json 2>/dev/null)}"/skills/llm-cli/scripts/llm-invoke.sh && [ -x "$INVOKE" ] && echo "OK: $INVOKE" || echo "FAIL: script not found"
```

특정 모델을 강제하려면 `scripts/llm-invoke.sh` 상단의 변수를 설정하세요.

## Usage Patterns

### Gemini

```bash
# 프롬프트만
$INVOKE gemini "What is the best practice for X"

# 파일 pipe + 프롬프트
cat src/auth.py | $INVOKE gemini "Review this code for security issues"

# Git diff pipe
git diff | $INVOKE gemini "Analyze these changes"
```

### Codex

```bash
# exec 모드 (코드 분석, stdin pipe)
cat src/auth.py | $INVOKE codex exec "Review this code"

# review 모드 (Git 변경사항)
$INVOKE codex review --uncommitted "Review these changes"
$INVOKE codex review --base main
```

## Error Handling

- CLI 미설치 시 `/ai-cli-tools:setup` 안내 메시지 출력
- provider/subcommand 오류 시 사용법 출력
- 모든 에러는 stderr로 출력, exit code 1 반환
