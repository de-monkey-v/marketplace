# Coverage Analysis and Test Case Design Guide

코드 커버리지 측정, 분석, 개선을 위한 실전 가이드입니다.

## Coverage Metrics

### Metric Types and Targets

| Metric | Definition | Target | When Useful | Example |
|--------|------------|--------|-------------|---------|
| **Statement** | 실행된 구문의 비율 | 80%+ | 기본 커버리지 측정 | `const x = 5;` 실행 여부 |
| **Branch** | 실행된 조건 분기의 비율 | 75%+ | 조건문, 논리 연산 검증 | `if (x > 0)` 양쪽 분기 실행 |
| **Function** | 호출된 함수의 비율 | 90%+ | API 완전성 확인 | 모든 public 메서드 호출 |
| **Line** | 실행된 코드 라인의 비율 | 80%+ | 전반적 커버리지 | 실제 코드 라인 실행 |
| **MC/DC** | Modified Condition/Decision Coverage | Safety-critical | 복잡한 조건식 검증 | 각 조건이 결과에 독립적 영향 |

### Metric Detailed Explanation

#### Statement Coverage

가장 기본적인 메트릭으로, 각 구문이 최소 한 번 실행되었는지 측정합니다.

```typescript
function divide(a: number, b: number): number {
  if (b === 0) {           // Line 2
    throw new Error('Division by zero');  // Line 3
  }
  return a / b;            // Line 5
}

// 50% statement coverage
test('divide positive numbers', () => {
  expect(divide(10, 2)).toBe(5);  // Line 2, 5 실행 (Line 3 미실행)
});

// 100% statement coverage
test('divide by zero throws error', () => {
  expect(() => divide(10, 0)).toThrow();  // Line 2, 3 실행
});
```

#### Branch Coverage

조건문의 각 분기가 실행되었는지 측정합니다.

```typescript
function getDiscount(price: number, isPremium: boolean): number {
  let discount = 0;

  if (price > 100) {          // Branch 1
    discount = 10;
  }

  if (isPremium) {            // Branch 2
    discount += 5;
  }

  return discount;
}

// Branch coverage 계산
// Branch 1: true/false
// Branch 2: true/false
// Total: 4 branches

// 50% branch coverage (2/4)
test('basic case', () => {
  expect(getDiscount(50, false)).toBe(0);  // Both branches false
});

// 100% branch coverage (4/4)
test('all branches', () => {
  expect(getDiscount(50, false)).toBe(0);    // F, F
  expect(getDiscount(150, false)).toBe(10);  // T, F
  expect(getDiscount(50, true)).toBe(5);     // F, T
  expect(getDiscount(150, true)).toBe(15);   // T, T
});
```

#### Function Coverage

정의된 함수 중 호출된 함수의 비율입니다.

```typescript
class UserService {
  create(user: User): void { /* ... */ }
  update(user: User): void { /* ... */ }
  delete(id: string): void { /* ... */ }
  find(id: string): User { /* ... */ }
}

// 50% function coverage (2/4 함수만 테스트)
test('user CRUD', () => {
  service.create(user);
  service.find(user.id);
  // update, delete는 테스트 안 함
});
```

#### MC/DC (Modified Condition/Decision Coverage)

항공우주 등 안전이 중요한 시스템에서 사용하는 엄격한 커버리지 기준입니다.

```typescript
// 복잡한 조건식
if ((A || B) && C) {
  // critical code
}

// MC/DC는 각 조건(A, B, C)이 독립적으로 결과에 영향을 미치는지 확인
// 최소 테스트 케이스:
// 1. A=T, B=F, C=T -> True  (A가 결과 결정)
// 2. A=F, B=F, C=T -> False (A가 결과 결정)
// 3. A=F, B=T, C=T -> True  (B가 결과 결정)
// 4. A=F, B=F, C=T -> False (B가 결과 결정)
// 5. A=T, B=F, C=T -> True  (C가 결과 결정)
// 6. A=T, B=F, C=F -> False (C가 결과 결정)
```

## Coverage Analysis Workflow

### Step-by-Step Process

#### 1. Run Coverage Analysis

프레임워크별 커버리지 실행 명령어:

