# Claude Code 구성 범위

> 원본: https://code.claude.com/docs/ko/settings#구성-범위

## 사용 가능한 범위

| 범위 | 위치 | 영향을 받는 대상 | 팀과 공유? |
|------|------|---------------|-----------|
| **Managed** | 시스템 수준 `managed-settings.json` | 머신의 모든 사용자 | 예 (IT에서 배포) |
| **User** | `~/.claude/` 디렉토리 | 모든 프로젝트에서 사용자 | 아니오 |
| **Project** | 저장소의 `.claude/` | 이 저장소의 모든 협업자 | 예 (git에 커밋됨) |
| **Local** | `.claude/*.local.*` 파일 | 이 저장소에서만 사용자 | 아니오 (gitignored) |

## 각 범위를 사용하는 시기

### Managed 범위
- 조직 전체에서 적용해야 하는 보안 정책
- 재정의할 수 없는 규정 준수 요구사항
- IT/DevOps에서 배포한 표준화된 구성

### User 범위
- 모든 곳에서 원하는 개인 설정 (테마, 편집기 설정)
- 모든 프로젝트에서 사용하는 도구 및 플러그인
- API 키 및 인증 (안전하게 저장됨)

### Project 범위
- 팀 공유 설정 (권한, hooks, MCP 서버)
- 전체 팀이 가져야 할 플러그인
- 협업자 간 도구 표준화

### Local 범위
- 특정 프로젝트에 대한 개인 재정의
- 팀과 공유하기 전에 구성 테스트
- 다른 사용자에게는 작동하지 않을 머신 특정 설정

## 범위 우선순위

동일한 설정이 여러 범위에서 구성되면 더 구체적인 범위가 우선합니다:

1. **Managed** (최상위) - 아무것도 재정의할 수 없음
2. **명령줄 인수** - 임시 세션 재정의
3. **Local** - 프로젝트 및 사용자 설정 재정의
4. **Project** - 사용자 설정 재정의
5. **User** (최하위) - 다른 것이 설정을 지정하지 않을 때 적용

## 범위별 파일 위치

| 기능 | 사용자 위치 | 프로젝트 위치 | Local 위치 |
|------|-----------|-------------|-----------|
| **Settings** | `~/.claude/settings.json` | `.claude/settings.json` | `.claude/settings.local.json` |
| **Subagents** | `~/.claude/agents/` | `.claude/agents/` | — |
| **MCP servers** | `~/.claude.json` | `.mcp.json` | `~/.claude.json` (프로젝트별) |
| **Plugins** | `~/.claude/settings.json` | `.claude/settings.json` | `.claude/settings.local.json` |
| **CLAUDE.md** | `~/.claude/CLAUDE.md` | `CLAUDE.md` 또는 `.claude/CLAUDE.md` | `CLAUDE.local.md` |
