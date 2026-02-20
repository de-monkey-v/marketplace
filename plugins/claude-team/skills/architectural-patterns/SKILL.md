---
name: architectural-patterns
description: "Architecture analysis and design reference. Provides codebase analysis checklists, ADR writing templates, pattern catalogs, and Breaking Change analysis matrices for systematic architectural decision-making."
version: 1.0.0
---

# Architectural Patterns Reference

A comprehensive reference skill for software architecture analysis, design decision-making, and impact assessment.

## Overview

This skill equips AI agents with systematic frameworks for analyzing codebases, documenting architectural decisions, and evaluating change impacts. It provides actionable checklists, decision matrices, and templates that ensure thorough analysis and clear documentation.

### Use Cases

- **Codebase Analysis** - Systematically identify architecture patterns, conventions, and tech stack
- **Design Documentation** - Write Architecture Decision Records (ADRs) with proper context
- **Pattern Selection** - Compare and choose appropriate architectural patterns
- **Impact Assessment** - Analyze breaking changes and plan migration strategies
- **Code Review** - Evaluate architectural compliance and detect violations

### When to Use This Skill

| Scenario | Primary Reference | Secondary References |
|----------|------------------|---------------------|
| Analyzing unknown codebase | analysis-checklist | - |
| Choosing architecture pattern | adr-templates | analysis-checklist |
| Documenting design decision | adr-templates | - |
| Evaluating API changes | breaking-change | analysis-checklist |
| Refactoring assessment | breaking-change | adr-templates |
| Dependency migration | breaking-change | analysis-checklist |

## References

### analysis-checklist.md

**Purpose:** Comprehensive codebase analysis framework

**Content:**
- **Phase 1: Project Structure** - Directory layout mapping, config inventory, entry point identification
- **Phase 2: Pattern Detection** - Decision matrix for Clean Arch, DDD, VSA, Hexagonal, MVC, Modular Monolith
- **Phase 3: Dependency Analysis** - Import graphs, circular dependencies, boundary violations
- **Phase 4: Convention Detection** - Naming patterns, error handling, testing, state management
- **Phase 5: Tech Stack Assessment** - Framework versions, deprecated APIs, security scan

**Use When:**
- First encounter with a codebase
- Planning refactoring or migration
- Onboarding to a project
- Conducting code review
- Preparing architecture documentation

**Key Features:**
- Checkbox-based checklist format
- Automated detection commands (grep, find, tree)
- Pattern identification decision tables
- Concrete examples for each analysis phase

---

### adr-templates.md

**Purpose:** Architecture Decision Record templates and pattern catalog

**Content:**
- **ADR Template** - Standard format for documenting decisions (Status, Context, Decision, Options, Consequences)
- **Pattern Catalog** - Detailed descriptions of 8+ architectural patterns
  - Clean Architecture
  - Domain-Driven Design (DDD)
  - Vertical Slice Architecture (VSA)
  - Hexagonal Architecture (Ports & Adapters)
  - Modular Monolith
  - Event-Driven Architecture
  - Microservices
  - CQRS (Command Query Responsibility Segregation)
- **Pattern Decision Matrix** - Comparison table by team size, complexity, scalability needs
- **Migration Paths** - How to evolve from simpler to more sophisticated patterns

**Use When:**
- Making architectural decisions
- Comparing design alternatives
- Documenting technical choices
- Planning system evolution
- Evaluating pattern fit

**Key Features:**
- Copy-paste ready ADR template
- Pros/Cons tables for each pattern
- When-to-use guidelines
- Typical directory structures
- Real-world applicability criteria

---

### breaking-change.md

**Purpose:** Breaking change impact analysis framework

**Content:**
- **Impact Classification** - 4-level severity matrix (Critical, High, Medium, Low)
- **Change Categories** - API contracts, data models, behavior, configuration, dependencies
- **Analysis Matrix** - Template for systematic impact documentation
- **Mitigation Strategies** - Versioning, deprecation, feature flags, backward compatibility
- **Automated Detection** - Commands and tools for identifying breaking changes
- **Consumer Communication** - Notification checklists and migration guides

