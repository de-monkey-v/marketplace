# Commit Message Format Reference

Commit message format rules. **Default is the detailed format.**

---

## Required Rules

**Commit message language resolution:**
- Resolve language via: `$ARGUMENTS` flag → current conversation / recent history → `.hyper-team/metadata.json` hint → default `kor`
- Write the subject and bullet contents in the resolved language
- Keep section labels such as `What`, `Why`, `Impact`, and `Notes` in English unless the repository explicitly defines different labels
- Code paths, issue numbers, and technical terms remain as-is
- If the user asks in Korean, keep the commit message content in Korean unless the repository explicitly requires another language

**Signatures are NEVER allowed:**
- `generated with [Claude Code]` — forbidden
- `Co-Authored-By: Claude` — forbidden
- `🤖` emoji — forbidden

---

## Detailed Format (Default)

Full Conventional Commits with structured body sections:

```
<type>(scope): 간결한 제목 (50자 내외)

What
구체적으로 무엇을 바꿨는지 작성한다.

- `path/to/file.ts`: 변경 요약
- 추가한 클래스/함수/메서드
- 수정한 핵심 로직
- 제거한 요소

Why
왜 바꿨는지와 이전 동작 대비 차이를 작성한다.

- Background: 변경 배경
- Problem: 해결하려는 문제
- Effect: 기대 효과

Impact — if applicable
- 영향 받는 기능/모듈
- 의존성 변경 (추가/제거/수정)
- 성능 영향

Notes — if applicable
- 확인할 테스트 시나리오
- 주의 사항
- 관련 문서 링크

Fixes: #123
Related: #456
BREAKING CHANGE: description of API change (if applicable)
```

### Format Rules

- **Subject**: Max 50 characters, imperative mood, no period
- **Body**: Wrap at 72 characters
- **Blank line**: Required between subject and body
- **Footer**: Issue references, Breaking Changes, etc.

### Scope Rules

Scope is extracted from changed file paths:

| File Path | Scope |
|-----------|-------|
| `src/auth/*.java` | `(auth)` |
| `plugins/git-utils/*` | `(git-utils)` |
| `api/users/*.ts` | `(users)` |
| Multiple unrelated areas | omit scope |

### What Section

Describe **what** was changed in concrete terms:
- **Per-file changes**: `path/to/file.ts`: change summary format
- **Added**: New classes, functions, methods
- **Modified**: Core logic changes
- **Removed**: Deleted code, features, dependencies

### Why Section

Explain **why** the change was made with context and motivation:
- **Background**: Situation or context that led to the change
- **Problem**: Specific issue in the previous code
- **Effect**: Expected improvements after the change

### Impact Section (optional)

Specify the scope of impact:
- Affected features, modules, services
- Dependency changes (added/removed/updated)
- Performance impact (if any)

### Notes Section (optional)

Additional information:
- Test scenarios to verify
- Migration requirements
- Caveats, related documentation links

### Footer (Issue References)

Link related issues:
- Extract from branch name: `feature/123-xxx` → `Fixes: #123`
- Manually specified issues: `Related: #456`
- Breaking changes: `BREAKING CHANGE: description`

---

## Simple Format (`--simple` flag)

Brief numbered list format:

```
<type>: 간결한 제목 (50자 내외)

1. 주요 변경 사항
2. 보조 변경 사항
3. 추가 설명 (필요 시)
```

Use `--simple` or `-s` flag when:
- Quick, small changes
- Self-explanatory fixes
- Personal/local commits

---

## Subject Rules (Common)

| Rule | Correct Example | Wrong Example |
|------|----------------|---------------|
| Max 50 chars | `<feat>: 로그인 추가` | `<feat>: JWT 기반 로그인과 세션 복구 및 보안 보강 추가` |
| Imperative mood | `로그인 추가` | `로그인을 추가함` |
| No trailing period | `<fix>: 오류 수정` | `<fix>: 오류 수정.` |
| Resolved language | `<feat>: add login` (eng) / `<feat>: 로그인 추가` (kor) | Mismatch with resolved language |

---

## Complete Examples

### Detailed: Feature Addition

