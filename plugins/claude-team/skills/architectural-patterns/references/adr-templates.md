# Architecture Decision Records (ADR) Templates & Pattern Catalog

Comprehensive templates for documenting architectural decisions and detailed catalog of common software architecture patterns.

## Table of Contents

1. [ADR Template](#adr-template)
2. [Architecture Pattern Catalog](#architecture-pattern-catalog)
3. [Pattern Decision Matrix](#pattern-decision-matrix)
4. [Migration Paths](#migration-paths)

---

## ADR Template

### Standard Format

Use this template for documenting all architectural decisions. Copy and fill out each section.

```markdown
# ADR-{NNN}: {Short Descriptive Title}

## Status

{Proposed | Accepted | Deprecated | Superseded by ADR-XXX}

## Context

{What is the issue that we're seeing that is motivating this decision or change?}

### Background
{Provide relevant background information, constraints, and requirements}

### Problem Statement
{Clear articulation of the problem to be solved}

### Goals
- {Goal 1}
- {Goal 2}

### Non-Goals
- {What this decision explicitly does NOT address}

## Decision

{What is the change that we're actually proposing and/or doing?}

{Describe the chosen solution clearly and concisely}

## Options Considered

### Option A: {Option Name}

**Description:** {Brief description}

**Pros:**
- ✅ {Pro 1}
- ✅ {Pro 2}

**Cons:**
- ❌ {Con 1}
- ❌ {Con 2}

**Effort Estimate:** {Low/Medium/High}

### Option B: {Option Name}

**Description:** {Brief description}

**Pros:**
- ✅ {Pro 1}
- ✅ {Pro 2}

**Cons:**
- ❌ {Con 1}
- ❌ {Con 2}

**Effort Estimate:** {Low/Medium/High}

### Option C: Do Nothing

**Description:** Continue with current approach

**Pros:**
- ✅ No migration cost
- ✅ No learning curve

**Cons:**
- ❌ Problem remains unsolved
- ❌ Technical debt accumulates

## Consequences

### Positive
- {Positive consequence 1}
- {Positive consequence 2}

### Negative
- {Negative consequence 1}
- {Negative consequence 2}

### Neutral
- {Neutral impact 1}

### Risks
- **Risk 1:** {description} - Mitigation: {strategy}
- **Risk 2:** {description} - Mitigation: {strategy}

## Implementation Plan

### Phase 1: {Phase Name}
- {Task 1}
- {Task 2}

### Phase 2: {Phase Name}
- {Task 1}
- {Task 2}

### Rollback Strategy
{How to undo this decision if it proves problematic}

## Metrics

How will we measure success?

- {Metric 1: e.g., Build time reduced by 30%}
- {Metric 2: e.g., Test coverage above 80%}
- {Metric 3: e.g., Deployment time under 10 minutes}

## References

- {Link to related ADRs}
- {Link to relevant documentation}
- {Link to research/benchmarks}

## Notes

{Any additional context, discussion points, or follow-up items}

---

**Author:** {name}
**Date:** {YYYY-MM-DD}
**Reviewers:** {names}
**Approved By:** {name}
```

---

## Architecture Pattern Catalog

### 1. Clean Architecture

**Overview:** Concentric layer architecture with dependencies pointing inward toward the domain core.

**Layers (outside → inside):**
1. **Frameworks & Drivers** (outermost) - UI, database, external APIs
2. **Interface Adapters** - Controllers, presenters, gateways
3. **Application Business Rules** - Use cases, interactors
4. **Enterprise Business Rules** (innermost) - Entities, domain models

**When to Use:**

| Criteria | Recommendation |
|----------|---------------|
| Project Size | Medium to Large (>50k LOC) |
| Team Size | 5-20 developers |
| Domain Complexity | High business logic complexity |
| Lifespan | Long-term (5+ years) |
| Testing Needs | Critical (need isolated unit tests) |

**Key Principles:**
- Dependency Rule: Dependencies only point inward
- Framework Independence: Core business logic isolated from frameworks
- Testability: Inner layers testable without UI, database, or external services
- UI Independence: Can swap UI without changing business rules

**Typical Directory Structure:**
```
src/
├── domain/                  # Innermost layer
│   ├── entities/
│   │   ├── User.ts
│   │   └── Order.ts
│   └── interfaces/          # Interfaces for outer layers to implement
│       ├── IUserRepository.ts
│       └── IEmailService.ts
├── application/             # Use cases layer
│   ├── usecases/
│   │   ├── CreateUser/
│   │   │   ├── CreateUserUseCase.ts
│   │   │   ├── CreateUserDTO.ts
│   │   │   └── CreateUserUseCase.test.ts
│   │   └── GetUser/
│   └── ports/               # Input/output ports
├── infrastructure/          # Outer layer - implementations
│   ├── persistence/
│   │   └── TypeORMUserRepository.ts  # Implements IUserRepository
│   ├── messaging/
│   │   └── NodemailerEmailService.ts # Implements IEmailService
│   └── web/
│       └── express/
└── presentation/            # Outermost layer
    ├── http/
    │   ├── controllers/
    │   └── middleware/
    └── graphql/
        └── resolvers/
```

**Pros:**
- ✅ Highly testable (mock outer layers easily)
- ✅ Framework agnostic core
- ✅ Clear separation of concerns
- ✅ Scalable for large teams
- ✅ Business logic independent of infrastructure

**Cons:**
- ❌ Steep learning curve
- ❌ More boilerplate code
- ❌ Over-engineering for simple CRUD apps
- ❌ Requires discipline to maintain boundaries

**Code Example:**
```typescript
// domain/entities/User.ts
export class User {
  constructor(
    private readonly id: string,
    private readonly email: string,
    private name: string
  ) {}

  updateName(newName: string): void {
    // Business rule: name must not be empty
    if (!newName.trim()) throw new Error('Name cannot be empty');
    this.name = newName;
  }
}

// domain/interfaces/IUserRepository.ts
export interface IUserRepository {
  save(user: User): Promise<void>;
  findById(id: string): Promise<User | null>;
}

// application/usecases/CreateUser/CreateUserUseCase.ts
export class CreateUserUseCase {
  constructor(private userRepository: IUserRepository) {}

  async execute(dto: CreateUserDTO): Promise<User> {
    const user = new User(dto.id, dto.email, dto.name);
    await this.userRepository.save(user);
    return user;
  }
}

// infrastructure/persistence/TypeORMUserRepository.ts
export class TypeORMUserRepository implements IUserRepository {
  async save(user: User): Promise<void> {
    // TypeORM implementation details
  }
}
```

---

### 2. Domain-Driven Design (DDD)

**Overview:** Strategic and tactical patterns for modeling complex business domains.

**Core Concepts:**
- **Bounded Contexts** - Explicit boundaries for domain models
- **Ubiquitous Language** - Shared vocabulary between developers and domain experts
- **Aggregates** - Cluster of entities treated as single unit
- **Entities** - Objects with identity that persist over time
- **Value Objects** - Immutable objects defined by attributes
- **Domain Events** - Record of something that happened in the domain
- **Repositories** - Abstraction for retrieving aggregates
- **Application Services** - Orchestrate use cases, call domain logic

**When to Use:**

| Criteria | Recommendation |
|----------|---------------|
| Project Size | Large (>100k LOC) |
| Team Size | 10-50 developers |
| Domain Complexity | Very high (finance, healthcare, logistics) |
| Business Involvement | High collaboration with domain experts |
| Strategic Modeling | Multiple bounded contexts needed |

**Typical Directory Structure:**
```
src/
├── contexts/                # Bounded contexts
│   ├── sales/              # Sales context
│   │   ├── domain/
│   │   │   ├── aggregates/
│   │   │   │   └── Order.ts
│   │   │   ├── entities/
│   │   │   │   └── OrderLine.ts
│   │   │   ├── valueobjects/
│   │   │   │   ├── Money.ts
│   │   │   │   └── OrderStatus.ts
│   │   │   ├── events/
│   │   │   │   └── OrderPlacedEvent.ts
│   │   │   └── repositories/
│   │   │       └── IOrderRepository.ts
│   │   ├── application/
│   │   │   ├── commands/
│   │   │   │   └── PlaceOrderHandler.ts
│   │   │   └── queries/
│   │   │       └── GetOrderHandler.ts
│   │   └── infrastructure/
│   │       ├── persistence/
│   │       └── messaging/
│   └── inventory/          # Inventory context (separate model!)
│       ├── domain/
│       ├── application/
│       └── infrastructure/
└── shared/                 # Shared kernel
    └── Money.ts            # Shared across contexts
```

**Pros:**
- ✅ Handles complex domains well
- ✅ Aligns code with business language
- ✅ Scalable for large teams (bounded contexts)
- ✅ Rich domain models with behavior
- ✅ Facilitates domain expert collaboration

**Cons:**
- ❌ Highest learning curve
- ❌ Significant upfront modeling effort
- ❌ Overkill for simple domains
- ❌ Risk of over-engineering
- ❌ Requires experienced architects

**Code Example:**
```typescript
// Value Object
export class Money {
  private constructor(
    private readonly amount: number,
    private readonly currency: string
  ) {
    if (amount < 0) throw new Error('Amount cannot be negative');
  }

  static create(amount: number, currency: string): Money {
    return new Money(amount, currency);
  }

  add(other: Money): Money {
    if (this.currency !== other.currency) {
      throw new Error('Cannot add different currencies');
    }
    return new Money(this.amount + other.amount, this.currency);
  }
}

// Aggregate Root
export class Order {
  private orderLines: OrderLine[] = [];
  private status: OrderStatus = OrderStatus.Draft;

  addLine(product: Product, quantity: number): void {
    if (this.status !== OrderStatus.Draft) {
      throw new Error('Cannot modify confirmed order');
    }
    this.orderLines.push(new OrderLine(product, quantity));
  }

  confirm(): OrderPlacedEvent {
    if (this.orderLines.length === 0) {
      throw new Error('Cannot confirm empty order');
    }
    this.status = OrderStatus.Confirmed;
    return new OrderPlacedEvent(this.id, new Date());
  }

  // Aggregate ensures consistency across orderLines
  getTotalPrice(): Money {
    return this.orderLines.reduce(
      (total, line) => total.add(line.getPrice()),
      Money.create(0, 'USD')
    );
  }
}
```

---

### 3. Vertical Slice Architecture (VSA)

**Overview:** Organize code by feature/use case rather than technical layer. Each slice contains all layers needed for that feature.

**When to Use:**

| Criteria | Recommendation |
|----------|---------------|
| Project Size | Small to Medium (<100k LOC) |
| Team Size | 2-10 developers |
| Domain Complexity | Low to Medium |
| Feature Independence | High (features rarely interact) |
| Delivery Speed | Critical (frequent releases) |

**Key Principles:**
- Feature folders contain everything needed for that feature
- Vertical slices over horizontal layers
- Minimize coupling between features
- Shared code explicitly in `shared/` or `common/`
- Often combined with CQRS (Commands & Queries)

**Typical Directory Structure:**
```
src/
├── features/
│   ├── createUser/
│   │   ├── CreateUserCommand.ts       # Request DTO
│   │   ├── CreateUserHandler.ts       # Business logic
│   │   ├── CreateUserValidator.ts     # Validation
│   │   ├── CreateUserRepository.ts    # Data access (if specific)
│   │   └── CreateUserHandler.test.ts
│   ├── getUser/
│   │   ├── GetUserQuery.ts
│   │   ├── GetUserHandler.ts
│   │   └── GetUserHandler.test.ts
│   ├── updateUserEmail/
│   │   ├── UpdateUserEmailCommand.ts
│   │   ├── UpdateUserEmailHandler.ts
│   │   └── UpdateUserEmailValidator.ts
│   └── deleteUser/
│       └── ...
├── shared/                            # Truly shared code only
│   ├── database/
│   │   └── DatabaseConnection.ts
│   ├── validation/
│   │   └── ValidationPipeline.ts
│   └── types/
│       └── User.ts                    # Shared User type
└── infrastructure/
    ├── http/
    │   └── app.ts                     # Routes map to handlers
    └── database/
        └── migrations/
```

**Pros:**
- ✅ Features are isolated (easy parallel development)
- ✅ Easy to understand (all code for feature in one place)
- ✅ Fast onboarding (focus on one feature)
- ✅ Minimal ceremony (less boilerplate than Clean/DDD)
- ✅ Easy to delete features (remove one folder)

**Cons:**
- ❌ Potential code duplication across slices
- ❌ Shared concepts harder to manage
- ❌ Can fragment team knowledge
- ❌ Less clear for cross-cutting concerns
- ❌ Risk of inconsistency between slices

**Code Example:**
```typescript
// features/createUser/CreateUserCommand.ts
export class CreateUserCommand {
  constructor(
    public readonly email: string,
    public readonly name: string
  ) {}
}

// features/createUser/CreateUserHandler.ts
export class CreateUserHandler {
  constructor(private db: Database, private validator: Validator) {}

  async handle(command: CreateUserCommand): Promise<UserDTO> {
    // Validation
    await this.validator.validate(command);

    // Business logic
    const userId = generateId();
    const user = { id: userId, email: command.email, name: command.name };

    // Persistence
    await this.db.users.insert(user);

    // Return
    return { id: userId, email: user.email, name: user.name };
  }
}

// infrastructure/http/routes.ts
app.post('/users', async (req, res) => {
  const command = new CreateUserCommand(req.body.email, req.body.name);
  const result = await container.resolve(CreateUserHandler).handle(command);
  res.status(201).json(result);
});
```

---

### 4. Hexagonal Architecture (Ports & Adapters)

**Overview:** Isolate core application logic from external concerns using ports (interfaces) and adapters (implementations).

**When to Use:**

| Criteria | Recommendation |
|----------|---------------|
| Project Size | Medium (30k-150k LOC) |
| Team Size | 3-15 developers |
| Domain Complexity | Medium to High |
| External Integrations | Multiple (databases, APIs, message queues) |
| Testing Needs | High (need to mock externals easily) |

**Core Concepts:**
- **Domain (Core)** - Business logic, completely isolated
- **Ports** - Interfaces defining how core interacts with outside
  - **Primary/Driving Ports** - Use case interfaces (e.g., ICreateUserUseCase)
  - **Secondary/Driven Ports** - Infrastructure interfaces (e.g., IUserRepository)
- **Adapters** - Concrete implementations of ports
  - **Primary/Driving Adapters** - Controllers, CLI, GraphQL resolvers
  - **Secondary/Driven Adapters** - Database repos, HTTP clients, message publishers

**Typical Directory Structure:**
```
src/
├── domain/                     # The hexagon (core)
│   ├── models/
│   │   └── User.ts
│   ├── services/
│   │   └── UserService.ts      # Domain logic
│   └── exceptions/
│       └── UserNotFoundError.ts
├── ports/
│   ├── primary/               # Driving ports (inbound)
│   │   ├── ICreateUserUseCase.ts
│   │   └── IGetUserUseCase.ts
│   └── secondary/             # Driven ports (outbound)
│       ├── IUserRepository.ts
│       ├── IEmailService.ts
│       └── IEventPublisher.ts
├── adapters/
│   ├── primary/               # Driving adapters (inbound)
│   │   ├── http/
│   │   │   ├── UserController.ts
│   │   │   └── routes.ts
│   │   ├── cli/
│   │   │   └── UserCLI.ts
│   │   └── graphql/
│   │       └── UserResolver.ts
│   └── secondary/             # Driven adapters (outbound)
│       ├── persistence/
│       │   ├── MongoUserRepository.ts    # Implements IUserRepository
│       │   └── PostgresUserRepository.ts
│       ├── messaging/
│       │   └── SendGridEmailService.ts   # Implements IEmailService
│       └── events/
│           └── KafkaEventPublisher.ts
└── application/               # Orchestration layer
    └── usecases/
        ├── CreateUserUseCase.ts  # Implements ICreateUserUseCase
        └── GetUserUseCase.ts
```

**Pros:**
- ✅ Highly testable (easy to swap adapters)
- ✅ Technology agnostic core
- ✅ Clear dependency flow
- ✅ Easy to add new adapters (new DB, new API)
- ✅ Good for polyglot systems

**Cons:**
- ❌ Many interfaces (can feel like boilerplate)
- ❌ Complexity for simple apps
- ❌ Learning curve for ports/adapters concept
- ❌ More files to navigate

**Code Example:**
```typescript
// ports/secondary/IUserRepository.ts
export interface IUserRepository {
  save(user: User): Promise<void>;
  findById(id: string): Promise<User | null>;
}

// domain/services/UserService.ts
export class UserService {
  constructor(
    private userRepo: IUserRepository,
    private emailService: IEmailService
  ) {}

  async createUser(email: string, name: string): Promise<User> {
    const user = new User(generateId(), email, name);
    await this.userRepo.save(user);
    await this.emailService.sendWelcome(email);
    return user;
  }
}

// adapters/secondary/persistence/PostgresUserRepository.ts
export class PostgresUserRepository implements IUserRepository {
  constructor(private pool: Pool) {}

  async save(user: User): Promise<void> {
    await this.pool.query(
      'INSERT INTO users (id, email, name) VALUES ($1, $2, $3)',
      [user.id, user.email, user.name]
    );
  }
}

// adapters/primary/http/UserController.ts
export class UserController {
  constructor(private userService: UserService) {}

  async create(req: Request, res: Response): Promise<void> {
    const user = await this.userService.createUser(req.body.email, req.body.name);
    res.status(201).json(user);
  }
}
```

---

### 5. Modular Monolith

**Overview:** Single deployable application divided into independent modules with clear boundaries.

**When to Use:**

| Criteria | Recommendation |
|----------|---------------|
| Project Size | Medium to Large (50k-500k LOC) |
| Team Size | 5-30 developers |
| Domain Complexity | Medium to High |
| Deployment Complexity | Want simplicity (single deployment) |
| Team Organization | Multiple teams working on different areas |

**Key Principles:**
- Modules are independently developable
- Each module has defined public API
- Modules communicate via interfaces, not implementation
- Eventual evolution to microservices possible
- Shared kernel for cross-cutting concerns

**Typical Directory Structure:**
```
src/
├── modules/
│   ├── user/
│   │   ├── api/                       # Public API of module
│   │   │   ├── IUserService.ts
│   │   │   ├── UserDTO.ts
│   │   │   └── UserEvents.ts
│   │   ├── domain/                    # Internal domain logic
│   │   │   ├── User.ts
│   │   │   └── UserFactory.ts
│   │   ├── application/
│   │   │   ├── UserService.ts         # Implements IUserService
│   │   │   └── UserCommandHandler.ts
│   │   ├── infrastructure/
│   │   │   └── UserRepository.ts
│   │   └── presentation/
│   │       └── UserController.ts
│   ├── order/
│   │   ├── api/
│   │   │   └── IOrderService.ts
│   │   ├── domain/
│   │   ├── application/
│   │   │   └── OrderService.ts        # Can depend on user/api
│   │   ├── infrastructure/
│   │   └── presentation/
│   └── payment/
│       ├── api/
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       └── presentation/
├── shared/                            # Shared kernel
│   ├── database/
│   ├── events/
│   └── validation/
└── infrastructure/
    ├── http/
    │   └── app.ts                     # Wires up all modules
    └── database/
        └── migrations/
```

**Dependency Rules:**
- ✅ `order` can depend on `user/api`
- ❌ `order` CANNOT depend on `user/domain` or `user/infrastructure`
- ✅ All modules can depend on `shared/`

**Pros:**
- ✅ Simple deployment (one artifact)
- ✅ Easier transactions across modules
- ✅ No network latency between modules
- ✅ Shared code management simpler
- ✅ Can evolve to microservices later

**Cons:**
- ❌ Requires discipline to maintain boundaries
- ❌ All modules scale together
- ❌ Shared database can become bottleneck
- ❌ Deployment couples all modules
- ❌ Risk of tight coupling over time

---

### 6. Event-Driven Architecture

**Overview:** Components communicate asynchronously via events rather than direct calls.

**When to Use:**

| Criteria | Recommendation |
|----------|---------------|
| Project Size | Medium to Large |
| Domain Complexity | High (complex workflows) |
| Scalability Needs | High (need to scale components independently) |
| Async Processing | Required (background jobs, notifications) |
| Eventual Consistency | Acceptable |

**Key Patterns:**
- **Event Notification** - Notify when something happened
- **Event-Carried State Transfer** - Events carry full state
- **Event Sourcing** - Store events as source of truth
- **CQRS** - Separate read and write models

**Pros:**
- ✅ Loose coupling between components
- ✅ Scalability (async processing)
- ✅ Audit trail (event log)
- ✅ Flexibility to add new consumers

**Cons:**
- ❌ Eventual consistency complexity
- ❌ Debugging harder (distributed traces)
- ❌ Event schema evolution challenges
- ❌ Requires message broker infrastructure

---

### 7. Microservices

**Overview:** Independently deployable services organized around business capabilities.

**When to Use:**

| Criteria | Recommendation |
|----------|---------------|
| Project Size | Very Large (>500k LOC across services) |
| Team Size | 20-100+ developers |
| Deployment Independence | Critical |
| Polyglot Requirements | Yes (different languages/frameworks) |
| Organization | Multiple autonomous teams |

**Pros:**
- ✅ Independent deployment & scaling
- ✅ Technology diversity
- ✅ Team autonomy
- ✅ Fault isolation

**Cons:**
- ❌ Operational complexity (many services)
- ❌ Network latency & failures
- ❌ Distributed transactions hard
- ❌ Testing complexity
- ❌ Data consistency challenges

---

### 8. CQRS (Command Query Responsibility Segregation)

**Overview:** Separate read (query) and write (command) models.

**When to Use:**

| Criteria | Recommendation |
|----------|---------------|
| Read/Write Ratio | Very different (1000:1 reads) |
| Query Complexity | Complex reporting needs |
| Scalability Needs | Need to scale reads independently |
| Event Sourcing | Often combined with CQRS |

**Pros:**
- ✅ Optimized read models (denormalized)
- ✅ Scale reads/writes independently
- ✅ Flexible query patterns

**Cons:**
- ❌ Eventual consistency
- ❌ Data duplication
- ❌ Increased complexity

---

## Pattern Decision Matrix

Use this matrix to select the most appropriate pattern for your project.

| Factor | Clean Arch | DDD | VSA | Hexagonal | Modular Mono | MVC | Microservices |
|--------|-----------|-----|-----|-----------|--------------|-----|---------------|
| **Team Size** | 5-20 | 10-50 | 2-10 | 3-15 | 5-30 | 1-10 | 20-100+ |
| **Project Size** | 50k-500k | 100k+ | <100k | 30k-150k | 50k-500k | <50k | 500k+ |
| **Domain Complexity** | High | Very High | Low-Med | Med-High | Med-High | Low | High |
| **Learning Curve** | Steep | Very Steep | Gentle | Medium | Medium | Gentle | Very Steep |
| **Boilerplate** | High | Very High | Low | High | Medium | Low | Medium |
| **Testability** | Excellent | Excellent | Good | Excellent | Good | Fair | Good |
| **Framework Independence** | Yes | Yes | No | Yes | Partial | No | Yes |
| **Best For** | Long-term apps | Complex domains | CRUD apps | Multi-integration | Growing teams | Simple apps | Large orgs |

### Selection Guide

**Start with Simple Domain (<10k LOC, 1-3 developers):**
→ MVC or Simple Layered Architecture

**Growing Project (10k-50k LOC, 3-5 developers):**
→ VSA (if feature-focused) or Layered Architecture

**Medium Complexity (50k-100k LOC, 5-10 developers):**
→ Clean Architecture or Hexagonal

**High Complexity Domain (100k+ LOC, 10+ developers):**
→ DDD with Bounded Contexts or Modular Monolith

**Need Independent Deployment (20+ developers, multiple teams):**
→ Microservices

**Complex Integrations:**
→ Hexagonal Architecture

**Event-Driven Requirements:**
→ Event-Driven + CQRS (can combine with Clean/DDD/Hexagonal)

---

## Migration Paths

### Evolution Ladder

```
MVC / Simple Layered
    ↓
Layered Architecture (3-tier)
    ↓
Clean Architecture / Hexagonal
    ↓
Modular Monolith
    ↓
Microservices
```

### Common Migrations

#### 1. MVC → Clean Architecture

**Why:** Need better testability and framework independence

**Steps:**
1. Extract business logic from controllers into use cases
2. Create domain entities with behavior
3. Define repository interfaces
4. Move framework-specific code to infrastructure layer
5. Implement dependency inversion

**Effort:** 2-4 weeks for typical app

#### 2. Layered → Modular Monolith

**Why:** Growing team needs clear module boundaries

**Steps:**
1. Identify logical modules (usually based on business areas)
2. Define public API for each module
3. Refactor to remove cross-module dependencies
4. Enforce module boundaries (e.g., ArchUnit tests)
5. Migrate module by module

**Effort:** 1-3 months depending on size

#### 3. Modular Monolith → Microservices

**Why:** Need independent deployment and scaling

**Steps:**
1. Ensure modules are truly independent (no shared DB tables)
2. Add API layer to each module
3. Extract module to separate service
4. Replace in-process calls with HTTP/gRPC
5. Deploy independently
6. Repeat for each module

**Effort:** 3-12 months depending on coupling

**Risks:**
- Distributed transactions complexity
- Network reliability issues
- Increased operational burden

#### 4. Monolith → VSA (Refactoring)

**Why:** Want feature isolation without microservices complexity

**Steps:**
1. Identify all use cases (commands & queries)
2. Create feature folder for each use case
3. Move related code into feature folder
4. Extract shared code to `shared/`
5. Remove unnecessary abstractions

**Effort:** 1-4 weeks

---

## ADR Examples

### Example 1: Choosing VSA

```markdown
# ADR-005: Adopt Vertical Slice Architecture

## Status
Accepted

## Context

### Background
Our team of 6 developers is building a SaaS application with ~30 distinct features. Currently using MVC pattern with controllers growing to 2000+ lines.

### Problem Statement
- Controllers handle too many responsibilities
- Difficult to work on features in parallel (merge conflicts)
- Testing requires mocking entire service layer
- Onboarding new developers takes 2+ weeks

### Goals
- Enable parallel feature development
- Reduce merge conflicts
- Improve testability
- Faster onboarding

## Decision

Adopt Vertical Slice Architecture, organizing code by feature rather than layer.

## Options Considered

### Option A: Clean Architecture
**Pros:**
- ✅ Clear separation of concerns
- ✅ Highly testable
- ✅ Framework independent

**Cons:**
- ❌ High boilerplate for CRUD features
- ❌ Steep learning curve
- ❌ 4-layer structure overkill for our domain

**Effort:** High

### Option B: Vertical Slice Architecture
**Pros:**
- ✅ Feature isolation (parallel development)
- ✅ Minimal boilerplate
- ✅ Easy to understand
- ✅ Each feature is complete unit

**Cons:**
- ❌ Some code duplication
- ❌ Less guidance on shared concerns

**Effort:** Medium

### Option C: Modular Monolith
**Pros:**
- ✅ Clear boundaries
- ✅ Can scale to larger team

**Cons:**
- ❌ Overkill for current size
- ❌ More structure than needed

**Effort:** High

## Consequences

### Positive
- Features can be developed independently
- New developers can focus on one slice
- Reduced merge conflicts
- Easier to delete dead features

### Negative
- Validation logic duplicated across slices
- Need conventions for cross-cutting concerns

### Risks
- **Risk:** Team may create inconsistent slice structures
  - **Mitigation:** Create slice template generator, conduct code reviews
- **Risk:** Shared code scattered across slices
  - **Mitigation:** Establish `shared/` folder for genuinely shared code

## Implementation Plan

### Phase 1: Template & Guidelines (Week 1)
- Create feature slice template
- Document shared vs. feature-specific criteria
- Set up linting rules

### Phase 2: Migrate High-Churn Features (Weeks 2-4)
- Migrate user authentication
- Migrate billing
- Migrate notifications

### Phase 3: New Features (Week 5+)
- All new features use VSA
- Gradually migrate remaining features

### Rollback Strategy
If VSA proves problematic, slices can be reorganized back to layered structure with minimal effort (all code remains, just directory structure changes).

## Metrics

- Merge conflicts reduced by 60%
- Feature development time reduced by 30%
- Onboarding time reduced to <1 week

## References
- https://www.jimmybogard.com/vertical-slice-architecture/
- ADR-003: CQRS Decision

## Notes
Consider combining with MediatR for command/query handling.

---
**Author:** Jane Doe
**Date:** 2026-01-15
**Reviewers:** John Smith, Alice Johnson
**Approved By:** Bob CTO
```

---

**Last Updated:** 2026-02-20
**Version:** 1.0.0
