---
name: backend-patterns
description: "백엔드 패턴 레퍼런스. 서비스/리포지토리/트랜잭션 패턴, 쿼리 최적화, N+1 방지, 마이그레이션 전략을 제공합니다."
version: 1.0.0
---

# Backend Patterns Reference

백엔드 개발을 위한 전문 레퍼런스 스킬입니다. 서비스 계층, 리포지토리 패턴, 트랜잭션 관리, 쿼리 최적화, 마이그레이션 전략 등 백엔드 개발의 핵심 패턴을 제공합니다.

## Overview

이 스킬은 백엔드 애플리케이션 개발 시 필요한 아키텍처 패턴과 데이터 액세스 전략을 제공합니다. 도메인 로직과 인프라 관심사를 분리하고, 성능과 유지보수성을 동시에 확보하는 방법을 안내합니다.

### Use Cases

- **서비스 계층 설계**: 비즈니스 로직을 HTTP/프레임워크 관심사와 분리
- **리포지토리 패턴**: 데이터 액세스 추상화 및 테스트 용이성 확보
- **트랜잭션 관리**: Unit of Work 패턴을 통한 일관성 보장
- **쿼리 최적화**: N+1 문제 방지 및 성능 개선
- **마이그레이션 전략**: 무중단 배포를 위한 안전한 스키마 변경

## Layered Architecture Summary

백엔드 애플리케이션은 일반적으로 다음과 같은 계층으로 구성됩니다:

