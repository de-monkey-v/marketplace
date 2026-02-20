# Test Patterns Reference

테스트 코드 작성을 위한 패턴 카탈로그와 프레임워크별 실전 가이드입니다.

## Test Pyramid

```
        /\
       /  \       E2E Tests (5-10%)
      / E2E \     - Few, slow, expensive
     /--------\   - Full system verification
    /          \  - Critical user journeys only
   /            \
  / Integration \  Integration Tests (20-30%)
 /               \ - Some, medium speed
/                 \- Component interactions
|-----------------|
|                 |
|   Unit Tests    | Unit Tests (60-75%)
|                 | - Many, fast, cheap
|                 | - Business logic focus
|_________________|
```

### Pyramid Guidelines

**유닛 테스트 (Base Layer)**
- 목표: 전체 테스트의 60-75%
- 실행 시간: 밀리초 단위 (전체 스위트 < 30초)
- 범위: 단일 함수, 클래스, 모듈
- 의존성: 모두 mock/stub으로 격리
- 예시: 계산 로직, 유효성 검증, 데이터 변환

**통합 테스트 (Middle Layer)**
- 목표: 전체 테스트의 20-30%
- 실행 시간: 초 단위 (전체 스위트 < 5분)
- 범위: 여러 컴포넌트 또는 레이어 간 상호작용
- 의존성: 일부 실제 인프라 사용 (테스트 DB, 메시지 큐)
- 예시: API 엔드포인트, DB 쿼리, 서비스 레이어 통합

**E2E 테스트 (Top Layer)**
- 목표: 전체 테스트의 5-10%
- 실행 시간: 분 단위 (전체 스위트 < 30분)
- 범위: 전체 애플리케이션 스택
- 의존성: 실제 환경과 유사하게 구성
- 예시: 사용자 가입/로그인, 주문 처리, 결제 플로우

## Unit Test Patterns

### 1. Given-When-Then (AAA) Pattern

가장 기본적이고 널리 사용되는 테스트 구조 패턴입니다.

```typescript
describe('ClassName', () => {
  describe('methodName', () => {
    it('should [expected behavior] when [condition]', () => {
      // Given (Arrange) - 테스트 전제 조건 설정
      const input = createTestInput();
      const dependency = createMockDependency();
      const target = new ClassName(dependency);

      // When (Act) - 테스트 대상 실행
      const result = target.method(input);

      // Then (Assert) - 결과 검증
      expect(result).toBe(expected);
      expect(dependency.someMethod).toHaveBeenCalled();
    });
  });
});
```

**실전 예제 - 계산기:**

```typescript
describe('Calculator', () => {
  describe('add', () => {
    it('should return sum of two numbers when both are positive', () => {
      // Given
      const calculator = new Calculator();
      const a = 5;
      const b = 3;

      // When
      const result = calculator.add(a, b);

      // Then
      expect(result).toBe(8);
    });

    it('should handle negative numbers correctly', () => {
      // Given
      const calculator = new Calculator();

      // When
      const result = calculator.add(-5, 3);

      // Then
      expect(result).toBe(-2);
    });
  });
});
```

### 2. Test Doubles - Decision Matrix

테스트에서 외부 의존성을 대체하는 객체들의 종류와 사용 시점을 정리합니다.

| Type | Purpose | When to Use | Example Scenario | Framework Example |
|------|---------|-------------|------------------|-------------------|
| **Stub** | 미리 정의된 데이터 반환 | 쿼리 작업, 데이터 조회 | 외부 API 응답, DB 조회 결과 | `jest.fn().mockReturnValue(data)` |
| **Mock** | 호출 여부 및 인자 검증 | 커맨드 작업, 부수 효과 | 이메일 발송, 로그 기록 | `jest.fn()` + `expect().toHaveBeenCalledWith()` |
| **Spy** | 실제 구현 유지하며 관찰 | 일부만 대체 필요 시 | 실제 메서드 호출하되 관찰 | `jest.spyOn(object, 'method')` |
| **Fake** | 단순화된 실제 구현 | 복잡한 인프라 대체 | In-memory DB, 파일 시스템 | Custom class implementation |

#### Stub Example

```typescript
// 외부 API 호출 대신 고정된 데이터 반환
it('should get user profile from API', async () => {
  // Given
  const mockApiClient = {
    get: jest.fn().mockResolvedValue({
      data: { id: '123', name: 'John' }
    })
  };
  const service = new UserService(mockApiClient);

  // When
  const user = await service.getUserProfile('123');

  // Then
  expect(user.name).toBe('John');
});
```

