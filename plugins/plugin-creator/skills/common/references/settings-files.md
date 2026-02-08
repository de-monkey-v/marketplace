# Claude Code 설정 파일

> 원본: https://code.claude.com/docs/ko/settings#설정-파일

## 설정 파일 위치

### 사용자 설정
`~/.claude/settings.json` - 모든 프로젝트에 적용

### 프로젝트 설정
- `.claude/settings.json` - 소스 제어에 체크인, 팀과 공유
- `.claude/settings.local.json` - 체크인되지 않음, 개인 설정용

### Managed 설정 (시스템 수준)
조직 전체 정책을 위한 IT 관리자용:

| OS | 경로 |
|----|------|
| macOS | `/Library/Application Support/ClaudeCode/` |
| Linux/WSL | `/etc/claude-code/` |
| Windows | `C:\Program Files\ClaudeCode\` |

> **참고**: 시스템 전체 경로입니다 (`~/Library/...`가 아님). 관리자 권한 필요.

### 기타 구성
`~/.claude.json` - 사용자 설정 (테마, 알림), OAuth 세션, MCP 서버 구성, 프로젝트별 상태

## 설정 파일 예제

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test:*)",
      "Read(~/.zshrc)"
    ],
    "deny": [
      "Bash(curl:*)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  },
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp"
  },
  "companyAnnouncements": [
    "Welcome to Acme Corp! Review our code guidelines at docs.acme.com"
  ]
}
```

## 설정 우선순위

1. **Managed 설정** (`managed-settings.json`) - 최상위
2. **명령줄 인수** - 임시 재정의
3. **Local 프로젝트 설정** (`.claude/settings.local.json`)
4. **공유 프로젝트 설정** (`.claude/settings.json`)
5. **사용자 설정** (`~/.claude/settings.json`) - 최하위
