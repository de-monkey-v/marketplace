# 디버깅 패턴 및 예제

Claude Code CLI의 디버깅 기능을 활용하는 패턴을 안내합니다.

---

## --debug 기본 사용법

### 카테고리 지정

```bash
# 단일 카테고리
claude --debug "mcp" "query"

# 여러 카테고리
claude --debug "api,mcp,hooks" "query"

# 모든 카테고리
claude --debug "all" "query"
```

### 카테고리 제외

`!` 접두사로 특정 카테고리 제외:

```bash
# statsig 제외
claude --debug "all,!statsig" "query"

# 여러 카테고리 제외
claude --debug "all,!statsig,!file,!cost" "query"
```

---

## 디버그 카테고리 상세

### api

API 요청/응답 로깅:

```bash
claude --debug "api" "query"
```

확인 가능한 정보:
- 요청 페이로드
- 응답 내용
- 토큰 사용량
- 지연 시간

### mcp

MCP 서버 통신:

```bash
claude --debug "mcp" "use mcp tool"
```

확인 가능한 정보:
- 서버 연결 상태
- 도구 호출 요청/응답
- 에러 메시지

### hooks

훅 트리거 및 실행:

```bash
claude --debug "hooks" "trigger hook action"
```

확인 가능한 정보:
- 훅 매칭
- 실행 결과 (allow/block)
- 훅 응답 메시지

### file

파일 작업:

```bash
claude --debug "file" "read some files"
```

확인 가능한 정보:
- 파일 읽기/쓰기 경로
- 파일 크기
- 권한 체크

### tool

도구 호출:

```bash
claude --debug "tool" "perform task"
```

확인 가능한 정보:
- 도구 선택 과정
- 파라미터
- 실행 결과

---

## --verbose와 조합

`--verbose`는 실행 상세 정보를 추가로 출력합니다:

```bash
# 디버그 + 상세 정보
claude --debug "mcp" --verbose "use mcp tool"

# 전체 정보
claude --debug "all,!statsig" --verbose "complex query"
```

---

## 문제별 디버깅 패턴

### 패턴 1: MCP 서버 연결 문제

```bash
# 1. MCP 통신 로그 확인
claude --debug "mcp" --verbose "call mcp tool"

# 2. 서버 설정 확인
claude mcp list

# 3. 서버 상태 테스트
claude mcp test my-server
```

예상 로그:
```
[mcp] Connecting to server: my-server
[mcp] Connection failed: ECONNREFUSED
```

### 패턴 2: 훅이 예상대로 동작하지 않음

```bash
# 1. 훅 매칭 확인
claude --plugin-dir ./my-plugin --debug "hooks" "trigger action"

# 2. 훅 응답 확인
claude --plugin-dir ./my-plugin --debug "hooks" --verbose "blocked action"
```

예상 로그:
```
[hooks] PreToolUse event: Write
[hooks] Checking hook: my-write-hook
[hooks] Hook matched, executing...
[hooks] Result: block (reason: "Not allowed")
```

### 패턴 3: 도구 권한 문제

```bash
# 1. 도구 호출 로그 확인
claude --debug "tool" "use specific tool"

# 2. 권한 설정 확인
claude --debug "tool" --allowedTools "Read,Grep" "try write"
```

예상 로그:
```
[tool] Tool request: Write
[tool] Permission check: denied (not in allowedTools)
```

### 패턴 4: API 응답 문제

```bash
# 1. API 통신 확인
claude --debug "api" "query"

# 2. 토큰/비용 확인
claude --debug "api,cost" "long query"
```

예상 로그:
```
[api] Request sent: 1234 tokens
[api] Response received: 5678 tokens
[cost] Estimated cost: $0.015
```

### 패턴 5: 플러그인 로드 문제

```bash
# 1. 전체 로드 과정 확인
claude --plugin-dir ./my-plugin --debug "all" --verbose "hello"

# 2. 특정 컴포넌트 확인
claude --plugin-dir ./my-plugin --debug "hooks,mcp" "query"
```

---

## 디버그 출력 저장

### 파일로 저장

```bash
# stderr를 파일로 리다이렉트 (디버그 로그는 stderr)
claude --debug "all" "query" 2> debug.log

# stdout과 stderr 분리
claude --debug "all" "query" > output.txt 2> debug.log
```

### 분석용 JSON 출력

```bash
# JSON 출력 + 디버그
claude -p --output-format json --debug "api" "query" 2> debug.log
cat debug.log  # 디버그 로그
```

---

## 일반적인 문제 해결

### "Tool not found" 에러

```bash
# 도구 목록 확인
claude --debug "tool" "list tools"

# 허용된 도구 확인
claude --allowedTools "Read,Write" --debug "tool" "query"
```

### "Permission denied" 에러

```bash
# 권한 모드 확인
claude --debug "tool" --permission-mode default "query"

# 자동 허용으로 테스트
claude --debug "tool" --permission-mode auto "query"
```

### "MCP server not responding" 에러

```bash
# 서버 상태 확인
claude --debug "mcp" --verbose "use mcp"

# 서버 재시작 후 테스트
claude mcp restart my-server
claude --debug "mcp" "use mcp"
```

### "Hook execution failed" 에러

```bash
# 훅 실행 상세 확인
claude --plugin-dir ./plugin --debug "hooks" --verbose "trigger"

# hooks.json 문법 확인
cat ./plugin/hooks/hooks.json | jq .
```

---

## 팁

1. **점진적 디버깅**: 특정 카테고리부터 시작, 필요시 확장
2. **노이즈 제거**: `!statsig,!file` 등으로 불필요한 로그 제외
3. **로그 저장**: 복잡한 문제는 파일로 저장 후 분석
4. **재현 가능한 쿼리**: 같은 쿼리로 반복 테스트
