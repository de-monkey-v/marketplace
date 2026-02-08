# Commit Message Format Reference

Commit message format rules. **Default is the detailed format.**

---

## Required Rules

**Commit message language follows `.hyper-team/metadata.json`:**
- Resolve language via: `$ARGUMENTS` flag → `.hyper-team/metadata.json` → default `eng`
- Write subject, What, Why sections in the resolved language
- Code paths, issue numbers, and technical terms remain as-is

**Signatures are NEVER allowed:**
- `generated with [Claude Code]` — forbidden
- `Co-Authored-By: Claude` — forbidden
- `🤖` emoji — forbidden

---

## Detailed Format (Default)

Full Conventional Commits with structured body sections:

```
<type>(scope): concise subject (max 50 chars)

## What
Describe the specific changes made.

- `path/to/file.ts`: change summary
- Added classes/functions/methods
- Modified core logic
- Removed elements

## Why
Explain the motivation and how it differs from previous behavior.

- Background: context that led to the change
- Problem: specific issue being resolved
- Effect: expected improvements after the change

## Impact — if applicable
- Affected features/modules
- Dependency changes (added/removed/updated)
- Performance impact

## Notes — if applicable
- Test scenarios to verify
- Caveats
- Related documentation links

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
<type>: concise subject (max 50 chars)

1. Primary change
2. Secondary change
3. Additional details (if needed)
```

Use `--simple` or `-s` flag when:
- Quick, small changes
- Self-explanatory fixes
- Personal/local commits

---

## Subject Rules (Common)

| Rule | Correct Example | Wrong Example |
|------|----------------|---------------|
| Max 50 chars | `<feat>: add user auth` | `<feat>: add user authentication with JWT tokens and session management plus security hardening` |
| Imperative mood | `add feature` | `added feature` |
| No trailing period | `<fix>: resolve error` | `<fix>: resolve error.` |
| Resolved language | `<feat>: add login` (eng) / `<feat>: 로그인 추가` (kor) | Mismatch with resolved language |

---

## Complete Examples

### Detailed: Feature Addition

```
<feat>(auth): add OAuth2 social login

## What
- `src/auth/OAuthService.ts`: implement Google, Kakao OAuth2 client
- `src/auth/JwtTokenProvider.ts`: add token generation/verification logic
- `src/api/AuthController.ts`: add /login, /callback endpoints
- New OAuthService class created
- JwtTokenProvider.generateToken() method added

## Why
- Background: continuous user requests for social login
- Problem: 40% signup abandonment rate with email/password
- Effect: 20% improvement in signup conversion, reduced password security burden

## Impact
- Affects entire auth module
- New dependencies: passport-oauth2, jsonwebtoken
- Runs alongside existing session-based authentication

Fixes: #42
Related: #38
```

### Detailed: Bug Fix

```
<fix>(api): resolve session collision on concurrent requests

## What
- `src/middleware/session.ts`: add session lock mechanism
- `src/utils/mutex.ts`: create Redis-based distributed lock utility
- `src/config/redis.ts`: add Redis client configuration

## Why
- Background: intermittent session data loss reports in production
- Problem: race condition on concurrent requests from same user
- Effect: session data integrity guaranteed, error rate 0.5% → 0.01%

## Impact
- Affects all authenticated API endpoints
- New dependency: ioredis
- Average response time increase of 5ms (lock acquisition wait)

## Notes
- Redis must be running for local testing
- Existing sessions are auto-migrated

Fixes: #156
```

### Detailed: Refactoring

```
<refactor>(user): separate UserService class responsibilities

## What
- `src/services/UserService.ts`: retain core user CRUD only
- `src/services/UserAuthService.ts`: extract auth logic (new)
- `src/services/UserNotificationService.ts`: extract notification logic (new)
- UserService reduced from 600 lines → 150 lines

## Why
- Background: UserService grew to 20+ methods
- Problem: single responsibility principle violation, difficult to test
- Effect: clear responsibility per class, improved unit test coverage

## Impact
- Import path changes for all controllers using UserService
- Existing API behavior unchanged (interface preserved)

Related: #89
```

### Simple: Minor Fix

```
<fix>: resolve null pointer in UserService

1. Add null check before accessing user.email
2. Return empty Optional instead of null
```

### Simple: Documentation Update

```
<docs>: update API documentation

1. Add authentication endpoint examples
2. Document error response format
3. Include rate limiting information
```

---

## Prohibited

**Never include:**

```
# Wrong: auto-generated signature included
<feat>: add feature

## What
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
- [ ] **Written in the resolved language**
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
- Bad: `<fix>: fix bug` → Good: `<fix>(auth): fix session expiration error on login`
- Bad: `<feat>: add feature` → Good: `<feat>(user): add profile image upload`
- Bad: `<refactor>: clean up code` → Good: `<refactor>(api): separate UserService responsibilities`

**Complex changes without body:**
- Always include What/Why sections when modifying multiple files
- Context explanation required unless it's a trivial typo fix

**Unrelated changes in one commit:**
- Do not mix feature additions with unrelated refactoring
- Each change should be in an independent commit

**Copying code diff:**
- Do not paste diff content verbatim
- Explain the "meaning" of the change