#### Mock Example

```typescript
// 이메일 발송 여부 검증 (부수 효과 확인)
it('should send welcome email when user signs up', async () => {
  // Given
  const mockEmailService = {
    send: jest.fn().mockResolvedValue(true)
  };
  const service = new UserService(mockEmailService);

  // When
  await service.signUp('user@example.com');

  // Then
  expect(mockEmailService.send).toHaveBeenCalledWith({
    to: 'user@example.com',
    subject: 'Welcome!',
    template: 'welcome'
  });
});
```

#### Spy Example

```typescript
// 실제 메서드는 실행하되, 호출 여부 관찰
it('should log audit trail when updating user', async () => {
  // Given
  const logger = new Logger();
  const logSpy = jest.spyOn(logger, 'log');
  const service = new UserService(logger);

  // When
  await service.updateUser('123', { name: 'Jane' });

  // Then
  expect(logSpy).toHaveBeenCalledWith('User updated', { userId: '123' });
  logSpy.mockRestore(); // cleanup
});
```

#### Fake Example

```typescript
// In-memory repository로 실제 DB 대체
class FakeUserRepository implements UserRepository {
  private users = new Map<string, User>();

  async save(user: User): Promise<void> {
    this.users.set(user.id, user);
  }

  async findById(id: string): Promise<User | null> {
    return this.users.get(id) || null;
  }

  async clear(): Promise<void> {
    this.users.clear();
  }
}

it('should save and retrieve user', async () => {
  // Given
  const repo = new FakeUserRepository();
  const user = { id: '123', name: 'John' };

  // When
  await repo.save(user);
  const retrieved = await repo.findById('123');

  // Then
  expect(retrieved).toEqual(user);
});
```

### 3. Parameterized Tests (Data-Driven)

동일한 로직을 다양한 입력값으로 테스트할 때 사용합니다.

```typescript
// Jest: test.each
describe('isPalindrome', () => {
  test.each([
    ['racecar', true],
    ['hello', false],
    ['A man a plan a canal Panama', true],
    ['', true],
    ['a', true]
  ])('isPalindrome("%s") should return %s', (input, expected) => {
    expect(isPalindrome(input)).toBe(expected);
  });
});

// JUnit 5: @ParameterizedTest
@ParameterizedTest
@CsvSource({
    "racecar, true",
    "hello, false",
    "A man a plan a canal Panama, true"
})
void testIsPalindrome(String input, boolean expected) {
    assertEquals(expected, StringUtils.isPalindrome(input));
}

// pytest: @pytest.mark.parametrize
@pytest.mark.parametrize("input,expected", [
    ("racecar", True),
    ("hello", False),
    ("A man a plan a canal Panama", True),
])
def test_is_palindrome(input, expected):
    assert is_palindrome(input) == expected
```

### 4. Builder Pattern for Test Data

복잡한 테스트 객체를 구성할 때 사용하는 패턴입니다.

```typescript
// Test Data Builder
class UserBuilder {
  private user: Partial<User> = {
    id: '123',
    email: 'test@example.com',
    name: 'Test User',
    role: 'user',
    active: true
  };

  withId(id: string): UserBuilder {
    this.user.id = id;
    return this;
  }

  withEmail(email: string): UserBuilder {
    this.user.email = email;
    return this;
  }

  withRole(role: string): UserBuilder {
    this.user.role = role;
    return this;
  }

  inactive(): UserBuilder {
    this.user.active = false;
    return this;
  }

  build(): User {
    return this.user as User;
  }
}

// 사용 예시
it('should not allow inactive users to login', () => {
  // Given - 읽기 쉽고 의도가 명확
  const user = new UserBuilder()
    .withEmail('inactive@example.com')
    .inactive()
    .build();

  // When & Then
  expect(() => authService.login(user)).toThrow('User is inactive');
});

it('should grant admin privileges to admin users', () => {
  // Given
  const admin = new UserBuilder()
    .withRole('admin')
    .build();

  // When
  const privileges = authService.getPrivileges(admin);

  // Then
  expect(privileges).toContain('delete_users');
});
```

### 5. Custom Matchers

도메인 특화된 검증 로직을 재사용 가능하게 만듭니다.

