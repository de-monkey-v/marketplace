# Codebase Analysis Checklist

A systematic framework for analyzing unfamiliar codebases, identifying architectural patterns, and understanding technical conventions.

## Overview

This checklist guides you through 5 analysis phases, from basic structure to detailed tech stack assessment. Execute phases sequentially for comprehensive understanding.

**Estimated Time:** 30-60 minutes for typical project
**Prerequisites:** Read access to codebase, terminal access
**Output Format:** Structured markdown report with findings

---

## Phase 1: Project Structure Analysis

### 1.1 Directory Layout Mapping

**Objective:** Build mental map of project organization

**Commands:**
```bash
# High-level structure (depth 2)
tree -L 2 -d .

# Alternative for large repos
find . -maxdepth 2 -type d | grep -v node_modules | grep -v .git

# Count files by directory
find . -type f | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head -20
```

**Checklist:**
- [ ] Identify source code directory (`src/`, `lib/`, `app/`)
- [ ] Locate test directory (`tests/`, `__tests__`, `spec/`)
- [ ] Find configuration directory (`config/`, `cfg/`)
- [ ] Locate build output (`dist/`, `build/`, `out/`)
- [ ] Identify static assets (`public/`, `static/`, `assets/`)
- [ ] Find documentation (`docs/`, `documentation/`)
- [ ] Check for scripts directory (`scripts/`, `bin/`)
- [ ] Locate infrastructure code (`infra/`, `terraform/`, `k8s/`)

**Pattern Indicators:**

| Directory Structure | Likely Pattern |
|-------------------|---------------|
| `src/{domain,application,infrastructure,presentation}` | Clean Architecture |
| `src/modules/{module-name}/{domain,app,infra}` | Modular Monolith |
| `src/features/{feature}/{Command,Query,Handler}` | Vertical Slice (VSA) |
| `src/{models,views,controllers}` | MVC |
| `src/{domain,ports,adapters}` | Hexagonal |
| `packages/{package-name}` | Monorepo |
| `services/{service-name}` | Microservices |

### 1.2 Configuration Files Inventory

**Objective:** Understand project setup and tooling

**Commands:**
```bash
# List all config files in root
ls -la | grep -E "\.(json|yaml|yml|toml|ini|env|config)$|rc$"

# Find all config-related files
find . -maxdepth 2 -type f \( -name "*.config.*" -o -name ".*rc" -o -name "*.json" \) | grep -v node_modules
```

**Checklist:**

**Package Management:**
- [ ] `package.json` (Node.js) - Check scripts, dependencies
- [ ] `requirements.txt` / `pyproject.toml` (Python)
- [ ] `Gemfile` (Ruby)
- [ ] `pom.xml` / `build.gradle` (Java)
- [ ] `Cargo.toml` (Rust)
- [ ] `go.mod` (Go)

**Build & Bundling:**
- [ ] `tsconfig.json` (TypeScript)
- [ ] `webpack.config.js` / `vite.config.js` / `rollup.config.js`
- [ ] `babel.config.js` / `.babelrc`
- [ ] `esbuild.config.js`

**Code Quality:**
- [ ] `.eslintrc.*` / `eslint.config.js`
- [ ] `.prettierrc` / `prettier.config.js`
- [ ] `.editorconfig`
- [ ] `sonar-project.properties`

**Testing:**
- [ ] `jest.config.js` / `vitest.config.js`
- [ ] `playwright.config.js` / `cypress.config.js`
- [ ] `.nycrc` / `coverage/`

**CI/CD:**
- [ ] `.github/workflows/*.yml` (GitHub Actions)
- [ ] `.gitlab-ci.yml` (GitLab CI)
- [ ] `Jenkinsfile` (Jenkins)
- [ ] `.circleci/config.yml` (CircleCI)

**Containerization:**
- [ ] `Dockerfile` / `docker-compose.yml`
- [ ] `.dockerignore`
- [ ] `kubernetes/*.yaml`

**Environment:**
- [ ] `.env.example` / `.env.sample`
- [ ] `config/default.json` / `config/production.json`

### 1.3 Entry Points Identification

**Objective:** Find where code execution begins

**Commands:**
```bash
# Find main entry points by file name
find . -name "main.*" -o -name "index.*" -o -name "app.*" | grep -v node_modules | grep -v dist

# Check package.json main field
jq -r '.main, .module, .exports' package.json 2>/dev/null

# Find files with main function (Python)
grep -r "if __name__ == .__main__" --include="*.py" | head -5

# Find files with main function (Go)
grep -r "func main()" --include="*.go"
```