**Use When:**
- Planning API changes
- Upgrading dependencies
- Refactoring public interfaces
- Database schema changes
- Removing deprecated features
- Releasing major versions

**Key Features:**
- Standardized impact levels
- Detection automation guidance
- Migration strategy templates
- Semver compliance guidelines
- Consumer-focused communication plans

## Usage Patterns

### Pattern 1: New Codebase Analysis

```
1. Read analysis-checklist.md
2. Execute Phase 1-5 checklists systematically
3. Document findings in structured format
4. If architectural decision needed → Read adr-templates.md
5. If changes planned → Read breaking-change.md
```

### Pattern 2: Architectural Decision Making

```
1. Read adr-templates.md (Pattern Catalog)
2. Use Pattern Decision Matrix to narrow options
3. Read detailed pattern descriptions for finalists
4. Fill out ADR Template with decision rationale
5. Document in project's architecture/decisions/ directory
```

### Pattern 3: Breaking Change Assessment

```
1. Read breaking-change.md
2. Classify change using Impact Classification table
3. Fill out Analysis Matrix for affected components
4. Select Mitigation Strategy
5. Use automated detection commands to verify impact
6. Prepare consumer communication using checklist
```

### Pattern 4: Code Review (Architecture Focus)

```
1. Read analysis-checklist.md (Phase 2: Pattern Detection)
2. Identify intended architecture pattern
3. Check for pattern violations using Phase 3 (Dependency Analysis)
4. Verify conventions using Phase 4 checklist
5. If violations found → Consult adr-templates.md for proper structure
```

## Related Agents

This skill is referenced by multiple specialized agents:

| Agent | Role | References Used | Purpose |
|-------|------|----------------|---------|
| `architect` | Architecture design/analysis | ALL | Comprehensive architectural work |
| `reviewer` | Code review | analysis-checklist | Pattern compliance verification |
| `db-architect` | Database design | adr-templates | Schema design decisions |
| `ddd-strategist` | Domain modeling | adr-templates | DDD pattern application |
| `side-effect-analyzer` | Impact analysis | breaking-change | Change risk assessment |
| `implementer` | Feature implementation | analysis-checklist | Understanding existing patterns |
| `planner` | Project planning | analysis-checklist | Codebase familiarity |
| `researcher` | Technical investigation | analysis-checklist | Systematic exploration |

## Execution Workflow

### For Agents Using This Skill

**Step 1: Identify Analysis Type**
- Structure analysis → analysis-checklist.md
- Design decision → adr-templates.md
- Impact assessment → breaking-change.md

**Step 2: Read Relevant Reference**
```
Read(/path/to/architectural-patterns/references/{reference-file}.md)
```

**Step 3: Apply Framework**
- Follow checklists sequentially
- Fill out templates completely
- Execute suggested commands
- Document findings

**Step 4: Output Results**
- Structured findings (for checklists)
- Completed ADR (for decisions)
- Impact matrix (for changes)

## Best Practices

### Analysis Checklist Usage

1. **Sequential Execution** - Complete phases in order (1→5)
2. **Command Automation** - Run provided grep/find commands to gather data
3. **Documentation** - Record findings in structured markdown
4. **Pattern Matching** - Use decision matrices, don't guess patterns
5. **Completeness** - Check all items before concluding analysis

### ADR Template Usage

1. **Status Clarity** - Always set initial status (usually "Proposed")
2. **Context First** - Explain problem before solution
3. **Multiple Options** - Document at least 2 alternatives considered
4. **Consequences Honesty** - Include negative consequences and risks
5. **Future Reference** - Write for readers unfamiliar with current context

### Breaking Change Framework Usage

1. **Impact Level First** - Classify severity before detailed analysis
2. **Consumer Focus** - Think from API consumer perspective
3. **Automated Detection** - Use tools to catch non-obvious breaks
4. **Migration Plan** - Always provide upgrade path
5. **Communication** - Notify affected parties early

## Integration with Other Skills

