# CLI 명령어 및 Slash Commands

## 검색 키워드
`CLI`, `명령어`, `플래그`, `단축키`, `설정`, `settings.json`, `인터랙티브`, `Vim`, `권한 모드`

---

## [CLI Reference](https://code.claude.com/docs/en/cli-reference)

**포함 주제**: CLI 명령어, 플래그, 시스템 프롬프트, 에이전트 정의

### 기본 CLI 명령어
```bash
claude                      # 인터랙티브 REPL 시작
claude "query"             # 초기 프롬프트와 함께 REPL 시작
claude -p "query"          # SDK 모드 (print mode) - 쿼리하고 종료
claude -c                  # 현재 디렉토리에서 최근 대화 계속
claude -r "session-name"   # 세션 ID 또는 이름으로 재개
```

### 주요 플래그
| 플래그 | 설명 | 예시 |
|--------|------|------|
| `--model` | 모델 변경 | `claude --model opus` |
| `--system-prompt` | 시스템 프롬프트 전체 대체 | `claude --system-prompt "You are..."` |
| `--append-system-prompt` | 기본 프롬프트에 추가 | `claude --append-system-prompt "Always use TS"` |
| `--tools` | 사용 가능 도구 제한 | `claude --tools "Bash,Edit,Read"` |
| `--permission-mode` | 권한 모드 설정 | `claude --permission-mode plan` |
| `--add-dir` | 추가 작업 디렉토리 | `claude --add-dir ../apps ../lib` |
| `--output-format` | 출력 형식 | `claude -p --output-format json "query"` |
| `--max-turns` | 에이전트 턴 수 제한 | `claude -p --max-turns 3 "query"` |
| `--verbose` | 상세 로깅 | `claude --verbose` |

### 에이전트 동적 정의
```bash
claude --agents '{
  "code-reviewer": {
    "description": "코드 검토 전문가",
    "prompt": "You are a senior code reviewer",
    "tools": ["Read", "Edit", "Bash"],
    "model": "sonnet"
  }
}'
```

---

## [Interactive Mode](https://code.claude.com/docs/en/interactive-mode)

**포함 주제**: 키보드 단축키, Vim 모드, 백그라운드 작업

### 필수 키보드 단축키
| 단축키 | 기능 |
|--------|------|
| `Ctrl+C` | 현재 입력/생성 취소 |
| `Ctrl+D` | Claude Code 종료 |
| `Ctrl+L` | 터미널 화면 초기화 |
| `Ctrl+R` | 역방향 명령 히스토리 검색 |
| `Ctrl+B` | 백그라운드 작업 실행 |
| `Ctrl+G` | 기본 텍스트 에디터에서 프롬프트 편집 |
| `Ctrl+O` | 상세 출력 토글 |
| `Shift+Tab` | 권한 모드 전환 |
| `Esc+Esc` | 코드/대화 되감기 |

### 빠른 명령어 (슬래시 명령어)
| 명령어 | 기능 |
|--------|------|
| `/help` | 사용 가능한 명령어 표시 |
| `/clear` | 대화 히스토리 삭제 |
| `/compact` | 대화 요약 |
| `/config` | 설정 인터페이스 열기 |
| `/memory` | CLAUDE.md 메모리 파일 편집 |
| `/plan` | 계획 모드 직접 진입 |
| `/resume` | 세션 재개 선택기 |
| `/status` | 상태 정보 표시 |
| `/tasks` | 백그라운드 작업 목록 |
| `/export` | 현재 대화를 파일로 내보내기 |
| `/model` | AI 모델 선택/변경 |

### 입력 모드
| 프리픽스 | 기능 | 예시 |
|----------|------|------|
| `!\` | Bash 직접 실행 | \`! npm test` |
| `/` | 명령어 또는 스킬 | `/clear` |
| `@` | 파일 경로 자동완성 | `@./src/main.py` |

### Vim 에디터 모드
- `/vim` 명령으로 활성화
- NORMAL 모드: h/j/k/l(이동), dd(삭제), yy(복사), p(붙여넣기)
- INSERT 모드: 일반 텍스트 입력

---

## [Settings](https://code.claude.com/docs/en/settings)

**포함 주제**: 설정 계층구조, JSON 설정, 환경 변수, 권한 규칙

### 설정 파일 계층
```
~/.claude/settings.json              # 사용자 전역 (모든 프로젝트)
  ↓
{project}/.claude/settings.json      # 프로젝트 (Git 체크인, 팀 공유)
  ↓
{project}/.claude/settings.local.json # 로컬 (Git 무시, 개인용)
```

### 설정 스코프
| 스코프 | 위치 | 용도 |
|--------|------|------|
| `user` | `~/.claude/settings.json` | 전역 설정 |
| `project` | `.claude/settings.json` | 팀 공유 설정 |
| `local` | `.claude/settings.local.json` | 개인 설정 |

### 설정 구성 예시
```json
{
  "model": "sonnet",
  "environmentVariables": {
    "NODE_ENV": "development",
    "DEBUG": "app:*"
  },
  "permissionRules": [
    { "tool": "Bash(git:*)", "permission": "allow" },
    { "tool": "Edit", "permission": "prompt" }
  ],
  "tools": ["Bash", "Edit", "Read", "Grep"],
  "maxTokens": 8000
}
```

---

## [Quickstart](https://code.claude.com/docs/en/quickstart)

**포함 주제**: 설치, 로그인, 첫 번째 세션, 권한 관리

### 설치 및 로그인
```bash
# NPM을 통한 설치
npm install -g @anthropic-ai/claude-code

# 첫 실행 (브라우저 로그인 창 열림)
claude
```

### 계정 요구사항
- Claude Pro/Max 구독 또는
- Claude Console 계정 (토큰 선불 결제)

### 권한 모드
| 모드 | 설명 |
|------|------|
| Normal | 각 변경사항마다 승인 요청 |
| Plan | 전체 계획 검토 후 승인 |
| Auto-Accept | 모든 변경 자동 승인 |

- `Shift+Tab`으로 모드 전환

### 3가지 접근 방식
| 방식 | 설명 |
|------|------|
| CLI (터미널) | `claude` 명령어로 직접 실행 |
| 데스크톱 앱 | 전용 UI 윈도우 |
| Claude.ai (웹) | 브라우저에서 세션 실행 및 동기화 |