**Checklist:**
- [ ] Identify primary entry point (e.g., `src/index.ts`)
- [ ] Find server/app initialization (e.g., `src/server.ts`, `src/app.ts`)
- [ ] Locate CLI entry points (e.g., `bin/cli.js`)
- [ ] Check for multiple entry points (multi-page apps, worker processes)
- [ ] Identify framework-specific entries (Next.js pages, Express app)

### 1.4 Build System Analysis

**Objective:** Understand compilation and deployment process

**Commands:**
```bash
# Extract build scripts from package.json
jq -r '.scripts | to_entries[] | select(.key | contains("build") or contains("compile")) | "\(.key): \(.value)"' package.json

# Check for build tools
which tsc webpack vite rollup esbuild 2>/dev/null

# Find build configuration
find . -maxdepth 2 -name "*build*" -o -name "*bundle*" | grep -v node_modules
```

**Checklist:**
- [ ] Identify build command (`npm run build`, `make build`)
- [ ] Check for TypeScript compilation (`tsc`)
- [ ] Identify bundler (Webpack, Vite, Rollup, esbuild)
- [ ] Locate build output directory
- [ ] Check for multi-stage builds (dev/prod)
- [ ] Find pre/post-build scripts
- [ ] Identify asset processing (CSS, images)

---

## Phase 2: Architecture Pattern Identification

### 2.1 Pattern Detection Decision Matrix

Use this matrix to systematically identify the architectural pattern.

**Step 1: Check Directory Structure**

| Pattern | Directory Structure | Score |
|---------|-------------------|-------|
| **Clean Architecture** | `src/{domain,application,infrastructure,presentation}` or `src/{entities,usecases,interfaces,frameworks}` | 🎯 High confidence |
| **DDD (Domain-Driven Design)** | `src/{contexts,modules,bounded-contexts}/{context-name}/{domain,app,infra}` + aggregates, entities, value objects | 🎯 High confidence |
| **VSA (Vertical Slice)** | `src/features/{feature-name}/{Command,Query,Handler,Validator}` | 🎯 High confidence |
| **Hexagonal (Ports & Adapters)** | `src/{domain,ports,adapters}` or `src/{core,ports,adapters}` | 🎯 High confidence |
| **Modular Monolith** | `src/modules/{module-name}` where each module has internal layers | 🔶 Medium confidence |
| **MVC** | `src/{models,views,controllers}` | 🎯 High confidence |
| **Layered (N-Tier)** | `src/{presentation,business,data}` or `src/{api,service,repository}` | 🔶 Medium confidence |
| **Microservices** | `services/{service-name}` or multiple repositories | 🎯 High confidence |

**Commands:**
```bash
# Check for Clean Architecture
find src -type d -name "domain" -o -name "application" -o -name "infrastructure" | head -5

# Check for DDD
find src -type d -name "*context*" -o -name "aggregates" -o -name "entities" | head -5

# Check for VSA
find src -type d -name "features" | xargs ls -la 2>/dev/null

# Check for Hexagonal
find src -type d -name "ports" -o -name "adapters" | head -5

# Check for MVC
ls src/ | grep -E "^(models|views|controllers)$"
```

**Step 2: Check Import Patterns**

```bash
# Check for layered dependencies (should only go inward)
# Example: infrastructure should import domain, not vice versa
grep -r "from.*domain" src/infrastructure --include="*.ts" | wc -l
grep -r "from.*infrastructure" src/domain --include="*.ts" | wc -l
# Second number should be 0 for Clean/Hexagonal

# Check for feature isolation (VSA)
# Features should not import from each other
grep -r "from.*features/.*" src/features --include="*.ts" | grep -v "shared" | head -10
```

**Step 3: Check Class/File Naming**

```bash
# DDD indicators
find . -name "*Aggregate.ts" -o -name "*Entity.ts" -o -name "*ValueObject.ts" | head -5

# VSA indicators
find . -name "*Command.ts" -o -name "*Query.ts" -o -name "*Handler.ts" | head -5

# Clean Architecture indicators
find . -name "*UseCase.ts" -o -name "*Interactor.ts" | head -5

# Hexagonal indicators
find . -name "*Port.ts" -o -name "*Adapter.ts" | head -5
```