```bash
# Jest
npm test -- --coverage
npx jest --coverage --collectCoverageFrom='src/**/*.ts'

# Vitest
npx vitest --coverage
npx vitest --coverage --reporter=html

# JUnit + JaCoCo (Maven)
mvn clean test jacoco:report

# JUnit + JaCoCo (Gradle)
./gradlew test jacocoTestReport

# pytest
pytest --cov=src --cov-report=html --cov-report=term

# Go
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html
```

#### 2. Analyze Coverage Report

리포트를 열어 다음을 확인합니다:

```
File                  | % Stmts | % Branch | % Funcs | % Lines | Uncovered Lines
----------------------|---------|----------|---------|---------|----------------
userService.ts        |   85.71 |    75.00 |  100.00 |   85.71 | 45-48
orderService.ts       |   60.00 |    50.00 |   80.00 |   60.00 | 23,67-72,89
paymentService.ts     |   95.00 |    90.00 |  100.00 |   95.00 | 112
----------------------|---------|----------|---------|---------|----------------
All files             |   80.24 |    71.67 |   93.33 |   80.24 |
```

**분석 포인트:**
1. 전체 커버리지가 목표(80%)에 도달했는가?
2. 특정 파일이 유독 낮은가? (orderService.ts: 60%)
3. Branch coverage가 낮은 곳은? (복잡한 조건문 미검증)
4. Uncovered Lines는 어디인가? (실제 코드 확인 필요)

#### 3. Identify Uncovered Critical Paths

커버되지 않은 코드 중 우선순위를 정합니다:

```typescript
// orderService.ts의 uncovered lines 23, 67-72, 89 확인

// Line 23: 에러 처리 (중요!)
if (!user.isVerified) {
  throw new UnverifiedUserError();  // ❗ 테스트 필요!
}

// Lines 67-72: 복잡한 비즈니스 로직 (중요!)
if (order.total > 1000 && user.tier === 'premium') {
  discount = calculatePremiumDiscount(order);  // ❗ 테스트 필요!
} else if (order.items.length > 10) {
  discount = calculateBulkDiscount(order);
}

// Line 89: 로깅 (덜 중요)
logger.debug('Order processed', { orderId });  // ⚠️ 낮은 우선순위
```

#### 4. Prioritize Test Cases

우선순위 결정 기준:

| 우선순위 | 코드 유형 | 예시 | 커버리지 목표 |
|---------|----------|------|--------------|
| **P1 - Critical** | 비즈니스 로직, 에러 처리, 보안 | 결제 로직, 인증, 권한 검증 | 95%+ |
| **P2 - High** | 데이터 변환, 유효성 검증 | DTO 매핑, 입력 검증 | 85%+ |
| **P3 - Medium** | 유틸리티, 헬퍼 함수 | 날짜 포맷, 문자열 처리 | 75%+ |
| **P4 - Low** | 로깅, 설정, 상수 | Logger 호출, config 로드 | 0-50% |

#### 5. Write Tests for Uncovered Paths

우선순위에 따라 테스트 추가:

```typescript
// P1: Critical - 에러 처리 테스트 추가
describe('createOrder', () => {
  it('should throw UnverifiedUserError when user is not verified', () => {
    // Given
    const unverifiedUser = createUser({ isVerified: false });

    // When & Then
    expect(() => orderService.createOrder(unverifiedUser, order))
      .toThrow(UnverifiedUserError);
  });
});

// P1: Critical - 프리미엄 할인 로직 테스트
it('should apply premium discount for high-value orders', () => {
  // Given
  const premiumUser = createUser({ tier: 'premium' });
  const order = createOrder({ total: 1500 });

  // When
  const result = orderService.createOrder(premiumUser, order);

  // Then
  expect(result.discount).toBeGreaterThan(0);
  expect(result.finalPrice).toBeLessThan(order.total);
});
```

#### 6. Don't Chase 100% Coverage

**80-85% 이후 수익 체감:**
- 남은 15-20%는 대부분 P4 (Low priority) 코드
- 100% 달성에 드는 비용 > 얻는 가치
- 엣지 케이스를 과도하게 테스트하는 것은 비효율적

**테스트하지 않아도 되는 것:**
- 프레임워크 내부 동작
- 간단한 getter/setter (복잡한 로직 없는 경우)
- 자동 생성된 코드
- 설정 파일, 상수 정의
- 로깅만 하는 코드

