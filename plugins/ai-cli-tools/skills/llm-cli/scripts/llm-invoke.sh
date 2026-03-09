#!/usr/bin/env bash
# LLM CLI Invocation Wrapper
#
# Usage:
#   llm-invoke.sh gemini "prompt"
#   echo "code" | llm-invoke.sh gemini "prompt"
#   llm-invoke.sh codex exec "prompt"
#   echo "code" | llm-invoke.sh codex exec "prompt"
#   llm-invoke.sh codex review [--uncommitted|--base branch] "prompt"
#
# CLI 기본 모델(최신)을 사용합니다.
# 특정 모델을 강제하려면 아래 변수를 설정하세요 (빈 값 = CLI 기본값).
GEMINI_MODEL="gemini-3.1-pro-preview"
CODEX_MODEL="gpt-5.4"

set -euo pipefail

provider="${1:-}"
if [ -z "$provider" ]; then
  echo "Error: provider required (gemini or codex)" >&2
  echo "Usage: llm-invoke.sh <gemini|codex> [subcommand] \"prompt\"" >&2
  exit 1
fi
shift

case "$provider" in
  gemini)
    if ! command -v gemini &>/dev/null; then
      echo "Error: gemini CLI not installed. Run /ai-cli-tools:setup" >&2
      exit 1
    fi
    prompt="$*"
    if [ -z "$prompt" ]; then
      echo "Error: prompt required" >&2
      exit 1
    fi
    if [ -n "$GEMINI_MODEL" ]; then
      gemini -m "$GEMINI_MODEL" -p "$prompt"
    else
      gemini -p "$prompt"
    fi
    ;;

  codex)
    subcommand="${1:-}"
    if [ -z "$subcommand" ]; then
      echo "Error: codex subcommand required (exec or review)" >&2
      exit 1
    fi
    shift

    if ! command -v codex &>/dev/null; then
      echo "Error: codex CLI not installed. Run /ai-cli-tools:setup" >&2
      exit 1
    fi

    model_flag=()
    [ -n "$CODEX_MODEL" ] && model_flag=(-m "$CODEX_MODEL")

    case "$subcommand" in
      exec)
        prompt="$*"
        if [ -z "$prompt" ]; then
          echo "Error: prompt required" >&2
          exit 1
        fi
        if [ -t 0 ]; then
          codex exec "${model_flag[@]}" -s read-only "$prompt"
        else
          codex exec "${model_flag[@]}" -s read-only - "$prompt"
        fi
        ;;
      review)
        codex review "${model_flag[@]}" "$@"
        ;;
      *)
        echo "Error: unknown codex subcommand: $subcommand (use exec or review)" >&2
        exit 1
        ;;
    esac
    ;;

  *)
    echo "Error: unknown provider: $provider (use gemini or codex)" >&2
    exit 1
    ;;
esac