### 2.2 Pattern Characteristics Checklist

Once you've identified a candidate pattern, verify with these characteristics:

#### Clean Architecture

- [ ] Dependencies point inward (domain has no external deps)
- [ ] Entities/domain models in core
- [ ] Use cases/interactors in application layer
- [ ] Controllers/presenters in presentation layer
- [ ] Frameworks/external libs in infrastructure/frameworks layer
- [ ] Dependency Inversion: interfaces in inner layers, implementations in outer

**Verification Command:**
```bash
# Domain layer should have minimal imports
head -20 src/domain/**/*.ts | grep "^import"
```

#### Domain-Driven Design (DDD)

- [ ] Bounded contexts clearly separated
- [ ] Aggregates identified (aggregate roots)
- [ ] Entities have identity
- [ ] Value objects are immutable
- [ ] Domain events present
- [ ] Repositories abstract persistence
- [ ] Application services orchestrate use cases

**Verification Command:**
```bash
# Find domain events
find . -name "*Event.ts" -o -name "*DomainEvent.ts" | head -10

# Find aggregates
grep -r "class.*Aggregate" --include="*.ts" | head -5
```

#### Vertical Slice Architecture (VSA)

- [ ] Features organized by use case, not technical layer
- [ ] Each feature has its own handlers, models, validators
- [ ] Minimal coupling between features
- [ ] Shared code in separate shared/common folder
- [ ] Often uses CQRS (Commands/Queries)

**Verification Command:**
```bash
# Check feature structure
ls -la src/features/*/

# Each should contain Handler, Command/Query
find src/features -name "*Handler.ts" | wc -l
find src/features -name "*Command.ts" -o -name "*Query.ts" | wc -l
```

#### Hexagonal Architecture

- [ ] Core domain has no dependencies on external frameworks
- [ ] Ports define interfaces for external interactions
- [ ] Adapters implement ports for specific technologies
- [ ] Primary/driving adapters (controllers, CLI)
- [ ] Secondary/driven adapters (repositories, APIs)

**Verification Command:**
```bash
# Ports should be interfaces/abstracts
grep -r "interface.*Port" src/ports --include="*.ts"

# Adapters should implement ports
grep -r "implements.*Port" src/adapters --include="*.ts"
```

### 2.3 Anti-Pattern Detection

**Checklist:**
- [ ] Circular dependencies between modules
- [ ] God objects (files >1000 lines)
- [ ] Anemic domain model (data classes with no behavior)
- [ ] Infrastructure leaking into domain
- [ ] Lack of abstraction boundaries

**Commands:**
```bash
# Find large files (potential god objects)
find src -name "*.ts" -exec wc -l {} \; | sort -rn | head -10

# Find circular imports (requires madge or similar)
npx madge --circular src/

# Find infrastructure imports in domain
grep -r "import.*express\|import.*typeorm\|import.*prisma" src/domain --include="*.ts"
```

---

## Phase 3: Dependency Analysis

### 3.1 Import Graph Analysis

**Objective:** Understand module relationships and dependency flow

**Tools:**
```bash
# Install madge for dependency visualization
npm install -g madge

# Generate dependency graph
madge --image graph.svg src/

# List circular dependencies
madge --circular src/

# Show dependencies for specific file
madge --depends src/services/user.service.ts src/
```

**Checklist:**
- [ ] Generate module dependency graph
- [ ] Identify entry points (nodes with no incoming edges)
- [ ] Identify leaf modules (nodes with no outgoing edges)
- [ ] Count depth of dependency tree
- [ ] Identify most depended-upon modules (central nodes)

### 3.2 Circular Dependency Detection

**Objective:** Find problematic circular imports

**Commands:**
```bash
# Using madge
madge --circular src/ --extensions ts,tsx

# Manual search for common patterns
# Find files that import each other
find src -name "*.ts" -exec sh -c 'grep -l "from.*user" {} | xargs grep -l "from.*order"' \;
```

**Checklist:**
- [ ] Run circular dependency detector
- [ ] Document all circular dependencies found
- [ ] Classify as: Critical (breaks build) or Benign (runtime only)
- [ ] Identify root cause (mutual import, shared state, etc.)
- [ ] Plan refactoring if needed (extract interface, move to shared module)

**Common Circular Patterns:**

