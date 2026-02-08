# Hooks (훅)

## 검색 키워드
`hook`, `훅`, `PreToolUse`, `PostToolUse`, `SessionStart`, `이벤트`, `자동화`, `matcher`, `command`, `prompt`

---

## [Hooks](https://code.claude.com/docs/en/hooks)

**포함 주제**: 훅 개념, 이벤트 타입, 설정 방식, 매처 패턴

### 훅의 개념
- Claude Code 세션 중 특정 시점에 실행되는 **이벤트 기반 자동화** 메커니즘
- 도구 호출 전후, 세션 시작/종료, 권한 요청 등 라이프사이클 포인트에서 동작

### 훅 타입
| 타입 | 설명 |
|------|------|
| `command` | bash 명령어 실행 |
| `prompt` | LLM으로 허용/차단 여부 동적 판단 |

### 훅 이벤트 (12가지)
| 이벤트 | 시점 | 블로킹 |
|--------|------|--------|
| `PreToolUse` | 도구 호출 전 | O |
| `PostToolUse` | 도구 호출 후 | X |
| `PostToolUseFailure` | 도구 실패 후 | X |
| `PermissionRequest` | 권한 요청 시 | O (자동 승인/거부) |
| `SessionStart` | 세션 시작 | X |
| `SessionEnd` | 세션 종료 | X |
| `PreCompact` | 컨텍스트 압축 전 | X |

### 매처 패턴
| 패턴 | 예시 | 설명 |
|------|------|------|
| 정확 일치 | `"Write"` | Write 도구만 |
| 정규식 | `"Edit\|Write"` | 여러 도구 |
| 와일드카드 | `"*"` | 모든 도구 |
| 빈 값 | `""` | 도구 구분 없이 모든 이벤트 |

### 설정 구조 예시
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "your-command"
          }
        ]
      }
    ]
  }
}
```

---

## [Plugins Reference - 훅 섹션](https://code.claude.com/docs/en/plugins-reference)

**포함 주제**: 플러그인 내 훅 정의, 훅 병합 메커니즘

### 훅 정의 위치
- 플러그인 루트의 `hooks/hooks.json` 파일
- 또는 `plugin.json`의 `hooks` 필드에 직접 설정
- 플러그인 활성화 시 자동 로드

### 훅 병합 및 실행 순서
1. 사용자 설정 (`~/.claude/hooks.json`)
2. 프로젝트 설정 (`.claude/hooks.json`)
3. 플러그인 설정 (`hooks/hooks.json`)

- 여러 출처의 훅이 같은 이벤트에 동시 응답 가능

---

## 설정 위치 요약

| 범위 | 위치 |
|------|------|
| 전역 | `~/.claude/hooks.json` |
| 프로젝트 | `.claude/hooks.json` |
| 플러그인 | `hooks/hooks.json` |

---

## 실전 예제

### 환경 파일 보호 훅
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -c \"import json, sys; data=json.load(sys.stdin); path=data.get('tool_input',{}).get('file_path',''); sys.exit(2 if any(p in path for p in ['.env', 'package-lock.json', '.git/']) else 0)\""
          }
        ]
      }
    ]
  }
}
```