```typescript
// Jest Custom Matcher
expect.extend({
  toBeValidEmail(received: string) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const pass = emailRegex.test(received);

    return {
      pass,
      message: () =>
        pass
          ? `expected ${received} not to be a valid email`
          : `expected ${received} to be a valid email`
    };
  }
});

// 사용
it('should validate email format', () => {
  expect('user@example.com').toBeValidEmail();
  expect('invalid-email').not.toBeValidEmail();
});

// 복잡한 객체 검증
expect.extend({
  toBeValidUser(received: any) {
    const checks = [
      received.id && typeof received.id === 'string',
      received.email && /\S+@\S+\.\S+/.test(received.email),
      received.createdAt && received.createdAt instanceof Date
    ];

    const pass = checks.every(check => check === true);

    return {
      pass,
      message: () => `expected ${JSON.stringify(received)} to be a valid user`
    };
  }
});
```

## Integration Test Patterns

### 1. Database Integration Tests

#### Transaction Rollback Pattern

각 테스트 후 자동으로 롤백하여 격리를 보장합니다.

```typescript
// TypeORM + Jest
describe('UserRepository Integration Tests', () => {
  let connection: Connection;
  let repository: UserRepository;

  beforeAll(async () => {
    connection = await createConnection({
      type: 'postgres',
      database: 'test_db',
      synchronize: true,
      entities: [User]
    });
  });

  beforeEach(async () => {
    await connection.query('BEGIN');
  });

  afterEach(async () => {
    await connection.query('ROLLBACK');
  });

  afterAll(async () => {
    await connection.close();
  });

  it('should save user to database', async () => {
    // Given
    const user = new User();
    user.email = 'test@example.com';

    // When
    await repository.save(user);
    const found = await repository.findOne({ email: 'test@example.com' });

    // Then
    expect(found).toBeDefined();
    expect(found.email).toBe('test@example.com');
  });
});
```

#### Test Containers Pattern

실제 DB 컨테이너를 사용하여 프로덕션 환경과 동일한 조건에서 테스트합니다.

```typescript
import { GenericContainer } from 'testcontainers';

describe('UserRepository with TestContainers', () => {
  let container: StartedTestContainer;
  let connection: Connection;

  beforeAll(async () => {
    container = await new GenericContainer('postgres:14')
      .withExposedPorts(5432)
      .withEnvironment({
        POSTGRES_USER: 'test',
        POSTGRES_PASSWORD: 'test',
        POSTGRES_DB: 'test_db'
      })
      .start();

    const port = container.getMappedPort(5432);
    connection = await createConnection({
      type: 'postgres',
      host: 'localhost',
      port,
      username: 'test',
      password: 'test',
      database: 'test_db'
    });
  }, 30000); // 컨테이너 시작 시간 고려

  afterAll(async () => {
    await connection.close();
    await container.stop();
  });

  // tests...
});
```

### 2. API Integration Tests

#### Supertest Pattern (Node.js/Express)

```typescript
import request from 'supertest';
import { app } from '../src/app';

describe('User API', () => {
  describe('POST /api/users', () => {
    it('should create user and return 201', async () => {
      // Given
      const newUser = {
        email: 'test@example.com',
        name: 'Test User'
      };

      // When
      const response = await request(app)
        .post('/api/users')
        .send(newUser)
        .expect(201)
        .expect('Content-Type', /json/);

      // Then
      expect(response.body).toMatchObject({
        email: newUser.email,
        name: newUser.name
      });
      expect(response.body.id).toBeDefined();
    });

    it('should return 400 when email is invalid', async () => {
      // Given
      const invalidUser = {
        email: 'invalid-email',
        name: 'Test User'
      };

      // When & Then
      const response = await request(app)
        .post('/api/users')
        .send(invalidUser)
        .expect(400);

      expect(response.body.error).toContain('Invalid email');
    });
  });

  describe('GET /api/users/:id', () => {
    it('should return user when exists', async () => {
      // Given - setup test data
      const user = await createTestUser();

      // When
      const response = await request(app)
        .get(`/api/users/${user.id}`)
        .expect(200);

      // Then
      expect(response.body).toMatchObject({
        id: user.id,
        email: user.email
      });
    });

    it('should return 404 when user not found', async () => {
      await request(app)
        .get('/api/users/nonexistent-id')
        .expect(404);
    });
  });
});
```