| Pattern | Example | Fix |
|---------|---------|-----|
| Mutual imports | A imports B, B imports A | Extract shared interface to C |
| Shared types | Service A/B both use same type, import each other | Move types to shared/types |
| Barrel exports | index.ts exports all, modules import from index | Direct imports instead of barrel |

### 3.3 External Dependency Audit

**Objective:** Understand third-party dependencies and risks

**Commands:**
```bash
# List all dependencies
jq -r '.dependencies, .devDependencies' package.json

# Count dependencies
jq '[.dependencies, .devDependencies] | add | length' package.json

# Find outdated packages
npm outdated

# Security audit
npm audit

# Check for deprecated packages
npm deprecate-check || npm-check -u

# Find largest dependencies
npx webpack-bundle-analyzer build/stats.json --mode static
```

**Checklist:**

**Dependency Categories:**
- [ ] Framework (React, Vue, Express, NestJS)
- [ ] Database (TypeORM, Prisma, Mongoose)
- [ ] HTTP client (axios, fetch)
- [ ] Validation (Zod, Yup, Joi)
- [ ] Testing (Jest, Vitest, Playwright)
- [ ] Build tools (Webpack, Vite, esbuild)
- [ ] Utility libraries (lodash, date-fns, ramda)

**Dependency Health:**
- [ ] Check last update dates (>2 years = potential abandonment)
- [ ] Check GitHub stars/activity
- [ ] Review security vulnerabilities
- [ ] Identify deprecated packages
- [ ] Check license compatibility

**Dependency Risk Matrix:**

| Criteria | Low Risk | Medium Risk | High Risk |
|----------|----------|-------------|-----------|
| Last Update | <6 months | 6-24 months | >24 months |
| Security Vulns | 0 | 1-3 low | Any critical |
| Downloads/week | >100k | 10k-100k | <10k |
| Maintainers | >3 active | 1-2 | Unmaintained |

### 3.4 Module Boundary Violations

**Objective:** Find violations of architectural layer rules

**Layer Dependency Rules:**

| Architecture | Rule |
|-------------|------|
| Clean Architecture | Domain → nothing, Application → Domain, Infrastructure → Application/Domain |
| Hexagonal | Domain → nothing, Ports → Domain, Adapters → Ports/Domain |
| DDD | Bounded Context A should not import Context B internals |
| VSA | Features should not import each other (except shared) |

**Commands:**
```bash
# Check Clean Architecture violations
# Domain importing infrastructure (VIOLATION)
grep -r "from.*infrastructure" src/domain --include="*.ts"

# Application importing infrastructure (VIOLATION)
grep -r "from.*infrastructure" src/application --include="*.ts"

# Check VSA violations
# Feature A importing Feature B (VIOLATION)
grep -r "from.*features/user" src/features/order --include="*.ts"

# Check for framework leakage into domain
grep -r "import.*express\|import.*fastify\|import.*koa" src/domain --include="*.ts"
```

**Checklist:**
- [ ] Verify domain layer has zero infrastructure imports
- [ ] Check application layer doesn't import presentation
- [ ] Verify features don't cross-import (VSA)
- [ ] Check bounded contexts respect boundaries (DDD)
- [ ] Ensure no direct database access in domain (should use repository)

---

## Phase 4: Convention Detection

### 4.1 Naming Conventions

**Objective:** Document project naming standards

#### File Naming

**Commands:**
```bash
# Check file naming pattern
find src -name "*.ts" | sed 's|.*/||' | head -20

# Count naming styles
find src -name "*-*" | wc -l  # kebab-case
find src -name "*_*" | wc -l  # snake_case
find src -name "*[A-Z]*" | wc -l  # PascalCase/camelCase
```

**Checklist:**
- [ ] Component files: `UserProfile.tsx` (PascalCase) or `user-profile.tsx` (kebab-case)
- [ ] Service files: `user.service.ts` or `userService.ts`
- [ ] Test files: `*.test.ts`, `*.spec.ts`, or `*.test.tsx`
- [ ] Type definition files: `*.types.ts` or `*.d.ts`
- [ ] Config files: `*.config.ts`
- [ ] Utilities: `utils/`, `helpers/`, `lib/`

#### Variable/Function Naming

**Commands:**
```bash
# Find function naming patterns
grep -r "^export function" src --include="*.ts" | head -10
grep -r "^export const.*= (" src --include="*.ts" | head -10

# Find class naming patterns
grep -r "^export class" src --include="*.ts" | head -10

# Find interface naming patterns
grep -r "^export interface" src --include="*.ts" | head -10
```

