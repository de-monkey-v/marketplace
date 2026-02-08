# 플러그인 로컬 테스트 워크플로우

개발 중인 플러그인을 테스트하는 실용적인 방법을 안내합니다.

---

## 기본 테스트

### 플러그인 로드 확인

```bash
# 플러그인 디렉토리 지정
claude --plugin-dir ./my-plugin "list available commands"

# 여러 플러그인 동시 로드
claude --plugin-dir ./plugin-a --plugin-dir ./plugin-b "query"
```

### 커맨드 테스트

```bash
# 슬래시 커맨드 실행
claude --plugin-dir ./my-plugin "run /my-command"

# 인자와 함께
claude --plugin-dir ./my-plugin "run /my-command arg1 arg2"
```

### 스킬 트리거 테스트

```bash
# 스킬이 올바르게 활성화되는지 확인
claude --plugin-dir ./my-plugin "스킬 트리거 키워드"
```

---

## 디버그 모드 테스트

### 훅 동작 확인

```bash
# 훅 실행 로그 출력
claude --plugin-dir ./my-plugin --debug "hooks" "trigger my hook"
```

출력 예시:
```
[hooks] PreToolUse hook triggered: my-hook
[hooks] Hook result: allowed
```

### MCP 서버 테스트

```bash
# MCP 통신 로그
claude --plugin-dir ./my-plugin --debug "mcp" "use mcp tool"
```

### 전체 디버그

```bash
# 모든 로그 (노이즈 제외)
claude --plugin-dir ./my-plugin --debug "all,!statsig" "complex query"
```

---

## 권한 제한 테스트

### 읽기 전용 모드

```bash
# 수정 불가능한 환경에서 테스트
claude --plugin-dir ./my-plugin --allowedTools "Read,Grep,Glob" "analyze code"
```

### 특정 도구만 허용

```bash
# 플러그인이 특정 도구만 사용하는지 확인
claude --plugin-dir ./my-plugin --tools "Read,Write" "perform task"
```

### 위험한 도구 차단

```bash
# Bash 실행 차단
claude --plugin-dir ./my-plugin --disallowedTools "Bash" "try dangerous action"
```

---

## 에이전트 테스트

### 에이전트 호출 확인

```bash
# 에이전트가 올바르게 선택되는지
claude --plugin-dir ./my-plugin --debug "tool" "trigger agent description keyword"
```

### 에이전트 도구 제한 테스트

```bash
# 에이전트에 허용된 도구만 사용하는지 확인
claude --plugin-dir ./my-plugin --verbose "call my-agent"
```

---

## 자동화된 테스트

### 스크립트로 테스트

```bash
#!/bin/bash
# test-plugin.sh

PLUGIN_DIR="./my-plugin"

echo "=== Testing Commands ==="
claude --plugin-dir $PLUGIN_DIR -p "run /my-command"

echo "=== Testing Skills ==="
claude --plugin-dir $PLUGIN_DIR -p "skill trigger keyword"

echo "=== Testing Agents ==="
claude --plugin-dir $PLUGIN_DIR -p "agent trigger keyword"

echo "=== All tests completed ==="
```

### 출력 검증

```bash
# JSON 출력으로 검증
result=$(claude --plugin-dir ./my-plugin -p --output-format json "test query")

if echo "$result" | jq -e '.is_error == false' > /dev/null; then
  echo "Test passed"
else
  echo "Test failed"
  echo "$result" | jq '.result'
fi
```

---

## 실전 테스트 시나리오

### 시나리오 1: 새 스킬 테스트

```bash
# 1. 스킬 파일 작성 후

# 2. 트리거 테스트
claude --plugin-dir ./my-plugin "스킬 description에 있는 키워드"

# 3. 디버그로 로드 확인
claude --plugin-dir ./my-plugin --verbose "키워드"
```

### 시나리오 2: 훅 테스트

```bash
# 1. PreToolUse 훅 테스트
claude --plugin-dir ./my-plugin --debug "hooks" "use the tool that triggers hook"

# 2. 차단 동작 확인
claude --plugin-dir ./my-plugin --debug "hooks" "try blocked action"
```

### 시나리오 3: 커맨드 체이닝 테스트

```bash
# 복잡한 커맨드 흐름 테스트
claude --plugin-dir ./my-plugin --debug "all,!statsig,!file" \
  "run /complex-command with multiple steps"
```

---

## 문제 해결

### 플러그인이 로드되지 않을 때

```bash
# 1. plugin.json 확인
cat ./my-plugin/.claude-plugin/plugin.json | jq .

# 2. 디버그로 로드 과정 확인
claude --plugin-dir ./my-plugin --debug "all" "hello"
```

### 스킬이 트리거되지 않을 때

```bash
# description 키워드 확인
grep -r "description:" ./my-plugin/skills/

# verbose로 스킬 매칭 확인
claude --plugin-dir ./my-plugin --verbose "trigger keyword"
```

### 훅이 실행되지 않을 때

```bash
# hooks.json 문법 확인
cat ./my-plugin/hooks/hooks.json | jq .

# 이벤트 매칭 확인
claude --plugin-dir ./my-plugin --debug "hooks" "trigger event"
```
