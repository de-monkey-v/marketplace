# Service Layer Patterns

서비스 계층, 리포지토리, 트랜잭션 관리 등 백엔드 비즈니스 로직 구조화를 위한 핵심 패턴들입니다.

## Table of Contents

- [Layered Architecture Patterns](#layered-architecture-patterns)
- [Dependency Injection Patterns](#dependency-injection-patterns)
- [Error Handling Patterns](#error-handling-patterns)
- [Event-Driven Patterns](#event-driven-patterns)
- [Middleware/Interceptor Patterns](#middlewareinterceptor-patterns)
- [Background Job Patterns](#background-job-patterns)
- [Anti-Patterns](#anti-patterns)

## Layered Architecture Patterns

### Service Layer Pattern

Service는 비즈니스 로직을 캡슐화하고 HTTP 관심사와 분리합니다.

```typescript
// Service handles business logic, not HTTP concerns
@Injectable()
class OrderService {
  constructor(
    private orderRepo: OrderRepository,
    private inventoryRepo: InventoryRepository,
    private paymentService: PaymentService,
    private eventBus: EventBus
  ) {}

  async createOrder(dto: CreateOrderDto): Promise<Order> {
    // 1. Validate business rules
    await this.validateOrderItems(dto.items);

    // 2. Reserve inventory
    const reservations = await this.inventoryRepo.reserve(dto.items);

    // 3. Process payment
    const payment = await this.paymentService.charge({
      amount: this.calculateTotal(dto.items),
      customerId: dto.customerId
    });

    // 4. Create order
    const order = await this.orderRepo.save({
      customerId: dto.customerId,
      items: dto.items,
      paymentId: payment.id,
      status: 'confirmed'
    });

    // 5. Emit domain event
    await this.eventBus.emit('order.created', {
      orderId: order.id,
      customerId: order.customerId
    });

    return order;
  }

  private async validateOrderItems(items: OrderItem[]): Promise<void> {
    if (items.length === 0) {
      throw new ValidationException('Order must have at least one item');
    }

    const availableItems = await this.inventoryRepo.checkAvailability(
      items.map(i => i.productId)
    );

    for (const item of items) {
      const available = availableItems.get(item.productId);
      if (!available || available.stock < item.quantity) {
        throw new OutOfStockException(item.productId);
      }
    }
  }

  private calculateTotal(items: OrderItem[]): number {
    return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  }
}
```

**Controller는 서비스를 호출하고 HTTP 응답만 담당:**

```typescript
@Controller('orders')
class OrderController {
  constructor(private orderService: OrderService) {}

  @Post()
  async createOrder(@Body() dto: CreateOrderDto): Promise<OrderResponse> {
    try {
      const order = await this.orderService.createOrder(dto);
      return { success: true, data: order };
    } catch (error) {
      if (error instanceof ValidationException) {
        throw new BadRequestException(error.message);
      }
      if (error instanceof OutOfStockException) {
        throw new ConflictException(error.message);
      }
      throw error;
    }
  }
}
```

### Repository Pattern

Repository는 데이터 액세스를 추상화하고 도메인 중심 인터페이스를 제공합니다.

```typescript
// Repository abstracts data access
interface OrderRepository {
  // Query methods using domain language
  findById(id: string): Promise<Order | null>;
  findByUser(userId: string, options?: PaginationOptions): Promise<Page<Order>>;
  findPendingOrders(since: Date): Promise<Order[]>;

  // Persistence methods
  save(order: Order): Promise<Order>;
  saveMany(orders: Order[]): Promise<Order[]>;
  delete(id: string): Promise<void>;

  // Business-specific queries
  findOrdersNeedingShipment(): Promise<Order[]>;
  countOrdersByStatus(status: OrderStatus): Promise<number>;
}

// TypeORM implementation
@Injectable()
class TypeORMOrderRepository implements OrderRepository {
  constructor(
    @InjectRepository(OrderEntity)
    private ormRepo: Repository<OrderEntity>
  ) {}

  async findById(id: string): Promise<Order | null> {
    const entity = await this.ormRepo.findOne({
      where: { id },
      relations: ['items', 'customer']
    });
    return entity ? this.toDomain(entity) : null;
  }

  async findByUser(
    userId: string,
    options?: PaginationOptions
  ): Promise<Page<Order>> {
    const [entities, total] = await this.ormRepo.findAndCount({
      where: { customerId: userId },
      relations: ['items'],
      skip: options?.offset ?? 0,
      take: options?.limit ?? 20,
      order: { createdAt: 'DESC' }
    });

    return {
      items: entities.map(e => this.toDomain(e)),
      total,
      hasMore: total > (options?.offset ?? 0) + entities.length
    };
  }

  async save(order: Order): Promise<Order> {
    const entity = this.toEntity(order);
    const saved = await this.ormRepo.save(entity);
    return this.toDomain(saved);
  }

  private toDomain(entity: OrderEntity): Order {
    // Map database entity to domain model
    return new Order({
      id: entity.id,
      customerId: entity.customerId,
      items: entity.items.map(i => new OrderItem(i)),
      status: entity.status,
      createdAt: entity.createdAt
    });
  }

  private toEntity(domain: Order): OrderEntity {
    // Map domain model to database entity
    const entity = new OrderEntity();
    entity.id = domain.id;
    entity.customerId = domain.customerId;
    entity.status = domain.status;
    return entity;
  }
}
```

**Prisma implementation:**

```typescript
@Injectable()
class PrismaOrderRepository implements OrderRepository {
  constructor(private prisma: PrismaService) {}

  async findById(id: string): Promise<Order | null> {
    const order = await this.prisma.order.findUnique({
      where: { id },
      include: { items: true, customer: true }
    });
    return order ? this.toDomain(order) : null;
  }

  async findByUser(
    userId: string,
    options?: PaginationOptions
  ): Promise<Page<Order>> {
    const [orders, total] = await Promise.all([
      this.prisma.order.findMany({
        where: { customerId: userId },
        include: { items: true },
        skip: options?.offset ?? 0,
        take: options?.limit ?? 20,
        orderBy: { createdAt: 'desc' }
      }),
      this.prisma.order.count({ where: { customerId: userId } })
    ]);

    return {
      items: orders.map(o => this.toDomain(o)),
      total,
      hasMore: total > (options?.offset ?? 0) + orders.length
    };
  }

  async save(order: Order): Promise<Order> {
    const saved = await this.prisma.order.upsert({
      where: { id: order.id ?? 'new' },
      create: {
        customerId: order.customerId,
        status: order.status,
        items: {
          create: order.items.map(i => ({
            productId: i.productId,
            quantity: i.quantity,
            price: i.price
          }))
        }
      },
      update: {
        status: order.status
      },
      include: { items: true }
    });
    return this.toDomain(saved);
  }

  private toDomain(prismaOrder: any): Order {
    return new Order({
      id: prismaOrder.id,
      customerId: prismaOrder.customerId,
      items: prismaOrder.items.map((i: any) => new OrderItem(i)),
      status: prismaOrder.status,
      createdAt: prismaOrder.createdAt
    });
  }
}
```

### Unit of Work Pattern

Unit of Work는 여러 리포지토리의 변경사항을 하나의 트랜잭션으로 묶습니다.

```typescript
// Transaction coordination across repositories
interface UnitOfWork {
  execute<T>(work: (tx: Transaction) => Promise<T>): Promise<T>;
}

// TypeORM implementation
@Injectable()
class TypeORMUnitOfWork implements UnitOfWork {
  constructor(private dataSource: DataSource) {}

  async execute<T>(work: (tx: Transaction) => Promise<T>): Promise<T> {
    const queryRunner = this.dataSource.createQueryRunner();
    await queryRunner.connect();
    await queryRunner.startTransaction();

    try {
      const tx = new TypeORMTransaction(queryRunner);
      const result = await work(tx);
      await queryRunner.commitTransaction();
      return result;
    } catch (error) {
      await queryRunner.rollbackTransaction();
      throw error;
    } finally {
      await queryRunner.release();
    }
  }
}

// Transaction interface
interface Transaction {
  orderRepo: OrderRepository;
  inventoryRepo: InventoryRepository;
  paymentRepo: PaymentRepository;
}

// Usage in service
@Injectable()
class OrderService {
  constructor(private uow: UnitOfWork) {}

  async createOrder(dto: CreateOrderDto): Promise<Order> {
    return this.uow.execute(async (tx) => {
      // All operations share the same transaction
      const inventory = await tx.inventoryRepo.reserve(dto.items);
      const payment = await tx.paymentRepo.create({
        amount: this.calculateTotal(dto.items),
        customerId: dto.customerId
      });
      const order = await tx.orderRepo.save({
        customerId: dto.customerId,
        items: dto.items,
        paymentId: payment.id
      });

      // If any operation fails, entire transaction rolls back
      return order;
    });
  }
}
```

**Decorator-based transaction (NestJS):**

```typescript
@Injectable()
class OrderService {
  constructor(
    private orderRepo: OrderRepository,
    private inventoryRepo: InventoryRepository,
    private paymentRepo: PaymentRepository
  ) {}

  @Transactional()  // Decorates method with transaction boundary
  async createOrder(dto: CreateOrderDto): Promise<Order> {
    // All repository calls share the same transaction
    const inventory = await this.inventoryRepo.reserve(dto.items);
    const payment = await this.paymentRepo.create({
      amount: this.calculateTotal(dto.items),
      customerId: dto.customerId
    });
    const order = await this.orderRepo.save({
      customerId: dto.customerId,
      items: dto.items,
      paymentId: payment.id
    });

    return order;
  }
}
```

## Dependency Injection Patterns

| Framework | DI Mechanism | Example |
|-----------|--------------|---------|
| **NestJS** | Decorator-based | `@Injectable()` + constructor injection |
| **Spring** | Annotation-based | `@Service`, `@Autowired` (constructor preferred) |
| **FastAPI** | Function-based | `Depends()` in route parameters |
| **Express** | Manual | Factory functions or IoC containers (InversifyJS, TSyringe) |

### NestJS DI Example

```typescript
// Service registration
@Injectable()
class OrderService {
  constructor(
    private orderRepo: OrderRepository,
    private eventBus: EventBus
  ) {}
}

// Module configuration
@Module({
  providers: [
    OrderService,
    { provide: OrderRepository, useClass: TypeORMOrderRepository },
    { provide: EventBus, useClass: EventEmitter2 }
  ],
  exports: [OrderService]
})
class OrderModule {}
```

### Spring Boot DI Example

```java
@Service
public class OrderService {
    private final OrderRepository orderRepo;
    private final EventBus eventBus;

    // Constructor injection (recommended)
    public OrderService(OrderRepository orderRepo, EventBus eventBus) {
        this.orderRepo = orderRepo;
        this.eventBus = eventBus;
    }
}

// Repository interface
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByCustomerId(Long customerId);
}
```

### FastAPI DI Example

```python
# Dependency
async def get_order_repo() -> OrderRepository:
    return TypeORMOrderRepository()

async def get_event_bus() -> EventBus:
    return EventBus()

# Service
class OrderService:
    def __init__(self, order_repo: OrderRepository, event_bus: EventBus):
        self.order_repo = order_repo
        self.event_bus = event_bus

    async def create_order(self, dto: CreateOrderDto) -> Order:
        # Business logic
        pass

# Route
@app.post("/orders")
async def create_order(
    dto: CreateOrderDto,
    order_service: OrderService = Depends(
        lambda: OrderService(
            order_repo=get_order_repo(),
            event_bus=get_event_bus()
        )
    )
):
    return await order_service.create_order(dto)
```

## Error Handling Patterns

### 1. Domain Exception Hierarchy

도메인 예외를 체계적으로 정의하여 비즈니스 에러를 명확히 표현합니다.

```typescript
// Base domain exception
abstract class DomainException extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500
  ) {
    super(message);
    this.name = this.constructor.name;
  }
}

// Specific exceptions
class NotFoundException extends DomainException {
  constructor(entity: string, id: string) {
    super(`${entity} with id ${id} not found`, 'NOT_FOUND', 404);
  }
}

class ValidationException extends DomainException {
  constructor(message: string, public errors?: Record<string, string[]>) {
    super(message, 'VALIDATION_ERROR', 400);
  }
}

class ConflictException extends DomainException {
  constructor(message: string) {
    super(message, 'CONFLICT', 409);
  }
}

class OutOfStockException extends ConflictException {
  constructor(productId: string) {
    super(`Product ${productId} is out of stock`);
  }
}

class UnauthorizedException extends DomainException {
  constructor(message: string = 'Unauthorized') {
    super(message, 'UNAUTHORIZED', 401);
  }
}

class ForbiddenException extends DomainException {
  constructor(message: string = 'Forbidden') {
    super(message, 'FORBIDDEN', 403);
  }
}
```

### 2. Global Error Handler

모든 예외를 일관되게 처리하고 적절한 HTTP 응답으로 변환합니다.

```typescript
// NestJS exception filter
@Catch()
class GlobalExceptionFilter implements ExceptionFilter {
  constructor(private logger: Logger) {}

  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    if (exception instanceof DomainException) {
      // Domain exception - expected business error
      this.logger.warn(
        `Domain exception: ${exception.code}`,
        { exception, request }
      );

      response.status(exception.statusCode).json({
        success: false,
        error: {
          code: exception.code,
          message: exception.message,
          ...(exception instanceof ValidationException && {
            errors: exception.errors
          })
        },
        timestamp: new Date().toISOString(),
        path: request.url
      });
    } else if (exception instanceof HttpException) {
      // Framework exception
      const status = exception.getStatus();
      response.status(status).json({
        success: false,
        error: {
          code: 'HTTP_EXCEPTION',
          message: exception.message
        },
        timestamp: new Date().toISOString(),
        path: request.url
      });
    } else {
      // Unexpected error - log with stack trace
      this.logger.error(
        'Unexpected error',
        exception instanceof Error ? exception.stack : exception
      );

      // Never expose internal details in production
      const message = process.env.NODE_ENV === 'production'
        ? 'Internal server error'
        : exception instanceof Error ? exception.message : 'Unknown error';

      response.status(500).json({
        success: false,
        error: {
          code: 'INTERNAL_ERROR',
          message
        },
        timestamp: new Date().toISOString(),
        path: request.url
      });
    }
  }
}
```

### 3. Result Pattern (Alternative to Exceptions)

예외 대신 Result 타입을 사용하여 에러를 명시적으로 처리합니다.

```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

// Helper functions
function success<T>(value: T): Result<T, never> {
  return { ok: true, value };
}

function failure<E>(error: E): Result<never, E> {
  return { ok: false, error };
}

// Usage
class OrderService {
  async createOrder(dto: CreateOrderDto): Promise<Result<Order, OrderError>> {
    // Validate
    const validation = await this.validateOrder(dto);
    if (!validation.ok) {
      return failure(validation.error);
    }

    // Process
    try {
      const order = await this.orderRepo.save(dto);
      return success(order);
    } catch (error) {
      return failure(new OrderError('Failed to create order', error));
    }
  }
}

// Controller
@Post()
async createOrder(@Body() dto: CreateOrderDto) {
  const result = await this.orderService.createOrder(dto);

  if (!result.ok) {
    throw new BadRequestException(result.error.message);
  }

  return { success: true, data: result.value };
}
```

## Event-Driven Patterns

### 1. Domain Events

도메인 이벤트를 통해 사이드 이펙트를 비즈니스 로직에서 분리합니다.

```typescript
// Event definition
interface DomainEvent {
  eventName: string;
  occurredAt: Date;
  aggregateId: string;
}

class OrderCreatedEvent implements DomainEvent {
  eventName = 'order.created';
  occurredAt = new Date();

  constructor(
    public aggregateId: string,
    public customerId: string,
    public total: number
  ) {}
}

// Event bus
interface EventBus {
  emit<T extends DomainEvent>(event: T): Promise<void>;
  on<T extends DomainEvent>(
    eventName: string,
    handler: (event: T) => Promise<void>
  ): void;
}

// Service emits events
class OrderService {
  constructor(
    private orderRepo: OrderRepository,
    private eventBus: EventBus
  ) {}

  async createOrder(dto: CreateOrderDto): Promise<Order> {
    const order = await this.orderRepo.save(dto);

    // Emit event - handlers execute asynchronously
    await this.eventBus.emit(new OrderCreatedEvent(
      order.id,
      order.customerId,
      order.total
    ));

    return order;
  }
}

// Event handlers
@Injectable()
class EmailNotificationHandler {
  async handleOrderCreated(event: OrderCreatedEvent): Promise<void> {
    // Send confirmation email
    await this.emailService.sendOrderConfirmation(event.customerId);
  }
}

@Injectable()
class AnalyticsHandler {
  async handleOrderCreated(event: OrderCreatedEvent): Promise<void> {
    // Track order in analytics
    await this.analytics.track('Order Created', {
      orderId: event.aggregateId,
      total: event.total
    });
  }
}

// Register handlers
eventBus.on('order.created', (e) => emailHandler.handleOrderCreated(e));
eventBus.on('order.created', (e) => analyticsHandler.handleOrderCreated(e));
```

### 2. Event Sourcing

이벤트를 상태 변경의 유일한 소스로 사용합니다.

```typescript
// Event store
interface EventStore {
  append(event: DomainEvent): Promise<void>;
  getEvents(aggregateId: string): Promise<DomainEvent[]>;
}

// Aggregate reconstructed from events
class Order {
  private events: DomainEvent[] = [];

  static fromEvents(events: DomainEvent[]): Order {
    const order = new Order();
    events.forEach(e => order.apply(e));
    return order;
  }

  createOrder(dto: CreateOrderDto): void {
    this.raise(new OrderCreatedEvent(this.id, dto.customerId, dto.total));
  }

  confirmPayment(paymentId: string): void {
    this.raise(new PaymentConfirmedEvent(this.id, paymentId));
  }

  private raise(event: DomainEvent): void {
    this.apply(event);
    this.events.push(event);
  }

  private apply(event: DomainEvent): void {
    if (event instanceof OrderCreatedEvent) {
      this.id = event.aggregateId;
      this.customerId = event.customerId;
      this.status = 'pending';
    } else if (event instanceof PaymentConfirmedEvent) {
      this.status = 'confirmed';
    }
  }

  getUncommittedEvents(): DomainEvent[] {
    return this.events;
  }
}
```

### 3. CQRS (Command Query Responsibility Segregation)

읽기와 쓰기 모델을 분리합니다.

```typescript
// Command (write model)
interface CreateOrderCommand {
  customerId: string;
  items: OrderItem[];
}

class OrderCommandHandler {
  async handle(command: CreateOrderCommand): Promise<string> {
    const order = new Order();
    order.create(command);

    // Save events
    for (const event of order.getUncommittedEvents()) {
      await this.eventStore.append(event);
    }

    return order.id;
  }
}

// Query (read model)
interface OrderQueryService {
  getOrderById(id: string): Promise<OrderView | null>;
  getOrdersByCustomer(customerId: string): Promise<OrderListView>;
}

// Read model is optimized for queries
interface OrderView {
  id: string;
  customerId: string;
  customerName: string;
  items: Array<{
    productId: string;
    productName: string;
    quantity: number;
    price: number;
  }>;
  total: number;
  status: string;
  createdAt: Date;
}

// Projection updates read model from events
class OrderProjection {
  async projectOrderCreated(event: OrderCreatedEvent): Promise<void> {
    await this.readDb.insert('order_views', {
      id: event.aggregateId,
      customerId: event.customerId,
      total: event.total,
      status: 'pending'
    });
  }
}
```

### 4. Saga Pattern

분산 트랜잭션을 여러 단계의 로컬 트랜잭션으로 조율합니다.

```typescript
// Saga coordinates distributed transaction
class OrderSaga {
  async execute(command: CreateOrderCommand): Promise<void> {
    let inventoryReserved = false;
    let paymentProcessed = false;

    try {
      // Step 1: Reserve inventory
      await this.inventoryService.reserve(command.items);
      inventoryReserved = true;

      // Step 2: Process payment
      await this.paymentService.charge(command.customerId, command.total);
      paymentProcessed = true;

      // Step 3: Create order
      await this.orderService.create(command);

    } catch (error) {
      // Compensating transactions
      if (paymentProcessed) {
        await this.paymentService.refund(command.customerId, command.total);
      }
      if (inventoryReserved) {
        await this.inventoryService.release(command.items);
      }
      throw error;
    }
  }
}
```

## Middleware/Interceptor Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Authentication** | Verify identity | JWT validation middleware |
| **Authorization** | Check permissions | RBAC/ABAC middleware |
| **Logging** | Request/response logging | Morgan, Winston |
| **Validation** | Input validation | class-validator, Zod |
| **Rate Limiting** | Throttle requests | Express-rate-limit |
| **Caching** | Response caching | Redis middleware |
| **Compression** | Response compression | gzip middleware |
| **CORS** | Cross-origin requests | CORS middleware |

### Authentication Middleware

```typescript
@Injectable()
class JwtAuthGuard implements CanActivate {
  constructor(private jwtService: JwtService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const token = this.extractToken(request);

    if (!token) {
      throw new UnauthorizedException('No token provided');
    }

    try {
      const payload = await this.jwtService.verifyAsync(token);
      request.user = payload;
      return true;
    } catch {
      throw new UnauthorizedException('Invalid token');
    }
  }

  private extractToken(request: Request): string | undefined {
    const [type, token] = request.headers.authorization?.split(' ') ?? [];
    return type === 'Bearer' ? token : undefined;
  }
}

// Usage
@Controller('orders')
@UseGuards(JwtAuthGuard)
class OrderController {
  @Get()
  async getOrders(@User() user: UserPayload) {
    return this.orderService.getOrdersByUser(user.id);
  }
}
```

### Validation Middleware

```typescript
// DTO with validation
class CreateOrderDto {
  @IsString()
  @IsNotEmpty()
  customerId: string;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => OrderItemDto)
  items: OrderItemDto[];
}

class OrderItemDto {
  @IsString()
  productId: string;

  @IsNumber()
  @Min(1)
  quantity: number;

  @IsNumber()
  @Min(0)
  price: number;
}

// Auto-validation in controller
@Post()
async createOrder(@Body() dto: CreateOrderDto) {
  // dto is already validated
  return this.orderService.createOrder(dto);
}
```

## Background Job Patterns

### Queue-Based Processing

```typescript
// Job definition
interface SendEmailJob {
  type: 'send-email';
  to: string;
  subject: string;
  body: string;
}

// Queue producer
@Injectable()
class EmailService {
  constructor(@InjectQueue('email') private emailQueue: Queue) {}

  async sendOrderConfirmation(orderId: string): Promise<void> {
    await this.emailQueue.add('send-email', {
      to: order.customer.email,
      subject: 'Order Confirmation',
      body: this.renderTemplate('order-confirmation', order)
    }, {
      attempts: 3,
      backoff: { type: 'exponential', delay: 1000 }
    });
  }
}

// Queue consumer
@Processor('email')
class EmailProcessor {
  @Process('send-email')
  async handleSendEmail(job: Job<SendEmailJob>): Promise<void> {
    const { to, subject, body } = job.data;
    await this.smtpService.send({ to, subject, body });
  }
}
```

### Scheduled Tasks

```typescript
@Injectable()
class TaskScheduler {
  @Cron('0 0 * * *')  // Every day at midnight
  async cleanupOldOrders(): Promise<void> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - 90);

    await this.orderRepo.deleteOlderThan(cutoffDate);
  }

  @Interval(60000)  // Every minute
  async processTimeoutOrders(): Promise<void> {
    const timedOutOrders = await this.orderRepo.findTimedOut();
    for (const order of timedOutOrders) {
      await this.orderService.cancelOrder(order.id);
    }
  }
}
```

### Retry Strategies

```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  options: {
    maxAttempts: number;
    backoff: 'exponential' | 'linear';
    initialDelay: number;
  }
): Promise<T> {
  let lastError: Error;

  for (let attempt = 1; attempt <= options.maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      if (attempt < options.maxAttempts) {
        const delay = options.backoff === 'exponential'
          ? options.initialDelay * Math.pow(2, attempt - 1)
          : options.initialDelay * attempt;

        await sleep(delay);
      }
    }
  }

  throw lastError;
}
```

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **Anemic Domain Model** | Logic scattered in services | Rich domain model with behavior |
| **God Service** | Single service does everything | Split by domain/bounded context |
| **Repository leaking queries** | ORM coupling, hard to test | Abstract query methods with domain language |
| **Transaction per operation** | Data inconsistency risk | Unit of Work for logical operations |
| **Synchronous event handling** | Cascading failures | Async event bus or message queue |
| **Fat Controller** | Business logic in controller | Move logic to service layer |
| **Service depends on Service** | Tight coupling, circular dependencies | Shared kernel or domain events |
| **No error boundaries** | Exceptions crash entire app | Global error handler + domain exceptions |

### Example: Anemic vs Rich Domain Model

```typescript
// ANEMIC (bad) - domain object is just data
class Order {
  id: string;
  customerId: string;
  items: OrderItem[];
  status: string;
  total: number;
}

// Logic scattered in service
class OrderService {
  async confirmOrder(orderId: string): Promise<void> {
    const order = await this.orderRepo.findById(orderId);
    if (order.status !== 'pending') {
      throw new Error('Cannot confirm non-pending order');
    }
    order.status = 'confirmed';
    await this.orderRepo.save(order);
  }
}

// RICH (good) - domain object has behavior
class Order {
  private constructor(
    public readonly id: string,
    public readonly customerId: string,
    private items: OrderItem[],
    private status: OrderStatus
  ) {}

  confirm(): void {
    if (this.status !== OrderStatus.Pending) {
      throw new InvalidOperationException('Cannot confirm non-pending order');
    }
    this.status = OrderStatus.Confirmed;
  }

  calculateTotal(): number {
    return this.items.reduce((sum, item) => sum + item.subtotal(), 0);
  }
}

// Service is thin - just coordinates
class OrderService {
  async confirmOrder(orderId: string): Promise<void> {
    const order = await this.orderRepo.findById(orderId);
    order.confirm();  // Domain logic in domain object
    await this.orderRepo.save(order);
  }
}
```