**Checklist:**
- [ ] Functions: `camelCase` (getUserById, calculateTotal)
- [ ] Classes: `PascalCase` (UserService, OrderRepository)
- [ ] Interfaces: `PascalCase` with/without `I` prefix (IUser vs User)
- [ ] Constants: `UPPER_SNAKE_CASE` or `camelCase`
- [ ] Private fields: `_private` prefix or `#private` syntax
- [ ] Boolean variables: `isActive`, `hasPermission`, `canEdit`

#### Type Naming

**Commands:**
```bash
# Find type alias patterns
grep -r "^export type" src --include="*.ts" | head -10

# Check for enum usage
grep -r "^export enum" src --include="*.ts" | head -10
```

**Checklist:**
- [ ] Type aliases: `PascalCase` (UserDTO, CreateOrderInput)
- [ ] Generics: Single uppercase letter (T, K, V) or descriptive (TUser)
- [ ] Enums: `PascalCase` for name, `UPPER_CASE` or `PascalCase` for values
- [ ] DTOs: `*DTO`, `*Input`, `*Output`, `*Response` suffix

### 4.2 Error Handling Patterns

**Objective:** Understand how errors are managed

**Commands:**
```bash
# Find error classes
find src -name "*Error.ts" -o -name "*Exception.ts"

# Check for custom error usage
grep -r "extends Error" src --include="*.ts"

# Find try-catch patterns
grep -r "try {" src --include="*.ts" | wc -l

# Find error middleware (Express)
grep -r "err, req, res, next" src --include="*.ts"
```

**Checklist:**

**Error Strategy:**
- [ ] Custom error classes (ValidationError, NotFoundError)
- [ ] Error codes/enums
- [ ] Centralized error handler (middleware, global handler)
- [ ] Logging on errors
- [ ] Error transformation (domain → HTTP codes)

**Error Patterns:**

| Pattern | Indicator | Example |
|---------|-----------|---------|
| Result type | `Result<T, E>`, `Either<L, R>` | `return Result.ok(data)` |
| Exception-based | `throw new Error()` | `throw new ValidationError()` |
| Error-first callbacks | `(err, data) =>` | Node.js style |
| Error boundaries | React error boundaries | `componentDidCatch()` |

### 4.3 Testing Patterns

**Objective:** Document testing strategy and conventions

**Commands:**
```bash
# Find test files
find . -name "*.test.ts" -o -name "*.spec.ts" | head -10

# Check test coverage config
cat jest.config.js | grep coverage -A 5

# Count unit vs integration tests
find . -path "*/unit/*" -name "*.test.ts" | wc -l
find . -path "*/integration/*" -name "*.test.ts" | wc -l

# Find test utilities
find . -name "*factory.ts" -o -name "*fixture.ts" -o -name "testUtils.ts"
```

**Checklist:**

**Test Organization:**
- [ ] Co-located tests (`src/user/user.test.ts`)
- [ ] Separate test directory (`tests/unit/`, `tests/integration/`)
- [ ] Test utilities/helpers location
- [ ] Test fixtures/factories

**Test Types:**
- [ ] Unit tests (isolated, mocked dependencies)
- [ ] Integration tests (multiple components)
- [ ] E2E tests (full user flows)
- [ ] Contract tests (API contracts)

**Test Patterns:**
- [ ] AAA (Arrange, Act, Assert)
- [ ] Given-When-Then
- [ ] Test factories for data creation
- [ ] Snapshot testing (React components)

**Test Naming:**
```bash
# Find test naming patterns
grep -r "describe\|it\|test" src --include="*.test.ts" | head -20
```

- [ ] `describe()` for component/function grouping
- [ ] `it()` or `test()` for individual tests
- [ ] Descriptive test names ("should return user when ID exists")

### 4.4 State Management Patterns

**Objective:** Identify how application state is managed

**Commands:**
```bash
# React state management
grep -r "useState\|useReducer\|useContext" src --include="*.tsx" | wc -l

# Redux detection
find . -name "*reducer.ts" -o -name "*action.ts" -o -name "store.ts"

# MobX detection
grep -r "observable\|makeObservable" src --include="*.ts"

# Zustand detection
grep -r "create.*zustand" src --include="*.ts"

# Vue state management
find . -name "*store.ts" | xargs grep -l "defineStore"
```