#### Spring Boot @SpringBootTest Pattern

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
@Transactional
class UserControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldCreateUserAndReturn201() throws Exception {
        // Given
        UserCreateRequest request = new UserCreateRequest(
            "test@example.com",
            "Test User"
        );

        // When & Then
        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.email").value("test@example.com"))
            .andExpect(jsonPath("$.id").exists());
    }

    @Test
    void shouldReturn400WhenEmailIsInvalid() throws Exception {
        // Given
        UserCreateRequest request = new UserCreateRequest(
            "invalid-email",
            "Test User"
        );

        // When & Then
        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.error").value(containsString("Invalid email")));
    }
}
```

### 3. Service Layer Integration Tests

여러 레이어를 함께 테스트하되, 외부 의존성만 mocking합니다.

```typescript
describe('OrderService Integration', () => {
  let orderService: OrderService;
  let mockPaymentGateway: jest.Mocked<PaymentGateway>;
  let realOrderRepository: OrderRepository;
  let realInventoryService: InventoryService;

  beforeEach(async () => {
    // 실제 컴포넌트 사용
    realOrderRepository = new OrderRepository(testDbConnection);
    realInventoryService = new InventoryService(testDbConnection);

    // 외부 시스템만 mocking
    mockPaymentGateway = {
      charge: jest.fn().mockResolvedValue({ success: true, transactionId: 'tx123' })
    } as any;

    orderService = new OrderService(
      realOrderRepository,
      realInventoryService,
      mockPaymentGateway
    );
  });

  it('should complete order flow when payment succeeds', async () => {
    // Given
    const order = {
      userId: 'user123',
      items: [{ productId: 'prod1', quantity: 2 }],
      totalAmount: 100
    };

    // When
    const result = await orderService.placeOrder(order);

    // Then
    expect(result.status).toBe('confirmed');
    expect(mockPaymentGateway.charge).toHaveBeenCalledWith({
      amount: 100,
      userId: 'user123'
    });

    // DB에 실제로 저장되었는지 확인
    const savedOrder = await realOrderRepository.findById(result.id);
    expect(savedOrder.status).toBe('confirmed');

    // 재고가 실제로 차감되었는지 확인
    const inventory = await realInventoryService.getStock('prod1');
    expect(inventory.available).toBe(inventory.initial - 2);
  });
});
```

### 4. Message Queue Integration Tests

```typescript
import { RabbitMQContainer } from 'testcontainers';
import amqp from 'amqplib';

describe('OrderEventPublisher Integration', () => {
  let container: StartedTestContainer;
  let connection: amqp.Connection;
  let channel: amqp.Channel;

  beforeAll(async () => {
    container = await new RabbitMQContainer().start();
    const amqpUrl = container.getAmqpUrl();
    connection = await amqp.connect(amqpUrl);
    channel = await connection.createChannel();
  }, 30000);

  afterAll(async () => {
    await channel.close();
    await connection.close();
    await container.stop();
  });

  it('should publish order created event', async () => {
    // Given
    const queueName = 'test.orders.created';
    await channel.assertQueue(queueName, { durable: false });

    const publisher = new OrderEventPublisher(channel);
    const order = { id: '123', userId: 'user1', total: 100 };

    // When
    await publisher.publishOrderCreated(order);

    // Then - 메시지가 큐에 도착했는지 확인
    const message = await new Promise<amqp.ConsumeMessage>((resolve) => {
      channel.consume(queueName, (msg) => {
        if (msg) {
          channel.ack(msg);
          resolve(msg);
        }
      });
    });

    const payload = JSON.parse(message.content.toString());
    expect(payload).toMatchObject({
      orderId: '123',
      userId: 'user1',
      eventType: 'ORDER_CREATED'
    });
  });
});
```

## E2E Test Patterns

### 1. Page Object Model (POM)

UI 상호작용을 캡슐화하여 재사용성과 유지보수성을 높입니다.

```typescript
// pages/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}

  async navigate() {
    await this.page.goto('/login');
  }

  async fillEmail(email: string) {
    await this.page.fill('[data-testid="email-input"]', email);
  }

  async fillPassword(password: string) {
    await this.page.fill('[data-testid="password-input"]', password);
  }

  async clickSubmit() {
    await this.page.click('[data-testid="login-submit"]');
  }

  async login(email: string, password: string) {
    await this.fillEmail(email);
    await this.fillPassword(password);
    await this.clickSubmit();
  }

  async getErrorMessage(): Promise<string> {
    return await this.page.textContent('[data-testid="error-message"]');
  }
}

