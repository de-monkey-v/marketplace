# --agents 플래그 JSON 형식

`--agents` 플래그로 플러그인 없이 동적으로 에이전트를 정의할 수 있습니다.

---

## 기본 형식

```bash
claude --agents '<JSON 배열>' "query"
```

JSON 배열에 에이전트 객체들을 정의합니다.

---

## 에이전트 객체 스키마

```typescript
interface AgentDefinition {
  name: string;           // 필수: 에이전트 이름
  description: string;    // 필수: 에이전트 설명 (트리거 조건)
  prompt: string;         // 필수: 시스템 프롬프트
  tools?: string[];       // 선택: 허용할 도구 목록
  model?: string;         // 선택: 사용할 모델
}
```

---

## 단일 에이전트 예제

```bash
claude --agents '[{
  "name": "code-reviewer",
  "description": "코드 리뷰 요청 시 사용",
  "prompt": "You are a senior code reviewer. Focus on code quality, security, and performance."
}]' "review this function"
```

---

## 다중 에이전트 예제

```bash
claude --agents '[
  {
    "name": "analyzer",
    "description": "코드 분석 요청 시 사용",
    "prompt": "Analyze code structure and patterns."
  },
  {
    "name": "fixer",
    "description": "버그 수정 요청 시 사용",
    "prompt": "Fix bugs with minimal changes."
  }
]' "analyze and fix this code"
```

---

## 도구 제한

특정 도구만 허용:

```bash
claude --agents '[{
  "name": "reader",
  "description": "코드 읽기 전용 에이전트",
  "prompt": "Read and explain code. Do not modify.",
  "tools": ["Read", "Grep", "Glob"]
}]' "explain this file"
```

---

## 모델 지정

에이전트별 다른 모델 사용:

```bash
claude --agents '[{
  "name": "quick-helper",
  "description": "간단한 질문용",
  "prompt": "Answer quickly and concisely.",
  "model": "haiku"
}]' "what is a closure?"
```

---

## 실용적인 예제

### 보안 리뷰어

```bash
claude --agents '[{
  "name": "security-reviewer",
  "description": "보안 취약점 검토",
  "prompt": "You are a security expert. Look for:\n- SQL injection\n- XSS vulnerabilities\n- Authentication issues\n- OWASP Top 10",
  "tools": ["Read", "Grep", "Glob"]
}]' "review security of auth module"
```

### 문서 작성자

```bash
claude --agents '[{
  "name": "documenter",
  "description": "문서화 작업",
  "prompt": "Write clear, concise documentation. Use JSDoc format for JavaScript.",
  "tools": ["Read", "Write", "Edit"]
}]' "document this API"
```

### 테스트 작성자

```bash
claude --agents '[{
  "name": "tester",
  "description": "테스트 코드 작성",
  "prompt": "Write comprehensive unit tests using Jest. Cover edge cases.",
  "tools": ["Read", "Write", "Grep"]
}]' "write tests for utils.ts"
```

---

## 파일에서 읽기

긴 에이전트 정의는 파일로 관리:

```bash
# agents.json 파일
cat > agents.json << 'EOF'
[
  {
    "name": "architect",
    "description": "아키텍처 설계 논의",
    "prompt": "You are a software architect. Consider scalability, maintainability, and best practices."
  },
  {
    "name": "implementer",
    "description": "기능 구현",
    "prompt": "Implement features following existing patterns in the codebase.",
    "tools": ["Read", "Write", "Edit", "Bash"]
  }
]
EOF

# 파일에서 읽어서 사용
claude --agents "$(cat agents.json)" "design and implement user auth"
```

---

## 플러그인 에이전트와의 차이

| 특성 | --agents | 플러그인 에이전트 |
|------|----------|-----------------|
| 정의 위치 | CLI 인자 | `agents/*.md` 파일 |
| 지속성 | 일회성 | 영구적 |
| 용도 | 빠른 프로토타이핑 | 재사용 가능한 에이전트 |
| 복잡도 | 단순 | 복잡한 설정 가능 |

**권장**: 반복 사용할 에이전트는 플러그인으로 만들고, 테스트/일회성 용도로 `--agents` 사용
