# CLI 플래그 전체 레퍼런스

카테고리별 Claude Code CLI 플래그 문서입니다.

---

## 디버깅 & 테스트

| 플래그 | 설명 | 예시 |
|--------|------|------|
| `--debug <categories>` | 디버그 로그 출력 | `--debug "mcp,hooks"` |
| `--verbose` | 상세 실행 정보 | `--verbose` |
| `--plugin-dir <path>` | 로컬 플러그인 로드 | `--plugin-dir ./my-plugin` |

### 디버그 카테고리

```bash
# 사용 가능한 카테고리
api       # API 요청/응답
mcp       # MCP 서버 통신
hooks     # 훅 트리거/실행
file      # 파일 작업
tool      # 도구 호출
statsig   # 피처 플래그
cost      # 비용 계산
all       # 모든 카테고리

# 제외 패턴 (! 접두사)
--debug "all,!statsig"    # statsig 제외
--debug "all,!file,!api"  # 여러 카테고리 제외
```

---

## 권한 제어

| 플래그 | 설명 | 예시 |
|--------|------|------|
| `--allowedTools <tools>` | 허용할 도구 목록 | `--allowedTools "Read,Grep"` |
| `--disallowedTools <tools>` | 차단할 도구 목록 | `--disallowedTools "Bash"` |
| `--tools <tools>` | SDK 모드 도구 제어 | `-p --tools "Read"` |
| `--permission-mode <mode>` | 권한 프리셋 | `--permission-mode auto` |

### permission-mode 값

| 값 | 설명 |
|----|------|
| `default` | 기본 - 위험한 작업 시 프롬프트 |
| `auto` | 자동 허용 (CI/자동화용) |
| `plan` | 계획 모드만 허용 |
| `bypassPermissions` | 모든 권한 무시 (주의) |

---

## 모델 & 에이전트

| 플래그 | 설명 | 예시 |
|--------|------|------|
| `--model <id>` | 사용할 모델 | `--model sonnet` |
| `--agent <name>` | 특정 에이전트로 시작 | `--agent "code-reviewer"` |
| `--agents <json>` | 동적 에이전트 정의 | `--agents '[{...}]'` |

### 모델 별칭

```bash
--model sonnet    # claude-sonnet-4-*
--model opus      # claude-opus-4-*
--model haiku     # claude-haiku-*
```

---

## 시스템 프롬프트

| 플래그 | 설명 |
|--------|------|
| `--system-prompt <text>` | 시스템 프롬프트 교체 |
| `--append-system-prompt <text>` | 시스템 프롬프트에 추가 |
| `--system-prompt-file <path>` | 파일에서 시스템 프롬프트 교체 |
| `--append-system-prompt-file <path>` | 파일에서 시스템 프롬프트에 추가 |

> 상세: `system-prompt-flags.md`

---

## MCP 설정

| 플래그 | 설명 | 예시 |
|--------|------|------|
| `--mcp-config <path>` | MCP 설정 파일 | `--mcp-config ./mcp.json` |
| `--strict-mcp-config` | MCP 에러 시 실패 | `--strict-mcp-config` |

### MCP 설정 파일 형식

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["server.js"],
      "env": {}
    }
  }
}
```

---

## 출력 형식 (SDK 모드)

| 플래그 | 설명 | 예시 |
|--------|------|------|
| `--output-format <format>` | 출력 형식 | `--output-format json` |
| `--input-format <format>` | 입력 형식 | `--input-format stream-json` |
| `--json-schema <schema>` | 출력 스키마 강제 | `--json-schema '{...}'` |
| `--include-partial-messages` | 스트리밍 중간 메시지 | `--include-partial-messages` |

### output-format 값

| 값 | 설명 |
|----|------|
| `text` | 일반 텍스트 (기본) |
| `json` | JSON 객체 |
| `stream-json` | 줄별 JSON 스트림 |

> 상세: `output-formats.md`

---

## 세션 관리

| 플래그 | 설명 | 예시 |
|--------|------|------|
| `-c, --continue` | 마지막 세션 계속 | `claude -c` |
| `-r, --resume <id>` | 특정 세션 재개 | `claude -r abc123` |
| `--session-id <id>` | 세션 ID 지정 | `--session-id my-session` |
| `--fork-session <id>` | 세션 분기 | `--fork-session abc123` |

---

## 작업 디렉토리 & 경로

| 플래그 | 설명 | 예시 |
|--------|------|------|
| `--add-dir <path>` | 추가 디렉토리 포함 | `--add-dir ../shared` |
| `-d, --dir <path>` | 작업 디렉토리 변경 | `-d ./project` |

---

## 비용 & 제한

| 플래그 | 설명 | 예시 |
|--------|------|------|
| `--max-turns <n>` | 최대 turn 수 | `--max-turns 10` |
| `--max-budget-usd <amount>` | 최대 비용 (USD) | `--max-budget-usd 5.00` |

---

## 기타

| 플래그 | 설명 |
|--------|------|
| `--chrome` | Chrome 브라우저 연결 |
| `--no-telemetry` | 텔레메트리 비활성화 |
| `--version` | 버전 출력 |
| `--help` | 도움말 출력 |