// tests/login.e2e.test.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

test.describe('Login Flow', () => {
  test('should login successfully with valid credentials', async ({ page }) => {
    // Given
    const loginPage = new LoginPage(page);
    await loginPage.navigate();

    // When
    await loginPage.login('user@example.com', 'password123');

    // Then
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('[data-testid="user-name"]')).toContainText('User Name');
  });

  test('should show error with invalid credentials', async ({ page }) => {
    // Given
    const loginPage = new LoginPage(page);
    await loginPage.navigate();

    // When
    await loginPage.login('user@example.com', 'wrongpassword');

    // Then
    const errorMessage = await loginPage.getErrorMessage();
    expect(errorMessage).toContain('Invalid credentials');
  });
});
```

### 2. Test User Management

격리된 테스트 계정으로 테스트 간 간섭을 방지합니다.

```typescript
// utils/testUsers.ts
export class TestUserManager {
  private static userCounter = 0;

  static async createTestUser(): Promise<TestUser> {
    const uniqueId = `test-${Date.now()}-${this.userCounter++}`;
    const user = {
      email: `${uniqueId}@test.com`,
      password: 'Test123!',
      name: `Test User ${uniqueId}`
    };

    // API를 통해 사용자 생성 (UI 통하지 않음!)
    const response = await fetch('/api/test/users', {
      method: 'POST',
      body: JSON.stringify(user)
    });

    return await response.json();
  }

  static async cleanup() {
    // 테스트 종료 후 생성된 사용자 정리
    await fetch('/api/test/users', { method: 'DELETE' });
  }
}

// 사용 예시
test('should complete checkout flow', async ({ page }) => {
  // Given - 새로운 테스트 사용자 생성
  const user = await TestUserManager.createTestUser();

  // When - 로그인 및 주문
  await loginAs(page, user);
  await completeOrder(page);

  // Then
  await expect(page.locator('[data-testid="order-confirmation"]')).toBeVisible();
});
```

### 3. State Setup via API (Not UI!)

E2E 테스트에서도 초기 상태 설정은 API를 사용합니다.

```typescript
test('should display order history', async ({ page }) => {
  // Given - API로 테스트 데이터 준비 (UI로 하지 않음!)
  const user = await createTestUser();
  const order1 = await createOrderViaAPI(user.id, { total: 100 });
  const order2 = await createOrderViaAPI(user.id, { total: 200 });

  // When - UI 테스트 시작
  await loginAs(page, user);
  await page.goto('/orders');

  // Then
  await expect(page.locator('[data-testid="order-item"]')).toHaveCount(2);
  await expect(page.locator(`[data-order-id="${order1.id}"]`)).toBeVisible();
  await expect(page.locator(`[data-order-id="${order2.id}"]`)).toBeVisible();
});
```

### 4. Retry Strategies for Flaky Tests

```typescript
// Playwright - 자동 재시도 및 대기
test('should load async data', async ({ page }) => {
  await page.goto('/dashboard');

  // ❌ 나쁜 예: 고정 대기
  // await page.waitForTimeout(5000);

  // ✅ 좋은 예: 조건 기반 대기
  await page.waitForSelector('[data-testid="data-loaded"]', {
    state: 'visible',
    timeout: 10000
  });

  // ✅ 더 나은 예: Playwright의 자동 대기
  await expect(page.locator('[data-testid="user-count"]'))
    .toHaveText(/\d+ users/, { timeout: 10000 });
});

// Cypress - 자동 재시도
cy.get('[data-testid="submit"]').click();
cy.get('[data-testid="success-message"]')
  .should('be.visible')
  .and('contain', 'Saved successfully');
```

## Framework Quick Reference

### Jest (JavaScript/TypeScript)

```typescript
// 기본 구조
describe('테스트 스위트', () => {
  beforeAll(() => { /* 스위트 시작 전 한 번 */ });
  afterAll(() => { /* 스위트 종료 후 한 번 */ });
  beforeEach(() => { /* 각 테스트 전 */ });
  afterEach(() => { /* 각 테스트 후 */ });

  it('should do something', () => {
    expect(actual).toBe(expected);
  });

  test('alternative syntax', () => {
    expect(actual).toEqual(expected);
  });
});