```
<feat>(auth): OAuth2 소셜 로그인 추가

What
- `src/auth/OAuthService.ts`: Google, Kakao OAuth2 클라이언트 구현
- `src/auth/JwtTokenProvider.ts`: 토큰 생성/검증 로직 추가
- `src/api/AuthController.ts`: /login, /callback 엔드포인트 추가
- OAuthService 클래스 추가
- JwtTokenProvider.generateToken() 메서드 추가

Why
- Background: 소셜 로그인 요청이 지속적으로 들어옴
- Problem: 이메일/비밀번호 가입 이탈률이 높음
- Effect: 가입 전환율 개선과 비밀번호 관리 부담 감소

Impact
- 인증 모듈 전반에 영향
- 새 의존성: passport-oauth2, jsonwebtoken
- 기존 세션 인증과 함께 동작

Fixes: #42
Related: #38
```

### Detailed: Bug Fix

```
<fix>(api): 동시 요청 시 세션 충돌 수정

What
- `src/middleware/session.ts`: 세션 락 처리 추가
- `src/utils/mutex.ts`: Redis 기반 분산 락 유틸 추가
- `src/config/redis.ts`: Redis 클라이언트 설정 추가

Why
- Background: 운영 환경에서 간헐적인 세션 유실 제보가 발생
- Problem: 동일 사용자 동시 요청에서 race condition 발생
- Effect: 세션 무결성 보장, 오류율 감소

Impact
- 인증이 필요한 API 전반에 영향
- 새 의존성: ioredis
- 평균 응답 시간 5ms 증가 가능

Notes
- 로컬 테스트 시 Redis 실행 필요
- 기존 세션은 자동 마이그레이션됨

Fixes: #156
```

### Detailed: Refactoring

```
<refactor>(user): UserService 책임 분리

What
- `src/services/UserService.ts`: 사용자 CRUD 핵심만 유지
- `src/services/UserAuthService.ts`: 인증 로직 분리
- `src/services/UserNotificationService.ts`: 알림 로직 분리
- UserService 크기 축소

Why
- Background: UserService가 20개 이상의 메서드로 비대해짐
- Problem: 단일 책임 원칙 위반으로 테스트와 유지보수가 어려움
- Effect: 책임이 명확해지고 단위 테스트 작성이 쉬워짐

Impact
- UserService를 쓰는 컨트롤러 import 경로 조정 필요
- 기존 API 동작은 유지됨

Related: #89
```

### Simple: Minor Fix

```
<fix>: UserService null 처리 수정

1. `user.email` 접근 전 null 체크 추가
2. null 대신 empty Optional 반환
```

### Simple: Documentation Update

```
<docs>: API 문서 업데이트

1. 인증 엔드포인트 예시 추가
2. 오류 응답 포맷 문서화
3. rate limiting 정보 추가
```

---

## Prohibited

**Never include:**

```
# Wrong: auto-generated signature included
<feat>: add feature

What
- change details

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Quality Checklist

Self-review before committing:

### Basic Format
- [ ] Uses one of the 11 valid types
- [ ] `<type>:` or `<type>(scope):` format (angle brackets required)
- [ ] Subject within 50 characters
- [ ] **Subject and bullet contents are written in the resolved language**
- [ ] **Section labels remain `What`, `Why`, `Impact`, `Notes` unless repo docs say otherwise**
- [ ] No auto-generated signatures
- [ ] No sensitive files included

### Content Quality
- [ ] Can the change be understood from the subject alone?
- [ ] Does the body explain "why" the change was made?
- [ ] Will this commit be understandable 6 months from now?
- [ ] Can another developer understand the context?

---

## Anti-patterns to Avoid

**Vague messages:**
- Bad: `<fix>: 버그 수정` → Good: `<fix>(auth): 로그인 시 세션 만료 처리 수정`
- Bad: `<feat>: 기능 추가` → Good: `<feat>(user): 프로필 이미지 업로드 추가`
- Bad: `<refactor>: 코드 정리` → Good: `<refactor>(api): UserService 책임 분리`

**Complex changes without body:**
- Always include What/Why sections when modifying multiple files
- Context explanation required unless it's a trivial typo fix

**Unrelated changes in one commit:**
- Do not mix feature additions with unrelated refactoring
- Each change should be in an independent commit

**Copying code diff:**
- Do not paste diff content verbatim
- Explain the "meaning" of the change