### With `team-lifecycle`
- `architect` agents spawned via Task tool use this skill
- Analysis results communicated via SendMessage

### With `testing-strategies`
- Breaking change detection triggers regression test planning
- Pattern analysis informs testing strategy selection

### With `code-quality`
- Architecture patterns define quality standards
- Analysis checklist overlaps with code review criteria

### With `api-design`
- Breaking change framework applies to API changes
- ADR templates document API design decisions

## Examples

### Example 1: Analyzing a TypeScript Project

```typescript
// Agent reads analysis-checklist.md Phase 1
// Executes: tree -L 3 src/

src/
├── domain/          // Clean Architecture indicator
├── application/
├── infrastructure/
└── presentation/

// Conclusion: Likely Clean Architecture
// Next: Read adr-templates.md Clean Architecture section
```

### Example 2: Documenting Pattern Choice

```markdown
# ADR-001: Adopt Vertical Slice Architecture

## Status
Accepted

## Context
Team of 4 developers building CRUD-heavy application.
Current MVC structure has controllers growing too large.
Need better feature isolation for parallel development.

## Decision
Adopt Vertical Slice Architecture, organizing by features.

## Options Considered

### Option A: Clean Architecture
- Pros: Clear layer separation, testable
- Cons: Too much ceremony for CRUD features

### Option B: Vertical Slice Architecture
- Pros: Feature isolation, minimal coupling, easy parallel work
- Cons: Potential code duplication across slices

## Consequences

### Positive
- Features can be developed independently
- Easier to onboard new developers
- Clear ownership boundaries

### Negative
- Some duplication of validation logic
- Need to establish cross-cutting concerns pattern

### Risks
- Team needs training on VSA principles
```

### Example 3: Breaking Change Analysis

```markdown
## Change: Remove deprecated `getUserById()` function

| Category | API Contract |
| Impact Level | Critical |
| Affected Consumers | Mobile app (v2.1), Admin dashboard |
| Detection Method | grep -r "getUserById" --include="*.ts" |
| Migration Strategy | Provide `getUser()` with same signature |

**Migration Guide:**
```typescript
// Before
const user = await getUserById(123);

// After
const user = await getUser({ id: 123 });
```

**Timeline:**
- v3.0.0-beta.1: Add `getUser()`, deprecate `getUserById()`
- v3.0.0-rc.1: Console warnings for `getUserById()` usage
- v3.0.0: Remove `getUserById()`
```

## Maintenance

### Updating References

When updating pattern catalogs or frameworks:

1. Maintain backward compatibility in template formats
2. Add new patterns without removing existing ones
3. Update decision matrices with new criteria
4. Version the skill (increment `version` in frontmatter)

### Feedback Integration

If agents report missing analysis items:

1. Add to relevant checklist phase
2. Provide example detection command
3. Update related decision matrices

## Quick Reference

### File Locations

```
architectural-patterns/
├── SKILL.md                              # This file
└── references/
    ├── analysis-checklist.md             # ~400 lines - Codebase analysis
    ├── adr-templates.md                  # ~400 lines - Decision docs + patterns
    └── breaking-change.md                # ~350 lines - Impact analysis
```

### Typical Usage Commands

```bash
# For agents analyzing code
Read(/home/monkey/.../architectural-patterns/references/analysis-checklist.md)

# For agents making design decisions
Read(/home/monkey/.../architectural-patterns/references/adr-templates.md)

# For agents evaluating changes
Read(/home/monkey/.../architectural-patterns/references/breaking-change.md)
```

## See Also

### Related Skills
- **`code-quality`** - Code review and standards enforcement
- **`testing-strategies`** - Test planning aligned with architecture
- **`api-design`** - API design principles and patterns
- **`backend-patterns`** - Implementation patterns for backend systems

### External Resources
- [C4 Model](https://c4model.com/) - Architecture visualization
- [ADR GitHub Org](https://adr.github.io/) - ADR best practices
- [Semantic Versioning](https://semver.org/) - Breaking change versioning

---

**Version:** 1.0.0
**Last Updated:** 2026-02-20
**Maintained By:** Claude Team Platform
