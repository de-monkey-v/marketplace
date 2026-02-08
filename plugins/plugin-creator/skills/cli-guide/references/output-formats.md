# SDK 출력 형식 가이드

Claude Code SDK 모드(-p)에서 사용하는 출력/입력 형식을 설명합니다.

---

## --output-format

응답 출력 형식을 지정합니다.

### text (기본)

일반 텍스트 출력:

```bash
claude -p "what is 2+2"
# 출력: 4
```

### json

구조화된 JSON 객체:

```bash
claude -p --output-format json "what is 2+2"
```

```json
{
  "type": "result",
  "subtype": "success",
  "cost_usd": 0.003,
  "is_error": false,
  "duration_ms": 1234,
  "duration_api_ms": 1000,
  "num_turns": 1,
  "result": "4",
  "session_id": "abc123"
}
```

### stream-json

줄별 JSON 스트림 (실시간 처리용):

```bash
claude -p --output-format stream-json "explain recursion"
```

각 줄이 독립적인 JSON 객체:

```jsonl
{"type":"assistant","message":{"content":"Recursion is..."}}
{"type":"assistant","message":{"content":" a technique..."}}
{"type":"result","result":"...","cost_usd":0.005}
```

---

## --input-format

입력 형식을 지정합니다 (stdin 사용 시).

### text (기본)

일반 텍스트 입력:

```bash
echo "what is 2+2" | claude -p
```

### stream-json

스트리밍 JSON 입력:

```bash
echo '{"type":"user","message":"what is 2+2"}' | claude -p --input-format stream-json
```

---

## --json-schema

출력을 특정 JSON 스키마에 맞게 강제합니다.

### 기본 사용

```bash
claude -p --json-schema '{
  "type": "object",
  "properties": {
    "answer": {"type": "number"}
  },
  "required": ["answer"]
}' "what is 2+2"
```

출력:
```json
{"answer": 4}
```

### 복잡한 스키마

```bash
claude -p --json-schema '{
  "type": "object",
  "properties": {
    "summary": {"type": "string"},
    "issues": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "severity": {"enum": ["low", "medium", "high"]},
          "description": {"type": "string"},
          "line": {"type": "number"}
        }
      }
    }
  },
  "required": ["summary", "issues"]
}' "review this code: $(cat file.js)"
```

### 파일에서 스키마 읽기

```bash
# schema.json 파일
cat > schema.json << 'EOF'
{
  "type": "object",
  "properties": {
    "tasks": {
      "type": "array",
      "items": {"type": "string"}
    },
    "priority": {"enum": ["low", "medium", "high"]}
  }
}
EOF

# 사용
claude -p --json-schema "$(cat schema.json)" "extract tasks from this email"
```

---

## --include-partial-messages

스트리밍 모드에서 중간 메시지 포함:

```bash
claude -p --output-format stream-json --include-partial-messages "long explanation"
```

토큰 단위로 실시간 출력을 받을 수 있습니다.

---

## 실용적인 패턴

### 1. 파이프라인에서 JSON 처리

```bash
# jq로 결과 추출
claude -p --output-format json "what is 2+2" | jq -r '.result'

# 에러 체크
result=$(claude -p --output-format json "query")
if echo "$result" | jq -e '.is_error' > /dev/null; then
  echo "Error occurred"
fi
```

### 2. 구조화된 코드 리뷰

```bash
claude -p --json-schema '{
  "type": "object",
  "properties": {
    "score": {"type": "number", "minimum": 0, "maximum": 10},
    "issues": {"type": "array", "items": {"type": "string"}},
    "suggestions": {"type": "array", "items": {"type": "string"}}
  }
}' "review: $(git diff HEAD~1)"
```

### 3. 자동화 스크립트

```bash
#!/bin/bash
# 여러 파일 분석 후 JSON 병합

for file in src/*.ts; do
  claude -p --output-format json \
    --json-schema '{"type":"object","properties":{"file":{"type":"string"},"complexity":{"type":"number"}}}' \
    "analyze complexity of: $(cat $file)"
done | jq -s '.'
```

### 4. 실시간 스트리밍 처리

```bash
# Node.js로 스트리밍 처리
claude -p --output-format stream-json "long task" | node -e "
const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
  const data = JSON.parse(line);
  if (data.type === 'assistant') {
    process.stdout.write(data.message.content || '');
  }
});
"
```

---

## 주의사항

1. **--json-schema는 출력만 강제**: 입력은 여전히 자연어
2. **스키마 복잡도 제한**: 너무 복잡한 스키마는 응답 품질 저하 가능
3. **stream-json + json-schema**: 함께 사용 시 최종 결과만 스키마 적용
4. **비용**: JSON 출력이 텍스트보다 약간 더 많은 토큰 사용