## Test Case Design Techniques

### 1. Equivalence Partitioning

입력 도메인을 동등한 클래스로 나누어 각 클래스에서 대표값을 테스트합니다.

```typescript
// 나이 검증 함수
function validateAge(age: number): boolean {
  return age >= 0 && age <= 150;
}

// Equivalence Classes:
// 1. Invalid: age < 0
// 2. Valid: 0 <= age <= 150
// 3. Invalid: age > 150

describe('validateAge', () => {
  // Class 1: Invalid (negative)
  it('should reject negative age', () => {
    expect(validateAge(-1)).toBe(false);
    expect(validateAge(-100)).toBe(false);
  });

  // Class 2: Valid
  it('should accept valid age', () => {
    expect(validateAge(0)).toBe(true);
    expect(validateAge(25)).toBe(true);
    expect(validateAge(150)).toBe(true);
  });

  // Class 3: Invalid (too high)
  it('should reject age over 150', () => {
    expect(validateAge(151)).toBe(false);
    expect(validateAge(200)).toBe(false);
  });
});
```

### 2. Boundary Value Analysis (BVA)

경계값과 그 근처 값을 집중적으로 테스트합니다.

```typescript
// 할인율 계산: 100 미만 0%, 100-999 10%, 1000 이상 20%
function getDiscountRate(amount: number): number {
  if (amount < 100) return 0;
  if (amount < 1000) return 0.1;
  return 0.2;
}

describe('getDiscountRate - Boundary Value Analysis', () => {
  describe('boundary at 100', () => {
    it('should return 0% just below boundary', () => {
      expect(getDiscountRate(99)).toBe(0);
    });

    it('should return 10% at boundary', () => {
      expect(getDiscountRate(100)).toBe(0.1);
    });

    it('should return 10% just above boundary', () => {
      expect(getDiscountRate(101)).toBe(0.1);
    });
  });

  describe('boundary at 1000', () => {
    it('should return 10% just below boundary', () => {
      expect(getDiscountRate(999)).toBe(0.1);
    });

    it('should return 20% at boundary', () => {
      expect(getDiscountRate(1000)).toBe(0.2);
    });

    it('should return 20% just above boundary', () => {
      expect(getDiscountRate(1001)).toBe(0.2);
    });
  });
});
```

### 3. Decision Table Testing

여러 조건의 조합을 체계적으로 테스트합니다.

```typescript
// 대출 승인 로직
function approveLoan(
  creditScore: number,
  income: number,
  hasCollateral: boolean
): boolean {
  if (creditScore >= 700 && income >= 50000) return true;
  if (creditScore >= 650 && income >= 70000 && hasCollateral) return true;
  return false;
}

// Decision Table:
// | Credit ≥700 | Income ≥50k | Income ≥70k | Collateral | Result |
// |-------------|-------------|-------------|------------|--------|
// |      T      |      T      |      -      |     -      |  PASS  |
// |      T      |      F      |      -      |     -      |  FAIL  |
// |      F      |      -      |      T      |     T      |  PASS  |
// |      F      |      -      |      T      |     F      |  FAIL  |
// |      F      |      -      |      F      |     -      |  FAIL  |

describe('approveLoan - Decision Table', () => {
  it('should approve: high credit + sufficient income', () => {
    expect(approveLoan(750, 60000, false)).toBe(true);
  });

  it('should reject: high credit + low income', () => {
    expect(approveLoan(750, 40000, false)).toBe(false);
  });

  it('should approve: medium credit + high income + collateral', () => {
    expect(approveLoan(680, 75000, true)).toBe(true);
  });

  it('should reject: medium credit + high income + no collateral', () => {
    expect(approveLoan(680, 75000, false)).toBe(false);
  });

  it('should reject: medium credit + low income', () => {
    expect(approveLoan(680, 45000, true)).toBe(false);
  });
});
```

### 4. State Transition Testing

상태 머신의 전이를 테스트합니다.

