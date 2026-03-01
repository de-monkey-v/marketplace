# Commit Types Reference

Complete list of commit types following CONTRIBUTING.md conventions.

## Type List

| Type | When to Use | Example |
|------|-------------|---------|
| `<feat>` | New feature | `<feat>: OAuth2 로그인 추가` |
| `<fix>` | Bug fix | `<fix>: UserService null 처리 수정` |
| `<refactor>` | Code restructure (no behavior change) | `<refactor>: 검증 로직 분리` |
| `<test>` | Add/modify tests | `<test>: AuthService 단위 테스트 추가` |
| `<docs>` | Documentation only | `<docs>: API 문서 업데이트` |
| `<style>` | Formatting (no logic change) | `<style>: config 들여쓰기 정리` |
| `<perf>` | Performance improvement | `<perf>: 데이터베이스 조회 최적화` |
| `<build>` | Build config changes | `<build>: Gradle 의존성 업데이트` |
| `<ci>` | CI configuration | `<ci>: GitHub Actions 워크플로 추가` |
| `<chore>` | Miscellaneous tasks | `<chore>: .gitignore 업데이트` |
| `<revert>` | Revert previous commit | `<revert>: "OAuth2 로그인 추가" 되돌리기` |

## Type Selection Guide

### Feature vs Fix vs Refactor

- **feat**: Completely new functionality that didn't exist before
- **fix**: Correcting incorrect behavior (bug)
- **refactor**: Improving code structure without changing behavior

### When to Use Each

**Use `<feat>` when:**
- Adding new API endpoint
- Implementing new UI component
- Adding new business logic

**Use `<fix>` when:**
- Correcting error handling
- Fixing validation logic
- Resolving unexpected behavior

**Use `<refactor>` when:**
- Extracting methods/classes
- Renaming for clarity
- Simplifying complex code

**Use `<docs>` when:**
- README changes
- API documentation
- Code comments (only)

**Use `<style>` when:**
- Formatting changes
- Whitespace adjustments
- No code logic changes

**Use `<chore>` when:**
- Updating dependencies
- Modifying .gitignore
- Administrative tasks

## Common Mistakes

### Wrong Type Selection

```
# Wrong: Using feat for bug fix
<feat>: Fix login error

# Correct
<fix>: Fix login error
```

### Missing Angle Brackets

```
# Wrong: No angle brackets
feat: Add new feature

# Correct
<feat>: Add new feature
```

### Wrong Type Name

```
# Wrong: Invalid type
<feature>: Add OAuth

# Correct
<feat>: Add OAuth
```
