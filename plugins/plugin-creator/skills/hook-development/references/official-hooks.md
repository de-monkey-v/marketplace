# Claude Code Hooks 공식 문서

> 원본: https://code.claude.com/docs/ko/hooks
> 최종 업데이트: 2026-01-26

---

# Hooks 참조

> 이 페이지는 Claude Code에서 hooks를 구현하기 위한 참조 문서를 제공합니다.

## 구성

Claude Code hooks는 설정 파일에서 구성됩니다:

* `~/.claude/settings.json` - 사용자 설정
* `.claude/settings.json` - 프로젝트 설정
* `.claude/settings.local.json` - 로컬 프로젝트 설정 (커밋되지 않음)
* 관리형 정책 설정

### 구조

Hooks는 matchers로 구성되며, 각 matcher는 여러 hooks를 가질 수 있습니다:

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",
        "hooks": [
          {
            "type": "command",
            "command": "your-command-here"
          }
        ]
      }
    ]
  }
}
```

* **matcher**: 도구 이름을 일치시키는 패턴, 대소문자 구분
  * 단순 문자열은 정확히 일치합니다: `Write`는 Write 도구만 일치
  * 정규식을 지원합니다: `Edit|Write` 또는 `Notebook.*`
  * `*`를 사용하여 모든 도구를 일치
* **hooks**: 패턴이 일치할 때 실행할 hooks의 배열
  * `type`: Hook 실행 유형 - bash 명령의 경우 `"command"` 또는 LLM 기반 평가의 경우 `"prompt"`
  * `command`: 실행할 bash 명령
  * `prompt`: LLM 평가를 위해 보낼 프롬프트
  * `timeout`: hook이 실행되어야 하는 시간(초)

### 프로젝트별 Hook 스크립트

환경 변수 `CLAUDE_PROJECT_DIR`을 사용하여 프로젝트에 저장된 스크립트를 참조:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/check-style.sh"
          }
        ]
      }
    ]
  }
}
```

### 플러그인 hooks

플러그인은 플러그인의 `hooks/hooks.json` 파일에서 hooks를 정의할 수 있습니다:

```json
{
  "description": "Automatic code formatting",
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/format.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

**플러그인용 환경 변수**:
* `${CLAUDE_PLUGIN_ROOT}`: 플러그인 디렉토리의 절대 경로
* `${CLAUDE_PROJECT_DIR}`: 프로젝트 루트 디렉토리

## Hook 이벤트

### PreToolUse

Claude가 도구 매개변수를 생성한 후 도구 호출을 처리하기 전에 실행됩니다.

**일반적인 matchers:**
* `Task` - Subagent 작업
* `Bash` - 셸 명령
* `Glob` - 파일 패턴 일치
* `Grep` - 콘텐츠 검색
* `Read` - 파일 읽기
* `Edit` - 파일 편집
* `Write` - 파일 쓰기
* `WebFetch`, `WebSearch` - 웹 작업

### PermissionRequest

사용자에게 권한 대화가 표시될 때 실행됩니다.

### PostToolUse

도구가 성공적으로 완료된 직후에 실행됩니다.

### Notification

Claude Code가 알림을 보낼 때 실행됩니다.

**일반적인 matchers:**
* `permission_prompt` - Claude Code의 권한 요청
* `idle_prompt` - Claude가 사용자 입력을 기다리는 경우
* `auth_success` - 인증 성공 알림

### UserPromptSubmit

사용자가 프롬프트를 제출할 때, Claude가 처리하기 전에 실행됩니다.

### Stop

주 Claude Code agent가 응답을 완료했을 때 실행됩니다.

### SubagentStop

Claude Code subagent가 응답을 완료했을 때 실행됩니다.

### PreCompact

Claude Code가 compact 작업을 실행하려고 할 때 실행됩니다.

**Matchers:**
* `manual` - `/compact`에서 호출됨
* `auto` - auto-compact에서 호출됨

### SessionStart

Claude Code가 새 세션을 시작하거나 기존 세션을 재개할 때 실행됩니다.

**Matchers:**
* `startup` - 시작에서 호출됨
* `resume` - `--resume`, `--continue` 또는 `/resume`에서 호출됨
* `clear` - `/clear`에서 호출됨
* `compact` - auto 또는 manual compact에서 호출됨

#### 환경 변수 유지

SessionStart hooks는 `CLAUDE_ENV_FILE` 환경 변수에 액세스할 수 있습니다:

```bash
#!/bin/bash

if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=production' >> "$CLAUDE_ENV_FILE"
  echo 'export API_KEY=your-api-key' >> "$CLAUDE_ENV_FILE"
fi

exit 0
```

### SessionEnd

Claude Code 세션이 종료될 때 실행됩니다.

## 프롬프트 기반 Hooks

bash 명령 hooks 외에도, LLM을 사용하여 작업을 허용할지 차단할지 평가하는 프롬프트 기반 hooks를 지원합니다:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Evaluate if Claude should stop: $ARGUMENTS. Check if all tasks are complete."
          }
        ]
      }
    ]
  }
}
```

### 응답 스키마

```json
{
  "ok": true | false,
  "reason": "Explanation for the decision"
}
```

## Hook 입력

Hooks는 stdin을 통해 JSON 데이터를 수신합니다:

```typescript
{
  session_id: string
  transcript_path: string
  cwd: string
  permission_mode: string
  hook_event_name: string
  ...
}
```

### PreToolUse 입력