**Checklist:**

**State Management Library:**
- [ ] Redux (reducers, actions, store)
- [ ] MobX (observables, reactions)
- [ ] Zustand (minimal store)
- [ ] Jotai/Recoil (atomic state)
- [ ] Pinia (Vue)
- [ ] Context API only (React)
- [ ] None (local state only)

**State Patterns:**
- [ ] Single global store vs. multiple stores
- [ ] Normalized state shape
- [ ] Immutable updates (Immer, spread operators)
- [ ] Async state handling (thunks, sagas, RTK Query)
- [ ] Optimistic updates

### 4.5 API Patterns

**Objective:** Document API design and conventions

**Commands:**
```bash
# Find route definitions
grep -r "router\.\(get\|post\|put\|delete\|patch\)" src --include="*.ts" | head -20

# Find API controllers
find src -name "*controller.ts" -o -name "*handler.ts"

# Check for OpenAPI/Swagger
find . -name "swagger.json" -o -name "openapi.yaml"

# Find GraphQL schemas
find . -name "*.graphql" -o -name "schema.ts" | xargs grep -l "GraphQL"
```

**Checklist:**

**API Type:**
- [ ] REST (CRUD operations)
- [ ] GraphQL (schemas, resolvers)
- [ ] gRPC (proto files)
- [ ] WebSocket (real-time)

**REST Conventions:**
- [ ] Plural resource names (`/users`, not `/user`)
- [ ] HTTP verb usage (GET, POST, PUT, DELETE, PATCH)
- [ ] Status code standards (200, 201, 400, 404, 500)
- [ ] Versioning strategy (`/v1/users`, header-based)
- [ ] Pagination (limit/offset, cursor-based)
- [ ] Filtering/sorting query params

**Request/Response Patterns:**
- [ ] DTO (Data Transfer Objects) usage
- [ ] Request validation (middleware, decorators)
- [ ] Response wrapping (`{ data, meta, errors }`)
- [ ] Error response format standardization

---

## Phase 5: Tech Stack Assessment

### 5.1 Framework Version Analysis

**Objective:** Document framework versions and compatibility

**Commands:**
```bash
# Check Node.js version requirement
cat package.json | jq -r '.engines.node'

# List major framework versions
jq -r '.dependencies | to_entries[] | select(.key | contains("react") or contains("vue") or contains("angular") or contains("express") or contains("nestjs")) | "\(.key): \(.value)"' package.json

# Check TypeScript version
jq -r '.devDependencies.typescript' package.json
```

**Checklist:**

**Core Versions:**
- [ ] Node.js version (LTS, current, legacy)
- [ ] TypeScript version
- [ ] Primary framework & version (React 18, Vue 3, etc.)
- [ ] Build tool version (Webpack 5, Vite 4)

**Version Status:**

| Package | Version | Status | Action Needed |
|---------|---------|--------|---------------|
| React | 18.2.0 | Current | None |
| TypeScript | 4.9.5 | Stable | Consider 5.x upgrade |
| Express | 4.18.0 | Stable | None |
| Webpack | 4.46.0 | Outdated | Migrate to 5.x or Vite |

### 5.2 Deprecated API Usage Detection

**Objective:** Find usage of deprecated APIs

**Commands:**
```bash
# React deprecated APIs
grep -r "componentWillMount\|componentWillReceiveProps\|componentWillUpdate" src --include="*.tsx"

# React 18 deprecations
grep -r "ReactDOM.render" src --include="*.tsx"  # Should use createRoot

# Express deprecated middleware
grep -r "bodyParser" src --include="*.ts"  # Built-in now

# Find TODO/FIXME comments about deprecations
grep -r "TODO.*deprecat\|FIXME.*deprecat" src --include="*.ts"
```

**Checklist:**

**Common Deprecations:**

| Framework | Deprecated API | Replacement | Search Command |
|-----------|---------------|-------------|----------------|
| React | componentWillMount | useEffect hook | `grep -r "componentWillMount"` |
| React | ReactDOM.render | createRoot | `grep -r "ReactDOM.render"` |
| Express | bodyParser | express.json() | `grep -r "bodyParser"` |
| TypeScript | `namespace` | ES modules | `grep -r "^namespace "` |
| Node.js | `url.parse` | new URL() | `grep -r "url.parse"` |

