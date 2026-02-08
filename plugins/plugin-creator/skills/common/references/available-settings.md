# Claude Code 사용 가능한 설정

> 원본: https://code.claude.com/docs/ko/settings#사용-가능한-설정

## 설정 키 목록

| 키 | 설명 | 예제 |
|----|------|------|
| `apiKeyHelper` | 인증 값 생성 스크립트 | `/bin/generate_temp_api_key.sh` |
| `cleanupPeriodDays` | 비활성 세션 삭제 기간 (기본: 30일) | `20` |
| `companyAnnouncements` | 시작 시 표시할 공지사항 | `["Welcome message"]` |
| `env` | 모든 세션에 적용될 환경 변수 | `{"FOO": "bar"}` |
| `attribution` | git 커밋/PR 속성 커스터마이징 | `{"commit": "...", "pr": ""}` |
| `permissions` | 권한 구조 (allow/ask/deny) | 별도 문서 참조 |
| `hooks` | 도구 실행 전후 사용자 정의 명령 | `{"PreToolUse": {...}}` |
| `disableAllHooks` | 모든 hooks 비활성화 | `true` |
| `allowManagedHooksOnly` | Managed/SDK hooks만 허용 | `true` |
| `model` | 기본 모델 재정의 | `"claude-sonnet-4-5-20250929"` |
| `otelHeadersHelper` | OpenTelemetry 헤더 생성 스크립트 | `/bin/generate_otel_headers.sh` |
| `statusLine` | 사용자 정의 상태 라인 구성 | `{"type": "command", ...}` |
| `fileSuggestion` | `@` 파일 자동완성 스크립트 | `{"type": "command", ...}` |
| `respectGitignore` | `.gitignore` 패턴 준수 (기본: true) | `false` |
| `outputStyle` | 출력 스타일 구성 | `"Explanatory"` |
| `forceLoginMethod` | 로그인 방법 제한 | `claudeai` 또는 `console` |
| `forceLoginOrgUUID` | 조직 자동 선택 | `"xxxxxxxx-xxxx-..."` |
| `enableAllProjectMcpServers` | 프로젝트 MCP 서버 자동 승인 | `true` |
| `enabledMcpjsonServers` | 승인할 MCP 서버 목록 | `["memory", "github"]` |
| `disabledMcpjsonServers` | 거부할 MCP 서버 목록 | `["filesystem"]` |
| `allowedMcpServers` | MCP 서버 허용 목록 (Managed) | `[{ "serverName": "github" }]` |
| `deniedMcpServers` | MCP 서버 거부 목록 (Managed) | `[{ "serverName": "filesystem" }]` |
| `strictKnownMarketplaces` | 마켓플레이스 허용 목록 (Managed) | `[{ "source": "github", ... }]` |
| `awsAuthRefresh` | AWS 인증 새로고침 스크립트 | `aws sso login --profile myprofile` |
| `awsCredentialExport` | AWS 자격증명 JSON 출력 스크립트 | `/bin/generate_aws_grant.sh` |
| `alwaysThinkingEnabled` | 확장 사고 기본 활성화 | `true` |
| `plansDirectory` | 계획 파일 저장 위치 (기본: `~/.claude/plans`) | `"./plans"` |
| `showTurnDuration` | 턴 지속 시간 표시 | `true` |
| `language` | Claude 응답 언어 | `"japanese"` |
| `autoUpdatesChannel` | 업데이트 채널 | `"stable"` 또는 `"latest"` |
| `spinnerTipsEnabled` | 스피너 팁 표시 (기본: true) | `false` |
| `terminalProgressBarEnabled` | 터미널 진행률 표시줄 (기본: true) | `false` |

## 권한 설정

| 키 | 설명 | 예제 |
|----|------|------|
| `allow` | 허용하는 도구 사용 규칙 | `["Bash(git diff:*)"]` |
| `ask` | 확인 요청하는 규칙 | `["Bash(git push:*)"]` |
| `deny` | 거부하는 규칙 | `["WebFetch", "Read(./.env)"]` |
| `additionalDirectories` | 추가 작업 디렉토리 | `["../docs/"]` |
| `defaultMode` | 기본 권한 모드 | `"acceptEdits"` |
| `disableBypassPermissionsMode` | bypassPermissions 모드 비활성화 | `"disable"` |

## 속성 설정 (attribution)

| 키 | 설명 |
|----|------|
| `commit` | git 커밋 속성 (빈 문자열 = 숨김) |
| `pr` | PR 설명 속성 (빈 문자열 = 숨김) |

```json
{
  "attribution": {
    "commit": "Generated with AI\n\nCo-Authored-By: AI <ai@example.com>",
    "pr": ""
  }
}
```
