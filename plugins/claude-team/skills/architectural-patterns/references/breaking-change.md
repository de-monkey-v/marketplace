# Breaking Change Analysis Framework

A systematic framework for analyzing, documenting, and mitigating breaking changes in software systems.

## Table of Contents

1. [Impact Classification](#impact-classification)
2. [Breaking Change Categories](#breaking-change-categories)
3. [Analysis Matrix](#analysis-matrix)
4. [Detection Methods](#detection-methods)
5. [Mitigation Strategies](#mitigation-strategies)
6. [Communication Plan](#communication-plan)

---

## Impact Classification

### Impact Levels

Use this classification to assess the severity of a breaking change.

| Level | Definition | Consumer Impact | Action Required |
|-------|-----------|----------------|-----------------|
| **Critical** | Breaks compilation or runtime for all or most consumers | Immediate breaking errors, app won't build/run | Mandatory migration, major version bump |
| **High** | Breaks specific use cases or common patterns | Errors for significant subset of users | Required migration, clear upgrade path |
| **Medium** | Requires consumer updates but provides migration path | Works with warnings, deprecated API still available | Optional migration with timeline |
| **Low** | No immediate consumer impact, future-facing change | No breaking errors, new preferred approach available | Awareness only, eventual migration |

### Impact Assessment Questions

Answer these to determine impact level:

1. **Will existing code fail to compile/run?**
   - Yes, all cases → Critical
   - Yes, some cases → High
   - No, but warnings → Medium
   - No impact → Low

2. **Is there a migration path?**
   - No automated migration → +1 severity level
   - Manual migration required → High or Critical
   - Automated migration available → Medium
   - Backward compatibility maintained → Low

3. **How many consumers affected?**
   - All consumers → Critical
   - >50% of consumers → High
   - 10-50% of consumers → Medium
   - <10% of consumers → Low

4. **Time to migrate?**
   - >1 week of work → Critical or High
   - 1-5 days → High or Medium
   - <1 day → Medium or Low
   - <1 hour → Low

### Impact Level Examples

#### Critical Examples

```typescript
// BEFORE: Public API
export function getUser(id: number): User {
  return db.users.find(id);
}

// AFTER: Function removed entirely
// ❌ NO REPLACEMENT - All consumers broken
```

```typescript
// BEFORE: Return type
export function getUser(id: number): User {
  return db.users.find(id);
}

// AFTER: Return type changed
export function getUser(id: number): Promise<User> {
  return db.users.find(id);
}
// ❌ All synchronous consumers broken
```

#### High Examples

```typescript
// BEFORE: Required parameter
export function createUser(email: string): User {
  return new User(email);
}

// AFTER: Additional required parameter
export function createUser(email: string, name: string): User {
  return new User(email, name);
}
// ❌ All call sites must add 'name' parameter
```

```typescript
// BEFORE: Default behavior
export function fetchData() {
  return fetch(url, { cache: 'force-cache' });
}

// AFTER: Default changed
export function fetchData() {
  return fetch(url, { cache: 'no-cache' });
}
// ❌ Performance implications for all consumers
```

#### Medium Examples

```typescript
// BEFORE: Deprecated API
export function getUserById(id: number): User {
  console.warn('getUserById is deprecated, use getUser instead');
  return getUser({ id });
}

export function getUser(params: { id: number }): User {
  return db.users.find(params.id);
}
// ⚠️ Old API still works, but deprecated
```

```typescript
// BEFORE: Optional parameter
export function createUser(email: string, name?: string): User {
  return new User(email, name || 'Anonymous');
}

// AFTER: Optional removed, renamed
export function createUser(params: { email: string; name: string }): User {
  return new User(params.email, params.name);
}
// ⚠️ Call signature changed but migration is straightforward
```

#### Low Examples

```typescript
// BEFORE: Internal implementation
function _validateEmail(email: string): boolean {
  return /\S+@\S+\.\S+/.test(email);
}

// AFTER: Implementation changed (not exported)
function _validateEmail(email: string): boolean {
  return validator.isEmail(email); // Different library
}
// ✅ No external impact
```

```typescript
// BEFORE: New optional parameter
export function createUser(email: string): User {
  return new User(email);
}

// AFTER: New optional parameter added
export function createUser(email: string, name?: string): User {
  return new User(email, name);
}
// ✅ Backward compatible, no breaking change
```

---

## Breaking Change Categories

### 1. API Contract Changes

**Definition:** Changes to public interfaces, function signatures, or REST endpoints.

#### Function Signature Changes

| Change Type | Impact | Example |
|------------|--------|---------|
| Remove function | Critical | `function foo()` deleted |
| Rename function | Critical | `getUserById` → `getUser` |
| Add required parameter | High | `fn(a)` → `fn(a, b)` |
| Remove parameter | High | `fn(a, b)` → `fn(a)` |
| Change parameter type | High | `fn(a: string)` → `fn(a: number)` |
| Change return type | High | `fn(): User` → `fn(): Promise<User>` |
| Reorder parameters | High | `fn(a, b)` → `fn(b, a)` |
| Add optional parameter | Low | `fn(a)` → `fn(a, b?)` |

#### REST API Changes

| Change Type | Impact | Example |
|------------|--------|---------|
| Remove endpoint | Critical | `DELETE /api/users` removed |
| Change HTTP method | Critical | `POST /users` → `PUT /users` |
| Change URL structure | Critical | `/users/:id` → `/v2/users/:id` |
| Remove request field | High | `{ name, email }` → `{ name }` |
| Change response shape | High | `{ user }` → `{ data: { user } }` |
| Add required field | High | `{ name }` → `{ name, email }` required |
| Change status codes | Medium | `200` → `204` for success |
| Add optional field | Low | `{ name }` → `{ name, age? }` |

#### Class/Interface Changes

| Change Type | Impact | Example |
|------------|--------|---------|
| Remove class/interface | Critical | `class User` deleted |
| Rename class/interface | Critical | `User` → `UserEntity` |
| Remove public property | High | Remove `user.email` |
| Change property type | High | `age: number` → `age: string` |
| Remove method | High | Remove `user.save()` |
| Make property required | High | `email?:` → `email:` |
| Add abstract method (to abstract class) | High | Implementers must add method |
| Add optional property | Low | Add `phone?: string` |

### 2. Data Model Changes

**Definition:** Changes to database schemas, serialization formats, or data structures.

#### Database Schema Changes

| Change Type | Impact | Example |
|------------|--------|---------|
| Remove table | Critical | `DROP TABLE users` |
| Remove column | High | `ALTER TABLE users DROP COLUMN email` |
| Change column type | High | `age VARCHAR` → `age INTEGER` |
| Add NOT NULL constraint | High | `ALTER TABLE users ALTER COLUMN email SET NOT NULL` |
| Remove foreign key | High | Break referential integrity |
| Change primary key | Critical | `id INTEGER` → `uuid VARCHAR` |
| Add nullable column | Low | `ALTER TABLE users ADD COLUMN phone VARCHAR` |
| Add default value | Low | `ADD COLUMN status VARCHAR DEFAULT 'active'` |

#### Serialization Changes

| Change Type | Impact | Example |
|------------|--------|---------|
| Change format | Critical | JSON → Protobuf |
| Remove field | High | Remove `user.email` from JSON |
| Rename field | High | `user_id` → `userId` |
| Change data type | High | `"123"` → `123` (string to number) |
| Nested structure change | High | `user.name` → `user.profile.name` |
| Add required field | Medium | Must provide on deserialization |
| Add optional field | Low | Can be omitted |

### 3. Behavior Changes

**Definition:** Changes to how existing APIs behave, including defaults, error handling, and side effects.

#### Default Value Changes

| Change Type | Impact | Example |
|------------|--------|---------|
| Change default parameter value | High | `timeout: 30s` → `timeout: 10s` |
| Change default return value | High | Return `null` → throw error |
| Change default config | High | Cache enabled → disabled |
| Remove default altogether | High | Required to specify explicitly |

#### Error Handling Changes

| Change Type | Impact | Example |
|------------|--------|---------|
| Throw new exception type | Medium | `Error` → `ValidationError` |
| Remove exception | High | No longer throws, returns null instead |
| Change error message format | Low | For logging/display only |
| Change when error is thrown | High | Validation timing changed |

#### Side Effect Changes

| Change Type | Impact | Example |
|------------|--------|---------|
| Add new side effect | Medium | `saveUser()` now sends email |
| Remove side effect | High | `deleteUser()` no longer cascades |
| Change order of operations | Medium | Validation before vs. after save |
| Async vs. sync | Critical | Synchronous → asynchronous |

### 4. Configuration Changes

**Definition:** Changes to environment variables, config files, or deployment requirements.

| Change Type | Impact | Example |
|------------|--------|---------|
| Remove config key | High | `DATABASE_URL` no longer supported |
| Rename config key | High | `DB_HOST` → `DATABASE_HOST` |
| Change config format | High | `.env` → `config.yaml` |
| Change default config value | Medium | `LOG_LEVEL=info` → `LOG_LEVEL=warn` |
| Add required config | High | Must set `API_KEY` or app won't start |
| Add optional config | Low | New feature flag |

### 5. Dependency Changes

**Definition:** Changes to third-party dependencies or minimum version requirements.

| Change Type | Impact | Example |
|------------|--------|---------|
| Remove dependency | High | Remove lodash, use native methods |
| Upgrade major version | High | React 17 → 18 (new APIs) |
| Change dependency (swap) | High | moment → date-fns |
| Increase minimum version | Medium | Node 14+ → Node 18+ |
| Add new dependency | Low | Add new optional feature |
| Update patch version | Low | Bug fix only |

---

## Analysis Matrix

Use this template to systematically document breaking changes.

### Template

| Change | Category | Impact Level | Affected Consumers | Affected Count | Detection Method | Migration Strategy | Timeline |
|--------|----------|--------------|-------------------|----------------|------------------|-------------------|----------|
| {description} | {API/Data/Behavior/Config/Deps} | {Critical/High/Medium/Low} | {who is affected} | {number or %} | {how to detect} | {how to migrate} | {when} |

### Example: Completed Matrix

| Change | Category | Impact Level | Affected Consumers | Affected Count | Detection Method | Migration Strategy | Timeline |
|--------|----------|--------------|-------------------|----------------|------------------|-------------------|----------|
| Remove `getUserById()` function | API Contract | Critical | All API consumers | 47 call sites | `grep -r "getUserById"` | Replace with `getUser({ id })` | v3.0.0 (2026-04-01) |
| Change `User.email` to required | Data Model | High | User creation flows | 12 components | TypeScript compiler | Add email validation to forms | v3.0.0 (2026-04-01) |
| Default cache disabled | Behavior | Medium | Performance-sensitive features | 5 modules | Runtime monitoring | Explicitly set `cache: true` | v2.5.0 (2026-03-01) |
| Rename `DB_HOST` → `DATABASE_HOST` | Config | Medium | All deployments | 8 environments | Deployment check | Update env vars in CI/CD | v2.5.0 (2026-03-01) |
| Upgrade React 17 → 18 | Dependency | High | All frontend code | Entire app | `npm ls react` | Update to `createRoot`, Suspense | v3.0.0 (2026-04-01) |
| Add optional `phone` field | API Contract | Low | None (backward compat) | 0 | N/A | Optional usage | v2.4.0 (2026-02-15) |

---

## Detection Methods

### Automated Detection

#### 1. TypeScript Compiler

**What it detects:**
- Function signature changes
- Type changes
- Removed exports
- Required vs. optional parameter changes

**Commands:**
```bash
# Compile with strict mode
tsc --noEmit --strict

# Check specific file
tsc --noEmit src/api/users.ts

# Generate declaration files to see public API
tsc --declaration --emitDeclarationOnly
```

#### 2. API Diff Tools

**API Extractor (TypeScript):**
```bash
# Install
npm install -g @microsoft/api-extractor

# Generate API report
api-extractor run

# Compare with previous version
diff api-report.md api-report-previous.md
```

**OpenAPI Diff (REST APIs):**
```bash
# Install
npm install -g oasdiff

# Compare OpenAPI specs
oasdiff spec1.yaml spec2.yaml --breaking-only
```

#### 3. Database Migration Analysis

**Detect breaking schema changes:**
```bash
# Check migration SQL for dangerous keywords
grep -E "DROP|ALTER.*DROP|ALTER.*NOT NULL" migrations/*.sql

# Use schema comparison tools
npm install -g dbdiff
dbdiff old-schema.sql new-schema.sql
```

#### 4. Dependency Version Checks

**Detect major version bumps:**
```bash
# Check for breaking dependency changes
npm outdated --long

# Show major version changes
npm-check-updates --target major

# Compare package.json
diff package.json package-previous.json | grep version
```

#### 5. Consumer Usage Analysis

**Find all usage sites:**
```bash
# Find all references to function
grep -r "getUserById" --include="*.ts" --include="*.tsx" .

# Count occurrences
grep -r "getUserById" --include="*.ts" | wc -l

# Find imports
grep -r "import.*getUserById" --include="*.ts"
```

**TypeScript Language Server (LSP):**
```typescript
// Use IDE "Find All References" feature
// Or use Language Server Protocol programmatically

import ts from 'typescript';

function findAllReferences(fileName: string, position: number) {
  // Use TypeScript Language Service API
}
```

#### 6. Runtime Monitoring

**Detect behavior changes:**
```bash
# Compare production metrics before/after
# - Response times
# - Error rates
# - Cache hit rates
# - Database query counts

# Use feature flags to A/B test behavior changes
```

### Detection Checklist

Before releasing, check:

- [ ] Run TypeScript compiler with `--strict`
- [ ] Generate and compare API reports
- [ ] Run database migration scripts in staging
- [ ] Check for removed/renamed functions (grep)
- [ ] Verify dependency major version bumps
- [ ] Test with real consumer applications
- [ ] Review test failures in consumer projects
- [ ] Check CI/CD pipelines for failures
- [ ] Monitor production error logs (canary deployment)

---

## Mitigation Strategies

### Strategy 1: Versioning

#### Semantic Versioning (SemVer)

Follow semver for all releases:

```
MAJOR.MINOR.PATCH

MAJOR: Breaking changes (1.0.0 → 2.0.0)
MINOR: New features, backward compatible (1.0.0 → 1.1.0)
PATCH: Bug fixes, backward compatible (1.0.0 → 1.0.1)
```

**Breaking Change Rules:**
- All breaking changes → MAJOR version bump
- Provide migration guide for each MAJOR release
- Support N-1 version for critical bugs

#### API Versioning Strategies

**Option A: URL Versioning (REST)**
```
/v1/users  (old)
/v2/users  (new, breaking)

Pros: Clear, easy to route
Cons: URL proliferation
```

**Option B: Header Versioning**
```http
GET /users
Accept: application/vnd.api+json; version=2

Pros: Clean URLs
Cons: Less visible, harder to test
```

**Option C: Query Parameter**
```
GET /users?api_version=2

Pros: Easy to change
Cons: Pollutes query params
```

**Recommendation:** URL versioning for major versions, header for minor tweaks.

### Strategy 2: Deprecation Workflow

**Phase-based deprecation:**

#### Phase 1: Announce (v2.5.0)
```typescript
/**
 * @deprecated Use getUser({ id }) instead. Will be removed in v3.0.0
 */
export function getUserById(id: number): User {
  console.warn('getUserById is deprecated, use getUser({ id })');
  return getUser({ id });
}

export function getUser(params: { id: number }): User {
  return db.users.find(params.id);
}
```

**Timeline:** 3-6 months notice

#### Phase 2: Warn (v2.8.0)
```typescript
export function getUserById(id: number): User {
  if (process.env.NODE_ENV !== 'production') {
    throw new Error('getUserById is deprecated and will be removed in v3.0.0');
  }
  console.error('getUserById is deprecated, use getUser({ id })');
  return getUser({ id });
}
```

**Timeline:** 1-2 months before removal

#### Phase 3: Remove (v3.0.0)
```typescript
// getUserById completely removed
// Only getUser exists
export function getUser(params: { id: number }): User {
  return db.users.find(params.id);
}
```

**Checklist:**
- [ ] Add `@deprecated` JSDoc tag
- [ ] Add runtime warning (console.warn)
- [ ] Update documentation
- [ ] Add to CHANGELOG.md
- [ ] Notify consumers (email, Slack, etc.)
- [ ] Provide migration guide
- [ ] Set removal date (6+ months out)

### Strategy 3: Feature Flags

**Gradual rollout of breaking changes:**

```typescript
import { featureFlag } from './feature-flags';

export function fetchData() {
  if (featureFlag('new-cache-behavior')) {
    // New behavior (breaking)
    return fetch(url, { cache: 'no-cache' });
  } else {
    // Old behavior
    return fetch(url, { cache: 'force-cache' });
  }
}
```

**Benefits:**
- Test in production with subset of users
- Quick rollback if issues
- Gradual migration

**Rollout plan:**
1. 5% of users (canary)
2. 25% of users (early adopters)
3. 50% of users
4. 100% of users
5. Remove old code path

### Strategy 4: Backward Compatibility Layers

**Adapter pattern to maintain old API:**

```typescript
// New API (preferred)
export function getUser(params: { id: number }): Promise<User> {
  return db.users.find(params.id);
}

// Old API (deprecated, wraps new API)
export function getUserById(id: number): Promise<User> {
  console.warn('getUserById is deprecated');
  return getUser({ id });
}
```

**Shim for behavior change:**
```typescript
export function createUser(
  emailOrParams: string | { email: string; name: string },
  name?: string
): User {
  // Support both old and new signatures
  if (typeof emailOrParams === 'string') {
    // Old signature: createUser(email, name)
    console.warn('createUser(email, name) is deprecated');
    return _createUserNew({ email: emailOrParams, name: name || 'Anonymous' });
  } else {
    // New signature: createUser({ email, name })
    return _createUserNew(emailOrParams);
  }
}

function _createUserNew(params: { email: string; name: string }): User {
  return new User(params.email, params.name);
}
```

### Strategy 5: Automated Migration Tools

**Provide codemods for consumers:**

```javascript
// codemod-getuserbyid-to-getuser.js
module.exports = function transformer(file, api) {
  const j = api.jscodeshift;
  const root = j(file.source);

  // Find: getUserById(123)
  // Replace: getUser({ id: 123 })
  root
    .find(j.CallExpression, {
      callee: { name: 'getUserById' }
    })
    .replaceWith(path => {
      const arg = path.node.arguments[0];
      return j.callExpression(
        j.identifier('getUser'),
        [j.objectExpression([
          j.property('init', j.identifier('id'), arg)
        ])]
      );
    });

  return root.toSource();
};
```

**Usage:**
```bash
npx jscodeshift -t codemod-getuserbyid-to-getuser.js src/**/*.ts
```

**Provide for common breaking changes:**
- Function signature changes
- Renamed imports
- Moved modules

---

## Communication Plan

### Internal Communication (Team)

**Before Change:**
- [ ] Document in RFC (Request for Comments)
- [ ] Discuss in architecture review
- [ ] Get stakeholder buy-in
- [ ] Plan migration timeline

**During Development:**
- [ ] Update CHANGELOG.md with `[BREAKING]` tag
- [ ] Add migration guide to docs
- [ ] Write tests for migration path
- [ ] Create deprecation warnings

**Before Release:**
- [ ] Review with tech leads
- [ ] Prepare rollback plan
- [ ] Test in staging environment
- [ ] Validate migration guide

### External Communication (Consumers)

#### 1. Changelog Entry

```markdown
## [3.0.0] - 2026-04-01

### BREAKING CHANGES

#### Removed `getUserById()` function

**Why:** Inconsistent with rest of API. All other methods use object parameters.

**Migration:**

```typescript
// Before
const user = await getUserById(123);

// After
const user = await getUser({ id: 123 });
```

**Automated Migration:** Run `npx @ourlib/codemod-v3` to automatically migrate.

**Timeline:**
- v2.5.0 (2026-01-01): `getUserById` deprecated with warnings
- v2.8.0 (2026-03-01): Warnings become errors in dev mode
- v3.0.0 (2026-04-01): `getUserById` removed

**Help:** See [Migration Guide](./docs/migration-v2-to-v3.md) for details.
```

#### 2. Migration Guide Document

**Structure:**

```markdown
# Migration Guide: v2 → v3

## Overview
Version 3.0 includes breaking changes to improve API consistency.

**Estimated migration time:** 1-4 hours depending on usage

## Breaking Changes Summary

| Change | Impact | Effort |
|--------|--------|--------|
| Remove `getUserById()` | High | 5 min (automated) |
| `User.email` required | Medium | 30 min |
| Default cache disabled | Low | 10 min |

## Detailed Changes

### 1. getUserById() Removed

**Affected:** All code calling `getUserById()`

**Detection:**
```bash
grep -r "getUserById" src/
```

**Migration:**
```typescript
// Before
const user = await getUserById(123);

// After
const user = await getUser({ id: 123 });
```

**Automated:** Run `npx @ourlib/codemod-v3 src/`

### 2. User.email Required

**Affected:** User creation, registration forms

**Detection:** TypeScript compiler will error on missing email

**Migration:**
```typescript
// Before (optional)
const user = new User({ name: 'John' });

// After (required)
const user = new User({ name: 'John', email: 'john@example.com' });
```

**Validation:** Add email input to all user creation forms

## Step-by-Step Migration

1. **Install v2.9.0 (last v2 version)**
   ```bash
   npm install @ourlib/api@2.9.0
   ```

2. **Run deprecation checker**
   ```bash
   npm run check-deprecations
   ```

3. **Run automated codemod**
   ```bash
   npx @ourlib/codemod-v3 src/
   ```

4. **Fix TypeScript errors**
   ```bash
   tsc --noEmit
   ```

5. **Update tests**
   ```bash
   npm test
   ```

6. **Upgrade to v3.0.0**
   ```bash
   npm install @ourlib/api@3.0.0
   ```

7. **Verify in staging**

8. **Deploy to production**

## Rollback Plan

If issues arise:

```bash
npm install @ourlib/api@2.9.0
git revert {commit-hash}
npm test
deploy
```

## Support

- **Questions:** Open issue on GitHub
- **Bugs:** Email support@ourlib.com
- **Slack:** #api-v3-migration
```

#### 3. Notification Channels

**Timeline-based notifications:**

| When | Channel | Content |
|------|---------|---------|
| 6 months before | Blog post, Twitter | "v3.0 coming in April 2026, breaking changes overview" |
| 3 months before | Email to all users | "Start planning migration, deprecation warnings added" |
| 1 month before | Email, Slack, GitHub discussion | "v3.0 release date confirmed, migration guide ready" |
| 1 week before | Email, banner on docs site | "v3.0 releases next week, last chance to prepare" |
| Release day | All channels | "v3.0 released! Migration guide: [link]" |
| 1 week after | Email | "How's your migration going? Need help?" |

#### 4. Support Resources

**Provide:**
- [ ] Migration guide document
- [ ] Automated codemod tool
- [ ] Video tutorial (for complex changes)
- [ ] FAQ page
- [ ] Dedicated Slack channel for questions
- [ ] Office hours (live Q&A sessions)
- [ ] Migration examples repository

---

## Breaking Change Checklist

Use this comprehensive checklist before releasing breaking changes:

### Planning Phase
- [ ] Document change in RFC
- [ ] Assess impact level (Critical/High/Medium/Low)
- [ ] Identify all affected consumers
- [ ] Estimate migration effort
- [ ] Get stakeholder approval
- [ ] Set release timeline (6+ months for critical changes)

### Development Phase
- [ ] Implement new API/behavior
- [ ] Add deprecation warnings to old API
- [ ] Write migration guide
- [ ] Create automated migration tool (codemod)
- [ ] Update TypeScript types
- [ ] Add tests for both old and new behavior
- [ ] Update documentation

### Pre-Release Phase
- [ ] Test migration in sample consumer project
- [ ] Run automated detection tools
- [ ] Verify rollback plan works
- [ ] Prepare communication materials
- [ ] Schedule announcement dates

### Communication Phase
- [ ] Announce 6 months ahead (blog, email)
- [ ] Release deprecation version (warnings)
- [ ] Remind 3 months ahead
- [ ] Remind 1 month ahead
- [ ] Remind 1 week ahead
- [ ] Publish migration guide

### Release Phase
- [ ] Release breaking change version
- [ ] Monitor error rates/metrics
- [ ] Respond to support requests quickly
- [ ] Publish post-mortem if issues arise

### Post-Release Phase
- [ ] Check in with major consumers
- [ ] Collect feedback on migration experience
- [ ] Update migration guide based on common questions
- [ ] Document lessons learned

---

## Appendix: Common Patterns

### Pattern 1: Soft Delete Before Hard Delete

```typescript
// v2.5.0: Mark as deprecated
/** @deprecated Use getUser instead */
export function getUserById(id: number): User {
  return getUser({ id });
}

// v2.8.0: Add warning
export function getUserById(id: number): User {
  console.warn('getUserById will be removed in v3.0.0');
  return getUser({ id });
}

// v3.0.0: Remove
// (function deleted entirely)
```

### Pattern 2: Options Object Evolution

```typescript
// v1: Positional params
function createUser(email: string, name: string, age: number) {}

// v2: Options object (BREAKING, but worth it)
function createUser(options: { email: string; name: string; age: number }) {}

// v2.1: Add optional field (non-breaking)
function createUser(options: {
  email: string;
  name: string;
  age: number;
  phone?: string;  // New optional
}) {}
```

### Pattern 3: Dual-Mode API

```typescript
// Support both old and new during transition
export function createUser(
  paramsOrEmail: { email: string; name: string } | string,
  name?: string
): User {
  let params: { email: string; name: string };

  if (typeof paramsOrEmail === 'string') {
    // Old signature
    console.warn('Positional params deprecated');
    params = { email: paramsOrEmail, name: name! };
  } else {
    // New signature
    params = paramsOrEmail;
  }

  return _createUser(params);
}
```

---

**Last Updated:** 2026-02-20
**Version:** 1.0.0
