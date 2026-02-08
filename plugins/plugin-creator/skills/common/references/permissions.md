# Claude Code 권한 설정

> 원본: https://code.claude.com/docs/ko/settings#권한-설정

## 권한 규칙 구문

권한 규칙은 `Tool` 또는 `Tool(specifier)` 형식을 따릅니다.

### 규칙 평가 순서

1. **Deny** 규칙이 먼저 확인됨
2. **Ask** 규칙이 두 번째로 확인됨
3. **Allow** 규칙이 마지막으로 확인됨

첫 번째 일치하는 규칙이 동작을 결정합니다.

### 도구의 모든 사용 일치

괄호 없이 도구 이름만 사용:

| 규칙 | 효과 |
|------|------|
| `Bash` | **모든** Bash 명령과 일치 |
| `WebFetch` | **모든** 웹 가져오기 요청과 일치 |
| `Read` | **모든** 파일 읽기와 일치 |

> **주의**: `Bash(*)`는 모든 Bash 명령과 일치하지 **않습니다**. 도구의 모든 사용을 허용/거부하려면 도구 이름만 사용하세요.

### 세분화된 제어를 위한 지정자

| 규칙 | 효과 |
|------|------|
| `Bash(npm run build)` | 정확한 명령과 일치 |
| `Read(./.env)` | 현재 디렉토리의 `.env` 파일 |
| `WebFetch(domain:example.com)` | example.com 도메인 |

### 와일드카드 패턴

| 와일드카드 | 위치 | 동작 | 예제 |
|-----------|------|------|------|
| `:*` | 패턴 끝에만 | **접두사 매칭** (단어 경계 포함) | `Bash(ls:*)` - `ls -la` O, `lsof` X |
| `*` | 패턴의 어디든지 | **Glob 매칭** (단어 경계 없음) | `Bash(ls*)` - `ls -la` O, `lsof` O |

### 접두사 매칭 예제 (`:*`)

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run:*)",
      "Bash(git commit:*)",
      "Bash(docker compose:*)"
    ],
    "deny": [
      "Bash(git push:*)",
      "Bash(rm -rf:*)"
    ]
  }
}
```

### Glob 매칭 예제 (`*`)

```json
{
  "permissions": {
    "allow": [
      "Bash(git * main)",
      "Bash(* --version)"
    ]
  }
}
```

## 민감한 파일 제외

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(./config/credentials.json)",
      "Read(./build)"
    ]
  }
}
```

## 주의사항

> **경고**: Bash 권한 패턴으로 명령 인수를 제한하려는 시도는 취약합니다. 예: `Bash(curl http://github.com/:*)`는 `curl -X GET http://github.com/...` 또는 셸 변수를 사용하는 명령과 일치하지 않습니다. 인수 제한 패턴을 보안 경계로 사용하지 마세요.
