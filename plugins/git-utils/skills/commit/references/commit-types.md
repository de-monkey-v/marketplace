# Commit Types Reference

Complete list of commit types following CONTRIBUTING.md conventions.

## Type List

| Type | When to Use | Example |
|------|-------------|---------|
| `<feat>` | New feature | `<feat>: Add OAuth2 login` |
| `<fix>` | Bug fix | `<fix>: Resolve null pointer in UserService` |
| `<refactor>` | Code restructure (no behavior change) | `<refactor>: Extract validation logic` |
| `<test>` | Add/modify tests | `<test>: Add unit tests for AuthService` |
| `<docs>` | Documentation only | `<docs>: Update API documentation` |
| `<style>` | Formatting (no logic change) | `<style>: Fix indentation in config` |
| `<perf>` | Performance improvement | `<perf>: Optimize database queries` |
| `<build>` | Build config changes | `<build>: Update Gradle dependencies` |
| `<ci>` | CI configuration | `<ci>: Add GitHub Actions workflow` |
| `<chore>` | Miscellaneous tasks | `<chore>: Update .gitignore` |
| `<revert>` | Revert previous commit | `<revert>: Revert "Add OAuth2 login"` |

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
