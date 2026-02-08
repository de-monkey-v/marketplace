# 시스템 프롬프트 플래그 상세

Claude Code의 시스템 프롬프트를 커스터마이징하는 4가지 플래그를 설명합니다.

---

## 플래그 비교

| 플래그 | 동작 | 소스 |
|--------|------|------|
| `--system-prompt` | 시스템 프롬프트 **교체** | 텍스트 직접 입력 |
| `--append-system-prompt` | 시스템 프롬프트에 **추가** | 텍스트 직접 입력 |
| `--system-prompt-file` | 시스템 프롬프트 **교체** | 파일에서 읽기 |
| `--append-system-prompt-file` | 시스템 프롬프트에 **추가** | 파일에서 읽기 |

---

## 교체 vs 추가

### --system-prompt (교체)

기본 시스템 프롬프트를 **완전히 대체**합니다:

```bash
claude --system-prompt "You are a Python expert. Only answer Python questions." \
  "how to read a file?"
```

**주의**: 기본 프롬프트가 제거되므로 도구 사용 지침 등이 사라질 수 있습니다.

### --append-system-prompt (추가)

기본 시스템 프롬프트 **끝에 추가**합니다:

```bash
claude --append-system-prompt "Always respond in Korean. 항상 한국어로 답변하세요." \
  "explain recursion"
```

**권장**: 대부분의 경우 `--append-system-prompt` 사용을 권장합니다.

---

## 텍스트 vs 파일

### 텍스트 직접 입력

짧은 프롬프트에 적합:

```bash
claude --append-system-prompt "Be concise. Limit responses to 100 words."
```

### 파일에서 읽기

긴 프롬프트나 재사용 시 적합:

```bash
# prompt.txt 파일 생성
echo "You are a security expert. Focus on:
- Vulnerability detection
- Secure coding practices
- OWASP guidelines" > prompt.txt

# 파일에서 읽기
claude --append-system-prompt-file prompt.txt "review this code"
```

---

## 사용 시나리오

### 1. 언어/스타일 지정

```bash
# 한국어 응답 강제
claude --append-system-prompt "항상 한국어로 답변하세요." "what is closure?"

# 간결한 응답 요청
claude --append-system-prompt "Be extremely concise. Use bullet points." "explain REST"
```

### 2. 역할 부여

```bash
# 코드 리뷰어 역할
claude --append-system-prompt "You are a senior code reviewer. Focus on:
- Code quality and readability
- Performance implications
- Security concerns" "review this PR"
```

### 3. 출력 형식 지정

```bash
# JSON 출력 강제
claude --append-system-prompt "Always respond with valid JSON. No markdown." \
  -p "list 3 programming languages with their paradigms"
```

### 4. 도메인 전문가

```bash
# 보안 전문가
claude --append-system-prompt-file security-expert.txt "analyze this code"
```

---

## Interactive vs Print 모드

### Interactive 모드 (기본)

시스템 프롬프트가 전체 세션에 적용:

```bash
claude --append-system-prompt "Focus on TypeScript"
# 이후 모든 대화에 적용됨
```

### Print 모드 (-p)

단일 요청에만 적용:

```bash
claude -p --append-system-prompt "Be concise" "explain monads"
# 한 번의 응답 후 종료
```

---

## 조합 사용

여러 플래그를 조합할 수 있습니다:

```bash
# 파일 + 추가 텍스트
claude --append-system-prompt-file base-prompt.txt \
  --append-system-prompt "Also consider performance." \
  "review code"
```

**적용 순서**:
1. 기본 시스템 프롬프트
2. `--system-prompt-file` (있으면 교체)
3. `--system-prompt` (있으면 교체)
4. `--append-system-prompt-file` (추가)
5. `--append-system-prompt` (추가)

---

## 권장 사항

| 상황 | 권장 플래그 |
|------|------------|
| 언어/스타일 변경 | `--append-system-prompt` |
| 역할 부여 | `--append-system-prompt` |
| 완전히 다른 동작 | `--system-prompt` (주의) |
| 긴 프롬프트 | `--append-system-prompt-file` |
| 재사용 가능한 프롬프트 | `--append-system-prompt-file` |

**일반적으로 `--append-*` 버전을 사용하세요.** 기본 프롬프트의 도구 사용 지침을 유지하면서 커스터마이징할 수 있습니다.