```typescript
// 주문 상태 머신
enum OrderState {
  CREATED = 'CREATED',
  PAID = 'PAID',
  SHIPPED = 'SHIPPED',
  DELIVERED = 'DELIVERED',
  CANCELLED = 'CANCELLED'
}

class Order {
  state: OrderState = OrderState.CREATED;

  pay(): void {
    if (this.state !== OrderState.CREATED) {
      throw new Error('Invalid transition');
    }
    this.state = OrderState.PAID;
  }

  ship(): void {
    if (this.state !== OrderState.PAID) {
      throw new Error('Invalid transition');
    }
    this.state = OrderState.SHIPPED;
  }

  cancel(): void {
    if (this.state === OrderState.DELIVERED) {
      throw new Error('Cannot cancel delivered order');
    }
    this.state = OrderState.CANCELLED;
  }
}

// State Transition Diagram:
// CREATED --pay()--> PAID --ship()--> SHIPPED --deliver()--> DELIVERED
//    |                 |                 |
//    +---cancel()------+-----cancel()----+
//                      (not from DELIVERED)

describe('Order State Transitions', () => {
  it('should transition from CREATED to PAID', () => {
    const order = new Order();
    order.pay();
    expect(order.state).toBe(OrderState.PAID);
  });

  it('should transition from PAID to SHIPPED', () => {
    const order = new Order();
    order.pay();
    order.ship();
    expect(order.state).toBe(OrderState.SHIPPED);
  });

  it('should allow cancel from CREATED', () => {
    const order = new Order();
    order.cancel();
    expect(order.state).toBe(OrderState.CANCELLED);
  });

  it('should reject invalid transition (ship before pay)', () => {
    const order = new Order();
    expect(() => order.ship()).toThrow('Invalid transition');
  });

  it('should test full happy path', () => {
    const order = new Order();
    order.pay();
    order.ship();
    // order.deliver();
    expect(order.state).toBe(OrderState.SHIPPED);
  });
});
```

## Test Case Documentation Template

체계적인 테스트 케이스 문서화:

```markdown
### TC-001: User Registration with Valid Data

- **Precondition**:
  - Database is empty
  - Email service is available

- **Input**:
  ```json
  {
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "name": "John Doe"
  }
  ```

- **Action**:
  1. POST /api/users/register with input data
  2. Verify email sent
  3. Click verification link

- **Expected**:
  - HTTP 201 Created
  - User saved to database with hashed password
  - Verification email sent
  - User status = 'PENDING_VERIFICATION'

- **Category**: Integration
- **Priority**: P1
- **Automation**: ✅ Automated

---

### TC-002: User Registration with Duplicate Email

- **Precondition**:
  - User with email "existing@example.com" already exists

- **Input**:
  ```json
  {
    "email": "existing@example.com",
    "password": "AnotherPass456!",
    "name": "Jane Doe"
  }
  ```

- **Action**:
  1. POST /api/users/register with duplicate email

- **Expected**:
  - HTTP 409 Conflict
  - Error message: "Email already registered"
  - No new user created in database

- **Category**: Integration
- **Priority**: P1
- **Automation**: ✅ Automated
```

## Coverage Commands by Framework

### Jest (JavaScript/TypeScript)

```bash
# 기본 커버리지
npm test -- --coverage

# 특정 디렉토리만
npx jest --coverage --collectCoverageFrom='src/**/*.ts'

# 임계값 설정 (jest.config.js)
module.exports = {
  coverageThreshold: {
    global: {
      branches: 75,
      functions: 90,
      lines: 80,
      statements: 80
    },
    './src/critical/': {
      branches: 90,
      functions: 95,
      lines: 95,
      statements: 95
    }
  }
};

# HTML 리포트
npx jest --coverage --coverageReporters=html
# 리포트 위치: coverage/index.html
```

### Vitest (JavaScript/TypeScript)

```bash
# 기본 커버리지 (v8 사용)
npx vitest --coverage

# Istanbul 사용
npx vitest --coverage --coverage.provider=istanbul

# UI 모드
npx vitest --coverage --ui

# 설정 (vite.config.ts)
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json'],
      exclude: ['**/node_modules/**', '**/test/**'],
      thresholds: {
        lines: 80,
        functions: 90,
        branches: 75,
        statements: 80
      }
    }
  }
});
```

### JUnit + JaCoCo (Java)

