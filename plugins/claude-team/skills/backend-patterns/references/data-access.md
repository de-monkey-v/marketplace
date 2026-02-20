# Data Access Patterns

쿼리 최적화, N+1 문제 해결, 안전한 마이그레이션 등 데이터 액세스 계층의 핵심 패턴들입니다.

## Table of Contents

- [N+1 Query Problem](#n1-query-problem)
- [Query Optimization Patterns](#query-optimization-patterns)
- [Index Strategy](#index-strategy)
- [Connection Pool Management](#connection-pool-management)
- [Migration Patterns](#migration-patterns)
- [ORM-Specific Patterns](#orm-specific-patterns)
- [Caching Strategies](#caching-strategies)
- [Monitoring Queries](#monitoring-queries)

## N+1 Query Problem

N+1 문제는 가장 흔한 성능 문제 중 하나입니다. 1개의 쿼리로 N개의 레코드를 조회한 후, 각 레코드마다 추가 쿼리를 실행하여 총 N+1개의 쿼리가 발생하는 현상입니다.

### Problem Example

```typescript
// BAD: N+1 queries
const users = await userRepo.findAll(); // 1 query: SELECT * FROM users

for (const user of users) {
  // N queries: SELECT * FROM orders WHERE user_id = ?
  user.orders = await orderRepo.findByUser(user.id);
}

// Result: 1 + N queries (if 100 users, 101 queries!)
```

### Solution 1: Eager Loading (JOIN)

```typescript
// GOOD: Eager loading with JOIN
const users = await userRepo.findAll({
  relations: ['orders']  // 1 query with JOIN
});

// Generated SQL:
// SELECT u.*, o.*
// FROM users u
// LEFT JOIN orders o ON o.user_id = u.id
```

**TypeORM:**
```typescript
const users = await userRepository.find({
  relations: ['orders', 'orders.items']
});
```

**Prisma:**
```typescript
const users = await prisma.user.findMany({
  include: {
    orders: {
      include: {
        items: true
      }
    }
  }
});
```

**SQLAlchemy:**
```python
users = session.query(User).options(
    joinedload(User.orders).joinedload(Order.items)
).all()
```

### Solution 2: Batch Loading

JOIN이 비효율적인 경우 (너무 많은 관계, 카테시안 곱 문제) 배치 로딩을 사용합니다.

```typescript
// GOOD: Batch loading
const users = await userRepo.findAll(); // 1 query

// 2nd query: SELECT * FROM orders WHERE user_id IN (?, ?, ...)
const userIds = users.map(u => u.id);
const allOrders = await orderRepo.findByUserIds(userIds);

// Group orders by user ID
const ordersByUser = new Map<string, Order[]>();
for (const order of allOrders) {
  if (!ordersByUser.has(order.userId)) {
    ordersByUser.set(order.userId, []);
  }
  ordersByUser.get(order.userId)!.push(order);
}

// Attach orders to users
users.forEach(u => {
  u.orders = ordersByUser.get(u.id) || [];
});

// Result: 2 queries instead of N+1
```

**DataLoader pattern (GraphQL common):**
```typescript
const orderLoader = new DataLoader(async (userIds: string[]) => {
  const orders = await orderRepo.findByUserIds(userIds);

  const ordersByUser = new Map<string, Order[]>();
  for (const order of orders) {
    if (!ordersByUser.has(order.userId)) {
      ordersByUser.set(order.userId, []);
    }
    ordersByUser.get(order.userId)!.push(order);
  }

  return userIds.map(id => ordersByUser.get(id) || []);
});

// Usage
for (const user of users) {
  user.orders = await orderLoader.load(user.id);
}
```

### Solution 3: Select Subquery

단일 값을 가져올 때는 서브쿼리가 효율적입니다.

```typescript
// Get order count for each user
const users = await userRepository
  .createQueryBuilder('user')
  .loadRelationCountAndMap('user.orderCount', 'user.orders')
  .getMany();

// Generated SQL:
// SELECT u.*,
//   (SELECT COUNT(*) FROM orders WHERE user_id = u.id) as orderCount
// FROM users u
```

### Detection Checklist

N+1 문제를 찾는 체크리스트:

- [ ] 루프 안에서 데이터베이스 쿼리 실행
- [ ] ORM lazy loading이 기본 설정
- [ ] 쿼리 로그에서 동일한 패턴의 쿼리가 반복
- [ ] API 응답 시간이 데이터 개수에 비례하여 증가
- [ ] 데이터베이스 커넥션 풀이 빠르게 소진

## Query Optimization Patterns

### 1. Indexing Strategy

| Pattern | When | How |
|---------|------|-----|
| **Single Column Index** | Frequent WHERE/ORDER BY on one column | `CREATE INDEX idx_user_email ON users(email)` |
| **Composite Index** | Multi-column WHERE/ORDER BY | `CREATE INDEX idx_order_user_date ON orders(user_id, created_at)` |
| **Covering Index** | SELECT uses only indexed columns | `CREATE INDEX idx_user_lookup ON users(email) INCLUDE (name, status)` |
| **Partial Index** | Filtered queries | `CREATE INDEX idx_active_users ON users(email) WHERE status = 'active'` |
| **Full-Text Index** | Text search | `CREATE FULLTEXT INDEX idx_product_search ON products(name, description)` |

### 2. Query Patterns

#### Pagination

```typescript
// BAD: OFFSET is slow for large offsets
const users = await userRepo.find({
  skip: 10000,  // Scans 10000 rows
  take: 20
});

// GOOD: Cursor-based pagination
const users = await userRepo.find({
  where: {
    id: MoreThan(lastSeenId)
  },
  take: 20,
  order: { id: 'ASC' }
});

// Generated SQL:
// SELECT * FROM users
// WHERE id > ?
// ORDER BY id ASC
// LIMIT 20
```

#### Count Queries

```typescript
// BAD: COUNT(*) on large tables
const total = await userRepo.count();

// GOOD: Use cached count or estimate
const total = await this.cache.get('user_count') ??
  await userRepo.count();

// Or use EXPLAIN for estimate (PostgreSQL)
const estimate = await this.db.query(
  "SELECT reltuples::bigint FROM pg_class WHERE relname = 'users'"
);
```

#### Exists Checks

```typescript
// BAD: Load entire record just to check existence
const user = await userRepo.findOne({ where: { email } });
if (user) {
  throw new ConflictException('Email already exists');
}

// GOOD: Use EXISTS query
const exists = await userRepo.exist({ where: { email } });
if (exists) {
  throw new ConflictException('Email already exists');
}

// Or COUNT with LIMIT 1
const count = await userRepo
  .createQueryBuilder()
  .where({ email })
  .limit(1)
  .getCount();
```

### 3. Query Plan Analysis

모든 슬로우 쿼리는 EXPLAIN ANALYZE로 분석합니다.

```sql
EXPLAIN ANALYZE
SELECT u.*, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.status = 'active'
GROUP BY u.id
ORDER BY order_count DESC
LIMIT 10;
```

**주요 확인 사항:**

| 항목 | 좋음 | 나쁨 |
|------|------|------|
| **Scan Type** | Index Scan, Index Only Scan | Seq Scan on large table |
| **Rows** | Actual rows ≈ Estimated rows | Large discrepancy |
| **Execution Time** | < 100ms | > 1000ms |
| **Buffers** | Shared hits > reads | Many shared reads |

## Index Strategy

### Index Strategy Checklist

효율적인 인덱스 전략을 위한 체크리스트:

- [ ] **Primary key index** (자동 생성됨)
- [ ] **Foreign key columns** indexed
- [ ] **Frequently filtered columns** (WHERE clause) indexed
- [ ] **Frequently sorted columns** (ORDER BY) indexed
- [ ] **Composite index** for multi-column WHERE
- [ ] **Avoid over-indexing** (write performance 저하)
- [ ] **Review unused indexes** periodically
- [ ] **Monitor index usage** statistics

### Composite Index Column Order

컴포지트 인덱스의 컬럼 순서가 중요합니다.

```sql
-- Index: (user_id, created_at, status)
CREATE INDEX idx_orders_composite ON orders(user_id, created_at, status);

-- ✅ Uses index (leftmost prefix)
SELECT * FROM orders WHERE user_id = 123;
SELECT * FROM orders WHERE user_id = 123 AND created_at > '2024-01-01';
SELECT * FROM orders WHERE user_id = 123 AND created_at > '2024-01-01' AND status = 'completed';

-- ❌ Does NOT use index (missing leftmost column)
SELECT * FROM orders WHERE created_at > '2024-01-01';
SELECT * FROM orders WHERE status = 'completed';
```

**Best practice**: 가장 선택적인(selective) 컬럼을 앞에 배치

```sql
-- GOOD: user_id is selective (many unique values)
CREATE INDEX idx_orders ON orders(user_id, status);

-- BAD: status has few distinct values (not selective)
CREATE INDEX idx_orders_bad ON orders(status, user_id);
```

### Covering Index

SELECT하는 모든 컬럼이 인덱스에 포함되면 테이블 액세스가 불필요합니다.

```sql
-- Query
SELECT user_id, created_at, status
FROM orders
WHERE user_id = 123
ORDER BY created_at DESC;

-- Covering index (includes all selected columns)
CREATE INDEX idx_orders_covering ON orders(user_id, created_at, status);

-- PostgreSQL INCLUDE syntax
CREATE INDEX idx_orders_covering ON orders(user_id, created_at) INCLUDE (status);
```

### Partial Index

조건부 인덱스는 특정 쿼리에 최적화됩니다.

```sql
-- Only index active users
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- Query uses partial index
SELECT * FROM users WHERE email = 'test@example.com' AND status = 'active';
```

### Index Maintenance

```sql
-- Find unused indexes (PostgreSQL)
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE '%pkey'
ORDER BY schemaname, tablename;

-- Find duplicate indexes
SELECT pg_size_pretty(SUM(pg_relation_size(idx))::BIGINT) AS size,
       (array_agg(idx))[1] AS idx1,
       (array_agg(idx))[2] AS idx2
FROM (
  SELECT indexrelid::regclass AS idx, indrelid, indkey::text
  FROM pg_index
) sub
GROUP BY indrelid, indkey
HAVING COUNT(*) > 1;

-- Rebuild bloated index
REINDEX INDEX CONCURRENTLY idx_name;
```

## Connection Pool Management

커넥션 풀은 데이터베이스 성능의 핵심입니다.

### Pool Configuration

| Parameter | Typical Value | Notes |
|-----------|--------------|-------|
| **Min Connections** | 2-5 | Keep alive during idle |
| **Max Connections** | 10-20 per instance | Don't exceed DB max_connections |
| **Connection Timeout** | 5s | Fail fast if no connection available |
| **Idle Timeout** | 30s | Release unused connections |
| **Max Lifetime** | 30m | Prevent stale connections |
| **Acquire Timeout** | 30s | How long to wait for connection |
| **Validation Query** | `SELECT 1` | Test connection health |

### TypeORM Configuration

```typescript
{
  type: 'postgres',
  host: 'localhost',
  port: 5432,
  database: 'myapp',
  extra: {
    // Connection pool config
    max: 20,                    // Maximum connections
    min: 2,                     // Minimum connections
    idleTimeoutMillis: 30000,   // Close idle connections after 30s
    connectionTimeoutMillis: 5000,  // Fail after 5s if no connection
    maxUses: 7500,              // Max queries per connection before refresh
  }
}
```

### Prisma Configuration

```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// Connection string
// postgresql://user:password@localhost:5432/mydb?connection_limit=20&pool_timeout=5
```

### Monitoring Connection Pool

```typescript
// TypeORM
const pool = dataSource.driver.pool;
console.log({
  totalCount: pool.totalCount,
  idleCount: pool.idleCount,
  waitingCount: pool.waitingCount
});

// Prisma
const metrics = await prisma.$metrics.json();
console.log(metrics.counters);
```

### Common Pool Issues

| Problem | Symptom | Solution |
|---------|---------|----------|
| **Connection leak** | Pool exhausted, timeout errors | Ensure connections are released (use try-finally) |
| **Pool too small** | High acquire wait time | Increase max connections |
| **Pool too large** | Database overload | Decrease max connections |
| **Long-running queries** | Connections held too long | Set statement_timeout, optimize queries |
| **Connection churn** | Frequent connect/disconnect | Increase min connections, idle timeout |

## Migration Patterns

### Safe Migration Checklist

모든 마이그레이션은 다음을 확인해야 합니다:

- [ ] **Backward compatible**: 이전 버전 코드와 호환
- [ ] **No data loss**: 데이터 손실 없음
- [ ] **Rollback plan**: 롤백 가능
- [ ] **Tested on staging**: 프로덕션과 유사한 환경에서 테스트
- [ ] **Execution time estimated**: 실행 시간 예측 (대용량 테이블 주의)
- [ ] **No downtime**: 무중단 배포 가능

### Zero-Downtime Migration Pattern

큰 변경은 여러 단계로 나눕니다.

#### Example: Rename Column

```sql
-- ❌ WRONG: Direct rename causes downtime
ALTER TABLE users RENAME COLUMN email TO email_address;

-- ✅ RIGHT: Multi-step migration

-- Step 1: Add new column (nullable, no default)
ALTER TABLE users ADD COLUMN email_address VARCHAR(255);

-- Step 2: Backfill data (batched)
-- Run in background job, not in migration
UPDATE users SET email_address = email WHERE email_address IS NULL;

-- Step 3: Deploy code using BOTH columns
-- Code reads email_address, falls back to email
-- Code writes to BOTH columns

-- Step 4: After deployment, verify data
SELECT COUNT(*) FROM users WHERE email_address IS NULL; -- should be 0

-- Step 5: Add NOT NULL constraint
ALTER TABLE users ALTER COLUMN email_address SET NOT NULL;

-- Step 6: Deploy code using only email_address

-- Step 7: Drop old column
ALTER TABLE users DROP COLUMN email;
```

#### Example: Add NOT NULL Column

```sql
-- ❌ WRONG: Breaks running code
ALTER TABLE orders ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending';

-- ✅ RIGHT: Multi-step

-- Step 1: Add nullable column
ALTER TABLE orders ADD COLUMN status VARCHAR(20);

-- Step 2: Backfill with default value
UPDATE orders SET status = 'pending' WHERE status IS NULL;

-- Step 3: Add NOT NULL constraint
ALTER TABLE orders ALTER COLUMN status SET NOT NULL;

-- Step 4: Add default for future inserts
ALTER TABLE orders ALTER COLUMN status SET DEFAULT 'pending';
```

### Large Table Migration

대용량 테이블 변경 시 테이블 락을 피하는 전략:

#### Online DDL Tools

| Database | Tool | How |
|----------|------|-----|
| **MySQL** | pt-online-schema-change | Percona Toolkit |
| **MySQL** | gh-ost | GitHub's online schema migration |
| **PostgreSQL** | Built-in | Most DDL is non-blocking |

#### Batched Data Migration

```typescript
// Backfill large table in batches
async function backfillEmailAddress() {
  let processed = 0;
  const batchSize = 1000;

  while (true) {
    const result = await db.query(`
      UPDATE users
      SET email_address = email
      WHERE email_address IS NULL
        AND id IN (
          SELECT id FROM users
          WHERE email_address IS NULL
          LIMIT ${batchSize}
        )
    `);

    processed += result.affectedRows;

    if (result.affectedRows === 0) {
      break; // Done
    }

    // Sleep to avoid overloading database
    await sleep(100);
  }

  console.log(`Backfilled ${processed} rows`);
}
```

### Migration Anti-Patterns

| Anti-Pattern | Risk | Solution |
|--------------|------|----------|
| **Direct column rename** | Downtime, code breaks | Add new → copy → drop old |
| **NOT NULL without default** | Breaks running inserts | Add nullable → backfill → add constraint |
| **Large table ALTER** | Lock table for minutes | Use online DDL tools |
| **Data migration in schema migration** | Mixed concerns, hard to rollback | Separate schema and data migrations |
| **No rollback plan** | Can't revert if fails | Always write DOWN migration |
| **Running on production first** | Risk of data loss | Test on staging with prod-like data |

### Migration Frameworks

| Framework | Language | Database | Features |
|-----------|----------|----------|----------|
| **Flyway** | Java/Any | All | Versioned migrations, checksums |
| **Liquibase** | Java/Any | All | XML/YAML/SQL, rollback |
| **Alembic** | Python | SQLAlchemy | Autogenerate, branching |
| **TypeORM** | TypeScript | All | Autogenerate, CLI |
| **Prisma Migrate** | TypeScript | All | Shadow DB, dev mode |
| **golang-migrate** | Go | All | CLI, library |

## ORM-Specific Patterns

### TypeORM

```typescript
// Eager loading
const users = await userRepository.find({
  relations: ['orders', 'orders.items']
});

// Query builder
const users = await userRepository
  .createQueryBuilder('user')
  .leftJoinAndSelect('user.orders', 'order')
  .where('user.status = :status', { status: 'active' })
  .orderBy('user.createdAt', 'DESC')
  .getMany();

// Batch loading (select in load)
const users = await userRepository.find({
  relations: ['orders'],
  relationLoadStrategy: 'query' // Separate query instead of JOIN
});

// Transaction
await dataSource.transaction(async (manager) => {
  await manager.save(User, user);
  await manager.save(Order, order);
});
```

### Prisma

```typescript
// Eager loading
const users = await prisma.user.findMany({
  include: {
    orders: {
      include: {
        items: true
      }
    }
  }
});

// Filtering
const users = await prisma.user.findMany({
  where: {
    status: 'active',
    orders: {
      some: {
        total: { gte: 100 }
      }
    }
  }
});

// Transaction
await prisma.$transaction([
  prisma.user.create({ data: userData }),
  prisma.order.create({ data: orderData })
]);

// Interactive transaction
await prisma.$transaction(async (tx) => {
  const user = await tx.user.create({ data: userData });
  const order = await tx.order.create({
    data: { ...orderData, userId: user.id }
  });
  return order;
});
```

### SQLAlchemy (Python)

```python
# Eager loading
users = session.query(User).options(
    joinedload(User.orders).joinedload(Order.items)
).all()

# Select in load (separate query)
users = session.query(User).options(
    selectinload(User.orders)
).all()

# Filtering
users = session.query(User).filter(
    User.status == 'active',
    User.orders.any(Order.total >= 100)
).all()

# Transaction
with session.begin():
    session.add(user)
    session.add(order)
    # Commits on success, rolls back on exception
```

### JPA/Hibernate (Java)

```java
// Eager loading
@Entity
public class User {
    @OneToMany(fetch = FetchType.EAGER)
    private List<Order> orders;
}

// Or use JOIN FETCH in query
List<User> users = em.createQuery(
    "SELECT u FROM User u JOIN FETCH u.orders",
    User.class
).getResultList();

// Batch loading
@BatchSize(size = 10)
@OneToMany
private List<Order> orders;

// Transaction
@Transactional
public void createOrder(OrderDto dto) {
    User user = userRepo.findById(dto.getUserId());
    Order order = new Order(dto);
    orderRepo.save(order);
}
```

### GORM (Go)

```go
// Eager loading
var users []User
db.Preload("Orders").Preload("Orders.Items").Find(&users)

// Filtering
db.Where("status = ?", "active").
   Joins("JOIN orders ON orders.user_id = users.id").
   Find(&users)

// Transaction
db.Transaction(func(tx *gorm.DB) error {
    if err := tx.Create(&user).Error; err != nil {
        return err
    }
    if err := tx.Create(&order).Error; err != nil {
        return err
    }
    return nil
})
```

## Caching Strategies

### Cache Patterns

| Strategy | Pattern | Use Case | Pros | Cons |
|----------|---------|----------|------|------|
| **Cache-Aside** | App manages cache | General purpose | Simple, cache failures don't break app | Cache misses are slow |
| **Write-Through** | Cache updated on write | Consistency critical | Always fresh data | Write latency |
| **Write-Behind** | Cache writes async | Write-heavy workloads | Fast writes | Eventual consistency |
| **Read-Through** | Cache loads on miss | Read-heavy workloads | Transparent to app | Complex setup |
| **TTL-Based** | Expire after time | Simple invalidation | Easy to implement | May serve stale data |

### Cache-Aside Pattern

```typescript
async function getUser(id: string): Promise<User> {
  // 1. Try cache
  const cached = await cache.get(`user:${id}`);
  if (cached) {
    return JSON.parse(cached);
  }

  // 2. Cache miss - load from DB
  const user = await userRepo.findById(id);
  if (!user) {
    throw new NotFoundException('User', id);
  }

  // 3. Store in cache
  await cache.set(`user:${id}`, JSON.stringify(user), {
    ttl: 300 // 5 minutes
  });

  return user;
}

async function updateUser(id: string, data: UpdateUserDto): Promise<User> {
  const user = await userRepo.update(id, data);

  // Invalidate cache
  await cache.del(`user:${id}`);

  return user;
}
```

### Cache Invalidation Patterns

```typescript
// 1. Time-based (TTL)
await cache.set(key, value, { ttl: 300 });

// 2. Event-based (on update)
eventBus.on('user.updated', async (event) => {
  await cache.del(`user:${event.userId}`);
});

// 3. Tag-based (invalidate related)
await cache.set(`user:${id}`, user, {
  tags: [`user:${id}`, `org:${user.orgId}`]
});

// Invalidate all users in org
await cache.invalidateTags([`org:${orgId}`]);
```

### Query Result Caching

```typescript
// Cache expensive query results
async function getTopProducts(limit: number): Promise<Product[]> {
  const cacheKey = `top-products:${limit}`;

  return cache.wrap(cacheKey, async () => {
    // Expensive query
    return productRepo
      .createQueryBuilder('product')
      .leftJoin('product.orders', 'order')
      .groupBy('product.id')
      .orderBy('COUNT(order.id)', 'DESC')
      .limit(limit)
      .getMany();
  }, {
    ttl: 3600 // 1 hour
  });
}
```

## Monitoring Queries

### Slow Query Logging

#### PostgreSQL

```sql
-- Enable slow query log
ALTER SYSTEM SET log_min_duration_statement = 1000; -- Log queries > 1s
SELECT pg_reload_conf();

-- View slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

#### MySQL

```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1; -- Log queries > 1s

-- View slow queries
SELECT * FROM mysql.slow_log
ORDER BY query_time DESC
LIMIT 10;
```

### Application-Level Monitoring

```typescript
// Log slow queries in TypeORM
{
  type: 'postgres',
  logging: true,
  maxQueryExecutionTime: 1000, // Warn if query > 1s
  logger: new CustomQueryLogger()
}

class CustomQueryLogger implements Logger {
  logQuery(query: string, parameters?: any[], queryRunner?: QueryRunner) {
    const start = Date.now();

    return () => {
      const duration = Date.now() - start;
      if (duration > 1000) {
        console.warn(`Slow query (${duration}ms):`, query, parameters);
      }
    };
  }
}
```

### Metrics to Track

| Metric | What | Alert If |
|--------|------|----------|
| **Query Duration** | Time to execute | p95 > 1s |
| **Connection Pool Usage** | Active / Max | Usage > 80% |
| **Query Errors** | Failed queries | Error rate > 1% |
| **Deadlocks** | Transaction conflicts | > 0 per minute |
| **Cache Hit Rate** | Cache effectiveness | < 90% |
| **Slow Query Count** | Queries > threshold | > 10 per minute |

### Monitoring Tools

- **Application**: New Relic, Datadog, Sentry
- **Database**: pgBadger (PostgreSQL), pt-query-digest (MySQL)
- **Metrics**: Prometheus + Grafana
- **APM**: Elastic APM, Dynatrace

---

**Best Practice Summary**:

1. **Always prevent N+1**: Use eager loading or batch loading
2. **Index strategically**: WHERE, JOIN, ORDER BY columns
3. **Analyze slow queries**: Use EXPLAIN ANALYZE
4. **Configure connection pool**: Match workload and DB limits
5. **Migrate safely**: Backward compatible, test on staging
6. **Cache intelligently**: Cache-aside for reads, invalidate on writes
7. **Monitor continuously**: Track slow queries, pool usage, errors