```
┌─────────────────────────────────────┐
│   Presentation Layer (Controller)   │  ← HTTP, GraphQL, gRPC
├─────────────────────────────────────┤
│   Application Layer (Service)       │  ← Use cases, business logic
├─────────────────────────────────────┤
│   Domain Layer (Entities, VOs)      │  ← Business rules, domain logic
├─────────────────────────────────────┤
│   Infrastructure Layer (Repository) │  ← Database, external services
└─────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Responsibility | Examples |
|-------|---------------|----------|
| **Presentation** | HTTP request/response handling | Controllers, DTOs, validation |
| **Application** | Business logic orchestration | Services, use cases |
| **Domain** | Core business rules | Entities, value objects, domain events |
| **Infrastructure** | External system integration | Repositories, API clients, message queues |

### Dependency Rules

- **Upper layers depend on lower layers** (Presentation → Application → Domain)
- **Domain layer has no dependencies** (pure business logic)
- **Infrastructure depends on Domain** (implements domain interfaces)

## Key Patterns

### 1. Service Layer Pattern

Service는 비즈니스 로직을 캡슐화하고 여러 리포지토리와 외부 서비스를 조율합니다.

**핵심 원칙:**
- HTTP/프레임워크 관심사와 분리
- 트랜잭션 경계 정의
- 도메인 이벤트 발행
- 여러 리포지토리 조율

**When to use:**
- 복잡한 비즈니스 로직이 있을 때
- 여러 엔티티를 조율해야 할 때
- 트랜잭션 경계를 명확히 해야 할 때

### 2. Repository Pattern

Repository는 데이터 액세스를 추상화하고 도메인 중심 쿼리 인터페이스를 제공합니다.

**핵심 원칙:**
- 컬렉션처럼 동작 (add, remove, findById)
- ORM/데이터베이스 구현 세부사항 숨김
- 도메인 언어로 메서드 명명
- 테스트 시 쉽게 모킹 가능

**When to use:**
- 데이터 액세스 로직을 비즈니스 로직과 분리
- 여러 데이터 소스를 추상화
- 테스트 용이성 확보

### 3. Unit of Work Pattern

Unit of Work는 여러 리포지토리의 변경사항을 하나의 트랜잭션으로 묶습니다.

**핵심 원칙:**
- 트랜잭션 경계 명시적 관리
- 여러 리포지토리 작업 조율
- 롤백 자동 처리
- 성공 시에만 커밋

**When to use:**
- 여러 엔티티를 한 트랜잭션에서 수정
- 트랜잭션 경계를 명확히 제어
- 복잡한 비즈니스 로직에서 일관성 보장

### 4. CQRS (Command Query Responsibility Segregation)

읽기와 쓰기 모델을 분리하여 각각 최적화합니다.

**When to use:**
- 읽기와 쓰기의 성능 요구사항이 다를 때
- 복잡한 쿼리 최적화가 필요할 때
- 이벤트 소싱을 적용할 때

### 5. Event-Driven Architecture

도메인 이벤트를 통해 모듈 간 결합도를 낮춥니다.

**When to use:**
- 사이드 이펙트를 비즈니스 로직에서 분리
- 마이크로서비스 간 통신
- 이벤트 소싱 구현

## Reference Files

### service-patterns.md

서비스 계층, 리포지토리, 트랜잭션 관리 패턴을 다룹니다.

**주요 내용:**
- Service Layer Pattern 구현 예제
- Repository Pattern 인터페이스 설계
- Unit of Work 트랜잭션 관리
- Dependency Injection 패턴
- 에러 핸들링 전략
- 이벤트 기반 아키텍처
- 미들웨어/인터셉터 패턴
- 백그라운드 작업 처리
- 안티패턴과 해결책

**Use when:**
- 서비스 계층 아키텍처 설계
- 비즈니스 로직 구조화
- 트랜잭션 전략 수립
- 이벤트 기반 설계

### data-access.md

데이터 액세스 최적화와 마이그레이션 전략을 다룹니다.

**주요 내용:**
- N+1 쿼리 문제와 해결책
- 쿼리 최적화 전략
- 인덱스 설계 가이드
- 커넥션 풀 관리
- 안전한 마이그레이션 패턴
- 무중단 스키마 변경
- ORM별 최적화 기법
- 캐싱 전략
- 쿼리 모니터링

**Use when:**
- 쿼리 성능 문제 해결
- N+1 문제 진단 및 수정
- 데이터베이스 마이그레이션 계획
- 인덱스 전략 수립
- 커넥션 풀 튜닝

## Related Agents

이 스킬은 다음 에이전트들과 함께 사용할 수 있습니다:

### Backend Framework Specialists
- **backend**: 범용 백엔드 개발 전문가
- **fastapi-expert**: FastAPI/Python 백엔드 전문가
- **nestjs-expert**: NestJS/TypeScript 백엔드 전문가
- **spring-expert**: Spring Boot/Java 백엔드 전문가
- **nextjs-expert**: Next.js API 라우트 및 서버 컴포넌트
- **nuxt-expert**: Nuxt.js 서버 미들웨어 및 API

### Data & Domain Specialists
- **db-architect**: 데이터베이스 스키마 설계 및 최적화
- **domain-modeler**: 도메인 모델링 및 DDD 설계
- **event-architect**: 이벤트 기반 아키텍처 설계

### Testing & Migration Specialists
- **integration-tester**: 통합 테스트 및 E2E 테스트
- **migration-strategist**: 데이터베이스 마이그레이션 전략
- **ddd-strategist**: 도메인 주도 설계 전략

## Framework-Specific Patterns

### NestJS (TypeScript)
```typescript
@Injectable()
class OrderService {
  constructor(
    private orderRepo: OrderRepository,
    private paymentService: PaymentService,
    private eventEmitter: EventEmitter2
  ) {}

  @Transactional()
  async createOrder(dto: CreateOrderDto): Promise<Order> {
    // Business logic
    this.eventEmitter.emit('order.created', order);
    return order;
  }
}
```

### Spring Boot (Java)
```java
@Service
@Transactional
public class OrderService {
    private final OrderRepository orderRepo;
    private final PaymentService paymentService;
    private final ApplicationEventPublisher eventPublisher;

    public Order createOrder(CreateOrderDto dto) {
        // Business logic
        eventPublisher.publishEvent(new OrderCreatedEvent(order));
        return order;
    }
}
```

### FastAPI (Python)
```python
class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        payment_service: PaymentService,
        event_bus: EventBus
    ):
        self.order_repo = order_repo
        self.payment_service = payment_service
        self.event_bus = event_bus

    async def create_order(self, dto: CreateOrderDto) -> Order:
        # Business logic
        await self.event_bus.emit(OrderCreatedEvent(order))
        return order