```bash
# Maven
mvn clean test jacoco:report
# 리포트: target/site/jacoco/index.html

# Gradle
./gradlew test jacocoTestReport
# 리포트: build/reports/jacoco/test/html/index.html

# 임계값 설정 (Maven pom.xml)
<plugin>
  <groupId>org.jacoco</groupId>
  <artifactId>jacoco-maven-plugin</artifactId>
  <executions>
    <execution>
      <id>check</id>
      <goals>
        <goal>check</goal>
      </goals>
      <configuration>
        <rules>
          <rule>
            <element>PACKAGE</element>
            <limits>
              <limit>
                <counter>LINE</counter>
                <value>COVEREDRATIO</value>
                <minimum>0.80</minimum>
              </limit>
            </limits>
          </rule>
        </rules>
      </configuration>
    </execution>
  </executions>
</plugin>

# Gradle (build.gradle)
jacocoTestCoverageVerification {
    violationRules {
        rule {
            limit {
                minimum = 0.8
            }
        }
    }
}
```

### pytest-cov (Python)

```bash
# 기본 커버리지
pytest --cov=src

# HTML 리포트
pytest --cov=src --cov-report=html
# 리포트: htmlcov/index.html

# 터미널 + HTML
pytest --cov=src --cov-report=term --cov-report=html

# Missing lines 표시
pytest --cov=src --cov-report=term-missing

# 임계값 설정 (.coveragerc 또는 pyproject.toml)
# .coveragerc
[report]
fail_under = 80

# pyproject.toml
[tool.coverage.report]
fail_under = 80

# Branch coverage
pytest --cov=src --cov-branch
```

### Go

```bash
# 기본 커버리지
go test -cover ./...

# 프로파일 생성
go test -coverprofile=coverage.out ./...

# HTML 리포트
go tool cover -html=coverage.out -o coverage.html

# 함수별 커버리지
go tool cover -func=coverage.out

# 패키지별 커버리지
go test -coverprofile=coverage.out ./...
go tool cover -func=coverage.out | grep total

# CI/CD에서 임계값 확인
total=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//')
if (( $(echo "$total < 80" | bc -l) )); then
  echo "Coverage $total% is below 80%"
  exit 1
fi
```

## What NOT to Test

불필요한 테스트로 시간을 낭비하지 마세요.

### 1. Framework/Library Internals

```typescript
// ❌ 테스트 불필요: React Hook이 제대로 동작하는지
it('useState should work', () => {
  const [count, setCount] = useState(0);
  setCount(1);
  expect(count).toBe(1);  // React 자체 테스트, 의미 없음
});

// ✅ 테스트 필요: 우리 컴포넌트가 제대로 동작하는지
it('should increment counter when button clicked', () => {
  render(<Counter />);
  fireEvent.click(screen.getByRole('button'));
  expect(screen.getByText('Count: 1')).toBeInTheDocument();
});
```

### 2. Third-party Library Behavior

```typescript
// ❌ 테스트 불필요: axios가 제대로 HTTP 요청하는지
it('axios should make GET request', async () => {
  const response = await axios.get('https://api.example.com');
  expect(response.status).toBe(200);  // axios 테스트, 의미 없음
});

// ✅ 테스트 필요: 우리 서비스가 API를 올바르게 사용하는지
it('should fetch user data from API', async () => {
  const mockAxios = jest.spyOn(axios, 'get').mockResolvedValue({
    data: { id: '123', name: 'John' }
  });

  const user = await userService.getUser('123');

  expect(mockAxios).toHaveBeenCalledWith('/api/users/123');
  expect(user.name).toBe('John');
});
```

### 3. Simple Getters/Setters (Without Logic)

```typescript
class User {
  private name: string;

  // ❌ 테스트 불필요: 단순 getter/setter
  getName(): string {
    return this.name;
  }

  setName(name: string): void {
    this.name = name;
  }

  // ✅ 테스트 필요: 로직이 있는 setter
  setEmail(email: string): void {
    if (!email.includes('@')) {
      throw new Error('Invalid email');
    }
    this.email = email;
  }
}
```

### 4. Configuration Files and Constants

