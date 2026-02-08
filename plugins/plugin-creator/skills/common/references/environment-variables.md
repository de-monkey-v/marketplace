# Claude Code 환경 변수

> 원본: https://code.claude.com/docs/ko/settings#환경-변수

모든 환경 변수는 `settings.json`의 `env` 키에서도 구성 가능합니다.

## 인증 관련

| 변수 | 목적 |
|------|------|
| `ANTHROPIC_API_KEY` | API 키 (X-Api-Key 헤더) |
| `ANTHROPIC_AUTH_TOKEN` | Authorization 헤더 값 (Bearer 접두사 붙음) |
| `ANTHROPIC_CUSTOM_HEADERS` | 사용자 정의 헤더 (`Name: Value` 형식) |
| `ANTHROPIC_FOUNDRY_API_KEY` | Microsoft Foundry 인증용 API 키 |
| `AWS_BEARER_TOKEN_BEDROCK` | Bedrock API 키 |

## 모델 관련

| 변수 | 목적 |
|------|------|
| `ANTHROPIC_MODEL` | 사용할 모델 설정 이름 |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Haiku 모델 설정 |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Opus 모델 설정 |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Sonnet 모델 설정 |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Subagent 모델 |

## 공급자 관련

| 변수 | 목적 |
|------|------|
| `CLAUDE_CODE_USE_BEDROCK` | Bedrock 사용 |
| `CLAUDE_CODE_USE_FOUNDRY` | Microsoft Foundry 사용 |
| `CLAUDE_CODE_USE_VERTEX` | Vertex 사용 |
| `CLAUDE_CODE_SKIP_BEDROCK_AUTH` | Bedrock AWS 인증 건너뛰기 |
| `CLAUDE_CODE_SKIP_FOUNDRY_AUTH` | Foundry Azure 인증 건너뛰기 |
| `CLAUDE_CODE_SKIP_VERTEX_AUTH` | Vertex Google 인증 건너뛰기 |

## Bash 도구 관련

| 변수 | 목적 |
|------|------|
| `BASH_DEFAULT_TIMEOUT_MS` | 기본 시간 초과 |
| `BASH_MAX_OUTPUT_LENGTH` | 최대 출력 문자 수 |
| `BASH_MAX_TIMEOUT_MS` | 최대 시간 초과 |
| `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR` | 명령 후 원래 디렉토리로 복귀 |

## 컨텍스트/토큰 관련

| 변수 | 목적 |
|------|------|
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 자동 압축 트리거 백분율 (1-100) |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | 최대 출력 토큰 수 (기본: 32,000, 최대: 64,000) |
| `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` | 파일 읽기 토큰 제한 |
| `MAX_MCP_OUTPUT_TOKENS` | MCP 응답 최대 토큰 (기본: 25000) |
| `MAX_THINKING_TOKENS` | 확장 사고 토큰 예산 |

## MCP 관련

| 변수 | 목적 |
|------|------|
| `MCP_TIMEOUT` | MCP 서버 시작 시간 초과 (ms) |
| `MCP_TOOL_TIMEOUT` | MCP 도구 실행 시간 초과 (ms) |
| `ENABLE_TOOL_SEARCH` | MCP 도구 검색 (`auto`, `auto:N`, `true`, `false`) |

## 비활성화 관련

| 변수 | 목적 |
|------|------|
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | 모든 비필수 트래픽 비활성화 |
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` | 백그라운드 작업 비활성화 |
| `CLAUDE_CODE_DISABLE_TERMINAL_TITLE` | 터미널 제목 자동 업데이트 비활성화 |
| `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` | 실험적 베타 헤더 비활성화 |
| `DISABLE_AUTOUPDATER` | 자동 업데이트 비활성화 |
| `DISABLE_BUG_COMMAND` | /bug 명령 비활성화 |
| `DISABLE_COST_WARNINGS` | 비용 경고 비활성화 |
| `DISABLE_ERROR_REPORTING` | Sentry 오류 보고 거부 |
| `DISABLE_TELEMETRY` | Statsig 원격 분석 거부 |
| `DISABLE_NON_ESSENTIAL_MODEL_CALLS` | 비필수 모델 호출 비활성화 |
| `DISABLE_INSTALLATION_CHECKS` | 설치 경고 비활성화 |
| `DISABLE_PROMPT_CACHING` | 프롬프트 캐싱 비활성화 |
| `DISABLE_PROMPT_CACHING_HAIKU` | Haiku 프롬프트 캐싱 비활성화 |
| `DISABLE_PROMPT_CACHING_OPUS` | Opus 프롬프트 캐싱 비활성화 |
| `DISABLE_PROMPT_CACHING_SONNET` | Sonnet 프롬프트 캐싱 비활성화 |

## 프록시 관련

| 변수 | 목적 |
|------|------|
| `HTTP_PROXY` | HTTP 프록시 서버 |
| `HTTPS_PROXY` | HTTPS 프록시 서버 |
| `NO_PROXY` | 프록시 우회 도메인/IP 목록 |
| `CLAUDE_CODE_PROXY_RESOLVES_HOSTS` | 프록시가 DNS 해석 수행 |

## 기타

| 변수 | 목적 |
|------|------|
| `CLAUDE_CONFIG_DIR` | 구성/데이터 파일 저장 위치 |
| `CLAUDE_CODE_TMPDIR` | 임시 파일 디렉토리 |
| `CLAUDE_CODE_SHELL` | 셸 자동 감지 재정의 |
| `CLAUDE_CODE_SHELL_PREFIX` | bash 명령 래핑 접두사 |
| `CLAUDE_CODE_TASK_LIST_ID` | 세션 간 작업 목록 공유 |
| `CLAUDE_CODE_EXIT_AFTER_STOP_DELAY` | 유휴 후 자동 종료 시간 (ms) |
| `CLAUDE_CODE_HIDE_ACCOUNT_INFO` | UI에서 이메일/조직명 숨기기 |
| `CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL` | IDE 확장 자동 설치 건너뛰기 |
| `IS_DEMO` | 데모 모드 활성화 |
| `USE_BUILTIN_RIPGREP` | 시스템 설치 rg 사용 (`0`으로 설정) |
| `SLASH_COMMAND_TOOL_CHAR_BUDGET` | Skill 메타데이터 최대 문자 수 (기본: 15000) |
| `FORCE_AUTOUPDATE_PLUGINS` | 플러그인 자동 업데이트 강제 |