// 주요 Matchers
expect(value).toBe(5);                    // ===
expect(value).toEqual({ a: 1 });          // deep equality
expect(value).toBeTruthy();
expect(value).toBeNull();
expect(value).toBeDefined();
expect(array).toContain(item);
expect(array).toHaveLength(3);
expect(string).toMatch(/pattern/);
expect(() => fn()).toThrow(Error);
expect(fn).toHaveBeenCalled();
expect(fn).toHaveBeenCalledWith(arg1, arg2);

// 비동기
await expect(promise).resolves.toBe(value);
await expect(promise).rejects.toThrow();

// Mock 생성
const mockFn = jest.fn();
const mockFn = jest.fn().mockReturnValue(42);
const mockFn = jest.fn().mockResolvedValue(data);
jest.spyOn(object, 'method');

// 실행
npm test
npm test -- --coverage
npm test -- --watch
```

### Vitest (JavaScript/TypeScript)

```typescript
// Jest와 거의 동일한 API
import { describe, it, expect, vi } from 'vitest';

describe('Component', () => {
  it('should work', () => {
    expect(1 + 1).toBe(2);
  });
});

// Mock (vi 사용)
const mockFn = vi.fn();
vi.spyOn(object, 'method');
vi.mock('./module');

// 실행
npx vitest
npx vitest --coverage
npx vitest --ui  // UI 모드
```

### JUnit 5 (Java)

```java
import org.junit.jupiter.api.*;
import static org.assertj.core.api.Assertions.*;

class CalculatorTest {
    private Calculator calculator;

    @BeforeAll
    static void setupClass() { /* 클래스 초기화 */ }

    @BeforeEach
    void setup() {
        calculator = new Calculator();
    }

    @Test
    @DisplayName("Should add two numbers")
    void shouldAddTwoNumbers() {
        // Given
        int a = 5, b = 3;

        // When
        int result = calculator.add(a, b);

        // Then
        assertThat(result).isEqualTo(8);
    }

    @ParameterizedTest
    @CsvSource({"1,2,3", "5,3,8"})
    void shouldAddParameters(int a, int b, int expected) {
        assertThat(calculator.add(a, b)).isEqualTo(expected);
    }
}

// Mock (Mockito)
@Mock
private UserRepository mockRepository;

@InjectMocks
private UserService service;

when(mockRepository.findById("123"))
    .thenReturn(Optional.of(user));

verify(mockRepository).save(any(User.class));

// 실행
mvn test
mvn test -Dtest=ClassName
./gradlew test
```

### pytest (Python)

```python
import pytest

class TestCalculator:
    @pytest.fixture
    def calculator(self):
        return Calculator()

    def test_add(self, calculator):
        # Given
        a, b = 5, 3

        # When
        result = calculator.add(a, b)

        # Then
        assert result == 8

    @pytest.mark.parametrize("a,b,expected", [
        (1, 2, 3),
        (5, 3, 8),
        (-1, 1, 0)
    ])
    def test_add_parametrized(self, calculator, a, b, expected):
        assert calculator.add(a, b) == expected

# Mock (pytest-mock or unittest.mock)
def test_api_call(mocker):
    mock_get = mocker.patch('requests.get')
    mock_get.return_value.json.return_value = {'data': 'value'}

    result = fetch_data()

    assert result == {'data': 'value'}
    mock_get.assert_called_once_with('https://api.example.com')

# 실행
pytest
pytest -v
pytest --cov=src --cov-report=html
pytest -k "test_add"  # 이름으로 필터링
```

### Go testing

```go
package calculator

import "testing"

func TestAdd(t *testing.T) {
    // Given
    a, b := 5, 3
    calculator := NewCalculator()

    // When
    result := calculator.Add(a, b)

    // Then
    if result != 8 {
        t.Errorf("Add(%d, %d) = %d; want 8", a, b, result)
    }
}

// Table-driven tests
func TestAddTable(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive", 5, 3, 8},
        {"negative", -1, 1, 0},
        {"zero", 0, 0, 0},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Add(tt.a, tt.b)
            if result != tt.expected {
                t.Errorf("got %d, want %d", result, tt.expected)
            }
        })
    }
}

// Mock (testify/mock)
type MockUserRepository struct {
    mock.Mock
}