```typescript
// config.ts
// ❌ 테스트 불필요
export const CONFIG = {
  API_URL: 'https://api.example.com',
  TIMEOUT: 5000,
  MAX_RETRIES: 3
};

// ✅ 테스트 필요: 설정을 사용하는 로직
class ApiClient {
  constructor(private config: Config) {}

  async fetch(url: string): Promise<Response> {
    // 이 로직은 테스트 필요
    const fullUrl = `${this.config.API_URL}${url}`;
    return await fetchWithRetry(fullUrl, this.config.MAX_RETRIES);
  }
}
```

### 5. Generated Code

```typescript
// Auto-generated by tool
// ❌ 테스트 불필요
export interface UserDTO {
  id: string;
  name: string;
  email: string;
}

// ✅ 테스트 필요: 수동으로 작성한 매핑 로직
export function toUserDTO(user: User): UserDTO {
  return {
    id: user.id,
    name: user.getFullName(),  // 로직 있음
    email: user.email.toLowerCase()  // 변환 로직 있음
  };
}
```

### 6. Trivial Code

```typescript
// ❌ 테스트 불필요
function add(a: number, b: number): number {
  return a + b;  // 너무 단순
}

// ✅ 테스트 필요
function calculateTotalPrice(items: CartItem[]): number {
  return items.reduce((total, item) => {
    const discount = item.discount || 0;
    const tax = item.taxRate || 0;
    const itemPrice = item.price * item.quantity;
    const discountedPrice = itemPrice * (1 - discount);
    const finalPrice = discountedPrice * (1 + tax);
    return total + finalPrice;
  }, 0);
}
```

## Coverage Best Practices

### 1. Set Realistic Thresholds

```javascript
// jest.config.js
module.exports = {
  coverageThreshold: {
    global: {
      statements: 80,
      branches: 75,
      functions: 90,
      lines: 80
    },
    // 중요한 모듈은 더 높게
    './src/core/payment/': {
      statements: 95,
      branches: 90,
      functions: 100,
      lines: 95
    },
    // 유틸리티는 낮춰도 OK
    './src/utils/logger/': {
      statements: 50,
      branches: 50,
      functions: 60,
      lines: 50
    }
  }
};
```

### 2. Focus on Critical Paths

```typescript
// 중요도에 따른 테스트 투자

// ✅ High priority: 결제, 인증, 보안
describe('PaymentService - Critical', () => {
  // 모든 엣지 케이스 테스트
  it('should handle payment gateway timeout', () => { /* ... */ });
  it('should rollback on partial failure', () => { /* ... */ });
  it('should prevent double charging', () => { /* ... */ });
  // ... 20+ test cases
});

// ✅ Medium priority: 비즈니스 로직
describe('OrderService', () => {
  // 주요 시나리오만
  it('should create order', () => { /* ... */ });
  it('should calculate total correctly', () => { /* ... */ });
  // ... 5-10 test cases
});

// ✅ Low priority: 유틸리티
describe('formatDate', () => {
  // 대표 케이스만
  it('should format date to ISO string', () => { /* ... */ });
  // ... 1-3 test cases
});
```

### 3. Exclude Non-Critical Files

```javascript
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',           // 타입 정의
    '!src/**/*.stories.tsx',    // Storybook
    '!src/**/*.test.{ts,tsx}',  // 테스트 파일
    '!src/index.ts',            // 엔트리 포인트
    '!src/setupTests.ts',       // 테스트 설정
    '!src/mocks/**',            // Mock 데이터
    '!src/constants/**',        // 상수
  ]
};
```

## Conclusion

효과적인 커버리지 전략:

1. **측정 자동화**: CI/CD에서 자동으로 커버리지 측정 및 리포트 생성
2. **현실적 목표**: 전체 80%, 핵심 로직 95%, 유틸리티 70%
3. **우선순위 기반**: P1(Critical) 먼저 테스트, P4(Low)는 생략 가능
4. **테스트 설계 기법**: Boundary Value, Decision Table 등 체계적 접근
5. **불필요한 테스트 배제**: 프레임워크 내부, 단순 코드는 테스트 생략

**핵심 원칙: 커버리지는 목표가 아니라 품질 지표입니다.**
- 100% 커버리지 = 100% 버그 없음이 아님
- 80% 커버리지 + 올바른 테스트 > 100% 커버리지 + 형식적 테스트
- 테스트 코드도 유지보수 비용이 드는 자산임을 명심