```json
{
  "session_id": "abc123",
  "hook_event_name": "PreToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "content": "file content"
  },
  "tool_use_id": "toolu_01ABC123..."
}
```

### PostToolUse 입력

```json
{
  "hook_event_name": "PostToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "content": "file content"
  },
  "tool_response": {
    "filePath": "/path/to/file.txt",
    "success": true
  }
}
```

### Notification 입력

```json
{
  "hook_event_name": "Notification",
  "message": "Claude needs your permission to use Bash",
  "notification_type": "permission_prompt"
}
```

### UserPromptSubmit 입력

```json
{
  "hook_event_name": "UserPromptSubmit",
  "prompt": "Write a function to calculate the factorial of a number"
}
```

### Stop/SubagentStop 입력

```json
{
  "hook_event_name": "Stop",
  "stop_hook_active": true
}
```

## Hook 출력

### 단순: 종료 코드

* **종료 코드 0**: 성공
* **종료 코드 2**: 차단 오류 - `stderr`가 오류 메시지로 사용됨
* **기타 종료 코드**: 차단되지 않는 오류

#### 종료 코드 2 동작

| Hook 이벤트            | 동작                                |
| ------------------- | --------------------------------- |
| `PreToolUse`        | 도구 호출을 차단하고 stderr를 Claude에 표시   |
| `PermissionRequest` | 권한을 거부하고 stderr를 Claude에 표시      |
| `PostToolUse`       | stderr를 Claude에 표시 (도구가 이미 실행됨)  |
| `UserPromptSubmit`  | 프롬프트 처리를 차단하고 stderr를 사용자에게 표시   |
| `Stop`              | 중지를 차단하고 stderr를 Claude에 표시      |
| `SubagentStop`      | 중지를 차단하고 stderr를 Claude subagent에 표시 |

### 고급: JSON 출력

더 정교한 제어를 위해 `stdout`에서 구조화된 JSON을 반환할 수 있습니다.

#### 공통 JSON 필드

```json
{
  "continue": true,
  "stopReason": "string",
  "suppressOutput": true,
  "systemMessage": "string"
}
```

#### `PreToolUse` 결정 제어

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "My reason here",
    "updatedInput": {
      "field_to_modify": "new value"
    }
  }
}
```

* `"allow"`: 권한 시스템을 우회
* `"deny"`: 도구 호출 실행을 방지
* `"ask"`: 사용자에게 확인 요청

#### `PermissionRequest` 결정 제어

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow",
      "updatedInput": {
        "command": "npm run lint"
      }
    }
  }
}
```

#### `PostToolUse` 결정 제어

```json
{
  "decision": "block",
  "reason": "Explanation for decision",
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "Additional information for Claude"
  }
}
```

#### `UserPromptSubmit` 결정 제어

```json
{
  "decision": "block",
  "reason": "Explanation for decision",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "My additional context here"
  }
}
```

#### `Stop`/`SubagentStop` 결정 제어

```json
{
  "decision": "block",
  "reason": "Must be provided when Claude is blocked from stopping"
}
```

## MCP 도구 작업

MCP 도구는 `mcp__<server>__<tool>` 패턴을 따릅니다:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__memory__.*",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Memory operation initiated' >> ~/mcp-operations.log"
          }
        ]
      }
    ]
  }
}
```

## 보안 고려 사항

### 보안 모범 사례

1. **입력 검증 및 살균** - 입력 데이터를 맹목적으로 신뢰하지 마세요
2. **항상 셸 변수를 인용** - `$VAR`이 아닌 `"$VAR"`을 사용
3. **경로 순회 차단** - 파일 경로에서 `..`을 확인
4. **절대 경로 사용** - 스크립트의 전체 경로를 지정
5. **민감한 파일 건너뛰기** - `.env`, `.git/`, 키 등을 피함

### 구성 안전성

설정 파일의 hooks에 대한 직접 편집은 즉시 적용되지 않습니다:

1. 시작 시 hooks의 스냅샷을 캡처
2. 세션 전체에서 이 스냅샷을 사용
3. hooks가 외부에서 수정되면 경고
4. `/hooks` 메뉴에서 검토가 필요

## Hook 실행 세부 사항

* **시간 초과**: 기본적으로 60초 실행 제한
* **병렬화**: 일치하는 모든 hooks가 병렬로 실행
* **중복 제거**: 동일한 hook 명령이 자동으로 중복 제거
* **환경**: 현재 디렉토리에서 Claude Code의 환경으로 실행
  * `CLAUDE_PROJECT_DIR`: 프로젝트 루트 디렉토리
  * `CLAUDE_CODE_REMOTE`: 원격 환경에서 실행 중인지 여부

## 디버깅

### 기본 문제 해결

1. **구성 확인** - `/hooks`를 실행하여 hook이 등록되었는지 확인
2. **구문 확인** - JSON 설정이 유효한지 확인
3. **명령 테스트** - hook 명령을 먼저 수동으로 실행
4. **권한 확인** - 스크립트가 실행 가능한지 확인
5. **로그 검토** - `claude --debug`를 사용하여 hook 실행 세부 사항 확인

### 일반적인 문제

* **인용되지 않은 따옴표** - JSON 문자열 내에서 `\"`를 사용
* **잘못된 matcher** - 도구 이름이 정확히 일치하는지 확인 (대소문자 구분)
* **명령을 찾을 수 없음** - 스크립트에 전체 경로를 사용