func (m *MockUserRepository) FindById(id string) (*User, error) {
    args := m.Called(id)
    return args.Get(0).(*User), args.Error(1)
}

// 실행
go test
go test -v
go test -cover
go test -coverprofile=coverage.out
go tool cover -html=coverage.out
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Bad Example | Good Example |
|--------------|---------|-------------|--------------|
| **Testing Implementation Details** | 리팩토링 시 테스트 깨짐 | `expect(component.state.count).toBe(5)` | `expect(screen.getByText('5')).toBeVisible()` |
| **Shared Mutable State** | 테스트 간 간섭으로 flaky | `const sharedUser = createUser()` (전역) | `beforeEach(() => user = createUser())` |
| **Sleeping in Tests** | 느리고 불안정 | `await sleep(5000)` | `await waitFor(() => expect(element).toBeVisible())` |
| **Over-mocking** | 실제 버그 놓침 | 모든 의존성 mocking | 경계에서만 mock, 내부는 실제 사용 |
| **No Assertion** | 테스트가 항상 통과 | `it('should work', () => { doSomething(); })` | `expect(result).toBe(expected)` |
| **Unclear Test Names** | 실패 시 원인 파악 어려움 | `test('test1')` | `test('should return null when user not found')` |
| **Testing Multiple Things** | 실패 원인 불명확 | 하나의 테스트에서 여러 시나리오 | 각 시나리오마다 별도 테스트 |
| **Large Setup Code** | 테스트 이해 어려움 | 50줄 setup 코드 | Helper 함수/Builder 패턴 사용 |
| **Ignoring Test Failures** | 신뢰도 하락 | `xit('flaky test')` | 근본 원인 해결 또는 삭제 |
| **Tight Coupling to Test Framework** | 이식성 저하 | 비즈니스 로직에 테스트 코드 섞임 | 순수한 비즈니스 로직 유지 |

### Anti-Pattern 상세 예시

#### 1. Testing Implementation Details (BAD)

```typescript
// ❌ 나쁜 예: React 컴포넌트 내부 state 테스트
it('should update count state', () => {
  const wrapper = shallow(<Counter />);
  wrapper.find('button').simulate('click');
  expect(wrapper.state('count')).toBe(1);  // 구현 세부사항!
});

// ✅ 좋은 예: 사용자가 보는 결과 테스트
it('should display incremented count when button clicked', () => {
  render(<Counter />);
  fireEvent.click(screen.getByRole('button'));
  expect(screen.getByText('Count: 1')).toBeInTheDocument();
});
```

#### 2. Shared Mutable State (BAD)

```typescript
// ❌ 나쁜 예: 테스트 간 상태 공유
let user: User;  // 공유 상태!

beforeAll(() => {
  user = createUser();  // 모든 테스트가 같은 user 사용
});

it('should update user name', () => {
  user.name = 'Jane';  // 다른 테스트에 영향!
});

// ✅ 좋은 예: 각 테스트마다 독립적인 상태
beforeEach(() => {
  user = createUser();  // 매 테스트마다 새로 생성
});
```

#### 3. Over-mocking (BAD)

```typescript
// ❌ 나쁜 예: 모든 것을 mocking
jest.mock('./userRepository');
jest.mock('./emailService');
jest.mock('./logger');
jest.mock('./validator');  // 내부 로직까지 mocking

const service = new UserService(
  mockRepo,
  mockEmail,
  mockLogger,
  mockValidator
);

// ✅ 좋은 예: 경계만 mocking, 내부는 실제 사용
const service = new UserService(
  mockRepo,        // 외부 의존성 (DB)
  mockEmail,       // 외부 의존성 (이메일)
  realLogger,      // 내부 로직
  realValidator    // 내부 로직
);
```

## Conclusion

이 레퍼런스의 패턴들을 적절히 조합하여 프로젝트에 맞는 테스트 전략을 구축하세요. 핵심은:

1. **테스트 피라미드 준수** - 유닛 테스트에 투자하고, E2E는 최소화
2. **명확한 의도 표현** - 테스트 이름과 구조로 의도 전달
3. **적절한 격리** - 독립적으로 실행 가능한 테스트 작성
4. **실용적 접근** - 100% 커버리지보다 핵심 로직 충실히 검증

테스트는 버그를 찾는 도구가 아니라, 코드 품질과 리팩토링 신뢰성을 보장하는 투자입니다.