```

## Best Practices

### Service Layer
1. **Single Responsibility**: 하나의 서비스는 하나의 도메인 영역만 담당
2. **No HTTP Concerns**: 서비스는 HTTP 요청/응답을 직접 다루지 않음
3. **Transaction Boundaries**: 서비스 메서드가 트랜잭션 경계
4. **Event Emission**: 사이드 이펙트는 이벤트로 분리

### Repository Layer
1. **Domain Language**: 도메인 용어로 메서드 명명 (findActiveOrders)
2. **Interface Segregation**: 필요한 메서드만 노출
3. **No Business Logic**: 순수한 데이터 액세스만 담당
4. **Return Domain Objects**: DTO가 아닌 도메인 엔티티 반환

### Data Access
1. **Eager Loading**: N+1 문제 방지를 위해 관계 미리 로드
2. **Index Strategy**: WHERE, JOIN, ORDER BY 컬럼에 인덱스
3. **Connection Pooling**: 적절한 풀 사이즈 설정
4. **Query Monitoring**: 슬로우 쿼리 로그 활성화

### Migration
1. **Backward Compatible**: 이전 버전 코드와 호환되는 변경
2. **Incremental Changes**: 큰 변경은 여러 단계로 분할
3. **Rollback Plan**: 롤백 가능한 마이그레이션 설계
4. **Test on Staging**: 프로덕션 데이터와 유사한 환경에서 테스트

## Common Pitfalls

### Anemic Domain Model
**Problem**: 도메인 객체가 데이터만 담고 로직은 서비스에 집중
**Solution**: Rich domain model - 도메인 객체에 비즈니스 로직 배치

### God Service
**Problem**: 하나의 서비스가 너무 많은 책임을 가짐
**Solution**: 도메인별로 서비스 분리, 단일 책임 원칙 준수

### N+1 Query
**Problem**: 루프 안에서 개별 쿼리 실행
**Solution**: Eager loading, batch loading, join fetch

### Transaction Per Operation
**Problem**: 작은 단위로 트랜잭션을 나눠 데이터 불일치
**Solution**: Unit of Work 패턴으로 논리적 작업 단위를 하나의 트랜잭션으로

### Synchronous Event Handling
**Problem**: 이벤트 핸들러가 동기적으로 실행되어 실패 전파
**Solution**: 비동기 이벤트 버스, 메시지 큐 활용

## Quick Reference

### Service Layer Checklist
- [ ] HTTP/프레임워크 의존성 없음
- [ ] 트랜잭션 경계 명확히 정의
- [ ] 도메인 이벤트 발행
- [ ] 단일 책임 원칙 준수
- [ ] 테스트 용이성 확보

### Repository Checklist
- [ ] 인터페이스 기반 설계
- [ ] 도메인 언어로 메서드 명명
- [ ] 비즈니스 로직 없음
- [ ] 쿼리 최적화 (N+1 방지)
- [ ] 테스트 더블 제공

### Query Optimization Checklist
- [ ] N+1 쿼리 문제 확인
- [ ] 적절한 인덱스 설계
- [ ] 쿼리 플랜 분석 (EXPLAIN)
- [ ] 커넥션 풀 설정 최적화
- [ ] 슬로우 쿼리 모니터링

### Migration Checklist
- [ ] 백워드 호환성 확보
- [ ] 롤백 계획 수립
- [ ] 스테이징 환경 테스트
- [ ] 실행 시간 예측
- [ ] 데이터 백업 완료

## Additional Resources

### Books
- **"Patterns of Enterprise Application Architecture"** by Martin Fowler
- **"Domain-Driven Design"** by Eric Evans
- **"Implementing Domain-Driven Design"** by Vaughn Vernon

### Online Resources
- Martin Fowler's Enterprise Patterns: https://martinfowler.com/eaaCatalog/
- Microsoft's .NET Microservices Architecture: https://docs.microsoft.com/en-us/dotnet/architecture/microservices/
- Database Migration Best Practices

### Tools
- **Migration**: Flyway, Liquibase, Alembic, TypeORM Migrations, Prisma Migrate
- **ORM**: TypeORM, Prisma, SQLAlchemy, JPA/Hibernate, GORM
- **Query Analysis**: EXPLAIN ANALYZE, Database profilers
- **Monitoring**: New Relic, Datadog, Prometheus + Grafana

---

**Version**: 1.0.0
**Last Updated**: 2026-02-20
**Maintainer**: Backend Patterns Working Group
