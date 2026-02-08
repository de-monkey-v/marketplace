# Claude Code 도구 목록

> 원본: https://code.claude.com/docs/ko/settings#claude가-사용할-수-있는-도구

## 사용 가능한 도구

| 도구 | 설명 | 권한 필요 |
|------|------|----------|
| **AskUserQuestion** | 요구사항 수집/모호함 명확히 하기 위한 객관식 질문 | 아니오 |
| **Bash** | 환경에서 셸 명령 실행 | 예 |
| **TaskOutput** | 백그라운드 작업 출력 검색 | 아니오 |
| **Edit** | 특정 파일에 대한 대상 편집 | 예 |
| **ExitPlanMode** | 계획 모드 종료 요청 | 예 |
| **Glob** | 패턴 매칭 기반 파일 찾기 | 아니오 |
| **Grep** | 파일 내용에서 패턴 검색 | 아니오 |
| **KillShell** | 실행 중인 백그라운드 bash 셸 종료 | 아니오 |
| **MCPSearch** | MCP 도구 검색 및 로드 (도구 검색 활성화 시) | 아니오 |
| **NotebookEdit** | Jupyter 노트북 셀 수정 | 예 |
| **Read** | 파일 내용 읽기 | 아니오 |
| **Skill** | 주 대화 내에서 skill 실행 | 예 |
| **Task** | sub-agent 실행 | 아니오 |
| **TaskCreate** | 작업 목록에 새 작업 생성 | 아니오 |
| **TaskGet** | 특정 작업 세부사항 검색 | 아니오 |
| **TaskList** | 모든 작업 나열 | 아니오 |
| **TaskUpdate** | 작업 상태/종속성/세부사항 업데이트 | 아니오 |
| **WebFetch** | URL에서 콘텐츠 가져오기 | 예 |
| **WebSearch** | 도메인 필터링 웹 검색 | 예 |
| **Write** | 파일 생성/덮어쓰기 | 예 |

## Bash 도구 동작

### 지속성 동작
- **작업 디렉토리 지속**: `cd` 명령 후 후속 명령은 해당 디렉토리에서 실행
- **환경 변수 비지속**: 한 명령에서 설정한 환경 변수는 후속 명령에서 사용 불가

### 환경 변수 사용 옵션

**옵션 1: Claude Code 시작 전 환경 활성화**
```bash
conda activate myenv
# 또는: source /path/to/venv/bin/activate
claude
```

**옵션 2: CLAUDE_ENV_FILE 설정**
```bash
export CLAUDE_ENV_FILE=/path/to/env-setup.sh
claude
```

env-setup.sh 내용:
```bash
conda activate myenv
# 또는: source /path/to/venv/bin/activate
# 또는: export MY_VAR=value
```

**옵션 3: SessionStart hook 사용**
```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "startup",
      "hooks": [{
        "type": "command",
        "command": "echo 'conda activate myenv' >> \"$CLAUDE_ENV_FILE\""
      }]
    }]
  }
}
```

## 도구 확장 (Hooks)

Claude Code hooks로 도구 실행 전후에 사용자 정의 명령 실행 가능:
- Python 파일 수정 후 포매터 자동 실행
- 특정 경로에 대한 Write 작업 차단