### 5.3 Security Vulnerability Scan

**Objective:** Identify security risks in dependencies

**Commands:**
```bash
# NPM audit
npm audit --json | jq '.metadata'

# Check for high/critical vulnerabilities
npm audit --audit-level=high

# Generate audit report
npm audit --json > audit-report.json

# Check for known malicious packages
npx @lavamoat/allow-scripts

# Check for license issues
npx license-checker --summary
```

**Checklist:**

**Security Scan:**
- [ ] Run `npm audit` and document findings
- [ ] Check for critical/high vulnerabilities
- [ ] Verify all packages have acceptable licenses
- [ ] Check for prototype pollution vulnerabilities
- [ ] Look for hardcoded secrets/credentials
- [ ] Verify HTTPS usage (no HTTP in production)

**Secrets Detection:**
```bash
# Find potential secrets
grep -r "api_key\|API_KEY\|secret\|password\|token" src --include="*.ts" | grep -v "placeholder"

# Check for .env files in repo (should not be committed)
find . -name ".env" -not -path "*/node_modules/*"

# Verify .env.example exists
ls .env.example
```

**Security Best Practices Checklist:**
- [ ] No secrets in code (use environment variables)
- [ ] `.env` in `.gitignore`
- [ ] HTTPS enforced
- [ ] Input validation present
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitization)
- [ ] CSRF protection (tokens)
- [ ] Rate limiting implemented

---

## Output Format

### Structured Analysis Report

```markdown
# Codebase Analysis Report

**Project:** {name}
**Analyzed:** {date}
**Analyzer:** {agent-name}

## Executive Summary

- **Architecture Pattern:** {Clean/DDD/VSA/Hexagonal/MVC}
- **Primary Language:** {TypeScript/JavaScript/Python}
- **Framework:** {React/Vue/Express/NestJS}
- **Lines of Code:** {count}
- **Dependencies:** {count}
- **Test Coverage:** {percentage}%

## Phase 1: Structure

### Directory Layout
{tree output}

### Key Directories
- Source: `src/`
- Tests: `tests/`
- Config: `config/`

### Configuration Files
- Package manager: `package.json`
- TypeScript: `tsconfig.json`
- Linter: `.eslintrc.js`
- Build: `webpack.config.js`

### Entry Points
- Main: `src/index.ts`
- Server: `src/server.ts`

## Phase 2: Architecture

### Pattern: {identified pattern}

**Confidence:** High/Medium/Low

**Evidence:**
- ✅ Directory structure matches pattern
- ✅ Naming conventions align
- ✅ Dependency flow correct

**Violations:**
- ❌ {any violations found}

## Phase 3: Dependencies

### Dependency Graph
{summary or link to graph}

### Circular Dependencies
{count found}
{list if any}

### External Dependencies
- Production: {count}
- Development: {count}
- Outdated: {count}

### High-Risk Dependencies
{list if any}

## Phase 4: Conventions

### Naming
- Files: kebab-case
- Functions: camelCase
- Classes: PascalCase
- Interfaces: PascalCase (no I prefix)

### Error Handling
- Pattern: Custom error classes
- Centralized: Yes (middleware)

### Testing
- Framework: Jest
- Coverage: {percentage}%
- Types: Unit, Integration, E2E

### State Management
- Library: Redux Toolkit
- Pattern: Normalized state

### API
- Type: REST
- Versioning: URL-based (/v1/)
- Validation: Zod schemas

## Phase 5: Tech Stack

### Versions
- Node.js: 18.x (LTS)
- TypeScript: 5.0
- React: 18.2
- Express: 4.18

### Deprecations Found
{list or "None"}

### Security
- Vulnerabilities: {count} ({severity breakdown})
- Action Required: {yes/no}

## Recommendations

1. {recommendation 1}
2. {recommendation 2}
3. {recommendation 3}

## Next Steps

- [ ] {action item 1}
- [ ] {action item 2}
```

---

## Appendix: Quick Reference Commands

```bash
# Project overview
tree -L 2 src/
find . -name "*.ts" | wc -l

# Pattern detection
ls -la src/

# Dependency analysis
npx madge --circular src/
npm outdated

# Security
npm audit
grep -r "API_KEY" src/

# Testing
npm test -- --coverage

# Build
npm run build
```

---

**Last Updated:** 2026-02-20
**Version:** 1.0.0
