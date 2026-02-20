# Refactoring Catalog

안전하고 체계적인 리팩토링을 위한 패턴 카탈로그입니다.

## Safe Refactoring Procedure

모든 리팩토링은 다음 5단계 절차를 따릅니다:

1. **테스트 통과 확인**: 리팩토링 전 모든 테스트가 통과하는지 확인
2. **하나씩 변경**: 한 번에 하나의 리팩토링만 수행 (Big Bang 금지)
3. **테스트 실행**: 각 변경 후 즉시 테스트 실행
4. **커밋**: 테스트 통과 후 즉시 커밋 (롤백 가능하도록)
5. **실패 시 되돌리기**: 테스트 실패 시 즉시 revert하고 원인 분석

**Golden Rule**: 리팩토링 중에는 기능을 추가하지 않습니다. 기능 추가와 리팩토링을 분리하세요.

---

## Refactoring Patterns

### 1. Extract Method

**When to Apply**:
- 메서드가 30줄 이상
- 주석이 필요한 코드 블록
- 중복된 코드 패턴
- 한 메서드가 여러 수준의 추상화를 섞어 사용

**Before**:
```javascript
function printOwing(invoice) {
  let outstanding = 0;

  console.log("***********************");
  console.log("**** Customer Owes ****");
  console.log("***********************");

  // Calculate outstanding
  for (const order of invoice.orders) {
    outstanding += order.amount;
  }

  console.log(`name: ${invoice.customer}`);
  console.log(`amount: ${outstanding}`);
}
```

**After**:
```javascript
function printOwing(invoice) {
  printBanner();
  const outstanding = calculateOutstanding(invoice);
  printDetails(invoice, outstanding);
}

function printBanner() {
  console.log("***********************");
  console.log("**** Customer Owes ****");
  console.log("***********************");
}

function calculateOutstanding(invoice) {
  return invoice.orders.reduce((sum, order) => sum + order.amount, 0);
}

function printDetails(invoice, outstanding) {
  console.log(`name: ${invoice.customer}`);
  console.log(`amount: ${outstanding}`);
}
```

**Safety Steps**:
1. 추출할 코드 블록 선택
2. 블록이 사용하는 변수 식별 (파라미터가 됨)
3. 블록이 수정하는 변수 식별 (반환값이 됨)
4. 새 메서드 생성 및 코드 복사
5. 원본 코드를 메서드 호출로 교체
6. 테스트 실행

**Risk Level**: Low

---

### 2. Extract Class

**When to Apply**:
- 클래스가 300줄 이상 또는 10개 이상 메서드
- 클래스의 일부 데이터/메서드가 함께 변경됨
- Data Clumps (같은 필드 그룹 반복)
- God Object (한 클래스가 너무 많은 책임)

**Before**:
```python
class Person:
    def __init__(self, name, office_area_code, office_number):
        self.name = name
        self.office_area_code = office_area_code
        self.office_number = office_number

    def get_telephone_number(self):
        return f"({self.office_area_code}) {self.office_number}"
```

**After**:
```python
class Person:
    def __init__(self, name, office_area_code, office_number):
        self.name = name
        self.telephone = TelephoneNumber(office_area_code, office_number)

    def get_telephone_number(self):
        return self.telephone.get_number()

class TelephoneNumber:
    def __init__(self, area_code, number):
        self.area_code = area_code
        self.number = number

    def get_number(self):
        return f"({self.area_code}) {self.number}"
```

**Safety Steps**:
1. 추출할 책임 식별 (관련 필드와 메서드)
2. 새 클래스 생성 (비어 있음)
3. 필드를 하나씩 이동 (Move Field)
4. 메서드를 하나씩 이동 (Move Method)
5. 각 이동 후 테스트 실행
6. 새 클래스의 인터페이스 검토 및 개선

**Risk Level**: Medium

---

### 3. Move Method

**When to Apply**:
- Feature Envy (다른 클래스의 데이터를 과도하게 사용)
- 메서드가 자신의 클래스보다 다른 클래스와 더 많이 상호작용
- 클래스 간 책임 재분배 필요

**Before**:
```java
class Account {
    private AccountType type;
    private int daysOverdrawn;

    double overdraftCharge() {
        if (type.isPremium()) {
            double result = 10;
            if (daysOverdrawn > 7) {
                result += (daysOverdrawn - 7) * 0.85;
            }
            return result;
        } else {
            return daysOverdrawn * 1.75;
        }
    }
}
```

**After**:
```java
class Account {
    private AccountType type;
    private int daysOverdrawn;

    double overdraftCharge() {
        return type.overdraftCharge(daysOverdrawn);
    }
}

class AccountType {
    double overdraftCharge(int daysOverdrawn) {
        if (this.isPremium()) {
            double result = 10;
            if (daysOverdrawn > 7) {
                result += (daysOverdrawn - 7) * 0.85;
            }
            return result;
        } else {
            return daysOverdrawn * 1.75;
        }
    }
}
```

**Safety Steps**:
1. 대상 클래스에 새 메서드 생성
2. 원본 메서드의 코드를 복사
3. 필요한 파라미터 전달하도록 수정
4. 원본 메서드를 위임 메서드로 변경
5. 테스트 실행
6. 모든 호출자가 새 메서드를 호출하도록 변경
7. 원본 메서드 제거

**Risk Level**: Medium

---

### 4. Replace Conditional with Polymorphism

**When to Apply**:
- 타입 코드 기반 switch/if 체인
- 동일한 조건 분기가 여러 곳에 반복
- 새로운 타입 추가 시 여러 곳 수정 필요 (Open/Closed 위반)

**Before**:
```typescript
class Bird {
    constructor(public type: string) {}

    getSpeed(): number {
        switch (this.type) {
            case 'european':
                return 35;
            case 'african':
                return 40;
            case 'norwegian-blue':
                return this.isNailed ? 0 : 10;
            default:
                throw new Error('Unknown bird type');
        }
    }
}
```

**After**:
```typescript
abstract class Bird {
    abstract getSpeed(): number;
}

class European extends Bird {
    getSpeed(): number {
        return 35;
    }
}

class African extends Bird {
    getSpeed(): number {
        return 40;
    }
}

class NorwegianBlue extends Bird {
    constructor(private isNailed: boolean) {
        super();
    }

    getSpeed(): number {
        return this.isNailed ? 0 : 10;
    }
}
```

**Safety Steps**:
1. 추상 클래스 또는 인터페이스 생성
2. 각 조건 분기마다 하위 클래스 생성
3. 하위 클래스에 해당 분기 로직 이동
4. 한 분기씩 이동하며 테스트
5. 모든 분기 이동 후 조건문 제거
6. 팩토리 메서드로 객체 생성 캡슐화

**Risk Level**: High

---

### 5. Introduce Parameter Object

**When to Apply**:
- 파라미터 리스트가 4개 이상
- 같은 파라미터 그룹이 여러 메서드에 반복
- Data Clumps (데이터 덩어리)

**Before**:
```javascript
function amountInvoiced(startDate, endDate) { ... }
function amountReceived(startDate, endDate) { ... }
function amountOverdue(startDate, endDate) { ... }
```

**After**:
```javascript
class DateRange {
    constructor(startDate, endDate) {
        this.startDate = startDate;
        this.endDate = endDate;
    }
}

function amountInvoiced(dateRange) { ... }
function amountReceived(dateRange) { ... }
function amountOverdue(dateRange) { ... }
```

**Safety Steps**:
1. 파라미터 객체 클래스 생성
2. 생성자에 파라미터 추가
3. 메서드에 새 파라미터 추가 (기존 파라미터 유지)
4. 메서드 본문을 새 파라미터 사용하도록 수정
5. 테스트 실행
6. 기존 파라미터 제거
7. 호출자를 모두 새 방식으로 변경

**Risk Level**: Low

---

### 6. Replace Magic Number with Constant

**When to Apply**:
- 숫자 리터럴의 의미가 명확하지 않음
- 같은 숫자가 여러 곳에서 사용됨
- 숫자가 변경될 가능성이 있음

**Before**:
```python
def calculate_total(quantity, price):
    base_price = quantity * price
    if base_price > 1000:
        return base_price * 0.95  # What's 0.95?
    else:
        return base_price * 0.98  # What's 0.98?
```

**After**:
```python
BULK_ORDER_THRESHOLD = 1000
BULK_ORDER_DISCOUNT = 0.95
REGULAR_DISCOUNT = 0.98

def calculate_total(quantity, price):
    base_price = quantity * price
    if base_price > BULK_ORDER_THRESHOLD:
        return base_price * BULK_ORDER_DISCOUNT
    else:
        return base_price * REGULAR_DISCOUNT
```

**Safety Steps**:
1. 상수 선언 (의미 있는 이름)
2. 한 곳의 매직 넘버를 상수로 교체
3. 테스트 실행
4. 모든 매직 넘버를 상수로 교체
5. 관련 상수를 그룹화 (enum, config 객체)

**Risk Level**: Low

---

### 7. Extract Interface

**When to Apply**:
- 클래스의 일부 기능만 클라이언트가 사용
- 구체 클래스에 대한 의존성을 제거하고 싶음
- 여러 구현을 바꿔 끼우고 싶음 (Strategy Pattern)
- 테스트에서 Mock 객체 사용하고 싶음

**Before**:
```java
class EmailNotifier {
    void send(String message) {
        // Send email
    }
}

class OrderService {
    private EmailNotifier notifier;

    void placeOrder(Order order) {
        // ...
        notifier.send("Order placed");
    }
}
```

**After**:
```java
interface Notifier {
    void send(String message);
}

class EmailNotifier implements Notifier {
    public void send(String message) {
        // Send email
    }
}

class SmsNotifier implements Notifier {
    public void send(String message) {
        // Send SMS
    }
}

class OrderService {
    private Notifier notifier;  // Interface dependency

    void placeOrder(Order order) {
        // ...
        notifier.send("Order placed");
    }
}
```

**Safety Steps**:
1. 인터페이스 생성 (비어 있음)
2. 필요한 메서드 시그니처를 인터페이스에 추가
3. 구체 클래스가 인터페이스를 구현하도록 선언
4. 클라이언트 코드를 인터페이스 타입 사용하도록 변경
5. 테스트 실행
6. 필요하면 추가 구현 클래스 생성

**Risk Level**: Low

---

### 8. Decompose Conditional

**When to Apply**:
- 복잡한 if/else 조건문
- 조건식이 길고 이해하기 어려움
- 조건과 결과의 의도가 명확하지 않음

**Before**:
```javascript
if (date.before(SUMMER_START) || date.after(SUMMER_END)) {
    charge = quantity * winterRate + winterServiceCharge;
} else {
    charge = quantity * summerRate;
}
```

**After**:
```javascript
if (isSummer(date)) {
    charge = summerCharge(quantity);
} else {
    charge = winterCharge(quantity);
}

function isSummer(date) {
    return !date.before(SUMMER_START) && !date.after(SUMMER_END);
}

function summerCharge(quantity) {
    return quantity * summerRate;
}

function winterCharge(quantity) {
    return quantity * winterRate + winterServiceCharge;
}
```

**Safety Steps**:
1. 조건식을 별도 함수로 추출 (의미 있는 이름)
2. then 블록을 별도 함수로 추출
3. else 블록을 별도 함수로 추출
4. 각 추출 후 테스트 실행

**Risk Level**: Low

---

### 9. Replace Temp with Query

**When to Apply**:
- 임시 변수가 복잡한 표현식의 결과를 저장
- 임시 변수가 한 번만 할당되고 변경되지 않음
- 표현식을 여러 곳에서 사용하고 싶음

**Before**:
```typescript
function getPrice() {
    const basePrice = quantity * itemPrice;
    const discountFactor = basePrice > 1000 ? 0.95 : 0.98;
    return basePrice * discountFactor;
}
```

**After**:
```typescript
function getPrice() {
    return getBasePrice() * getDiscountFactor();
}

function getBasePrice() {
    return quantity * itemPrice;
}

function getDiscountFactor() {
    return getBasePrice() > 1000 ? 0.95 : 0.98;
}
```

**Safety Steps**:
1. 임시 변수가 한 번만 할당되는지 확인
2. 할당 표현식을 별도 메서드로 추출
3. 임시 변수를 메서드 호출로 교체
4. 테스트 실행
5. 인라인 최적화는 컴파일러에 맡김 (가독성 우선)

**Risk Level**: Low

**Prerequisites**: 임시 변수가 여러 번 할당되면 먼저 Split Temporary Variable 리팩토링 필요

---

### 10. Inline Method

**When to Apply**:
- 메서드 본문이 메서드 이름만큼이나 명확함
- 과도한 간접 참조 (indirection)
- 잘못된 위임 (메서드가 단순히 다른 메서드를 호출만 함)
- 리팩토링 후 불필요해진 메서드

**Before**:
```python
def get_rating(driver):
    return 2 if is_more_than_five_late_deliveries(driver) else 1

def is_more_than_five_late_deliveries(driver):
    return driver.late_deliveries > 5
```

**After**:
```python
def get_rating(driver):
    return 2 if driver.late_deliveries > 5 else 1
```

**Safety Steps**:
1. 메서드가 다형성이 아닌지 확인 (하위 클래스에서 오버라이드되지 않음)
2. 모든 호출자를 찾기
3. 각 호출을 메서드 본문으로 교체
4. 테스트 실행
5. 메서드 정의 제거

**Risk Level**: Low

**Warning**: 메서드가 public API거나 여러 곳에서 호출되면 신중히 판단. 가독성이 떨어지면 인라인하지 말 것.

---

### 11. Pull Up / Push Down

**Pull Up Method**: 하위 클래스의 동일한 메서드를 상위 클래스로 올림

**When to Apply**:
- 여러 하위 클래스가 동일한 메서드를 가짐
- 중복 제거 (DRY)
- 공통 인터페이스 제공

**Before**:
```java
class Salesman extends Employee {
    String getName() { return name; }
}

class Engineer extends Employee {
    String getName() { return name; }
}
```

**After**:
```java
class Employee {
    String getName() { return name; }
}

class Salesman extends Employee { }
class Engineer extends Employee { }
```

**Push Down Method**: 상위 클래스의 메서드를 일부 하위 클래스로 내림

**When to Apply**:
- 상위 클래스의 메서드가 일부 하위 클래스에서만 사용됨
- Speculative Generality (불필요한 일반화) 제거

**Safety Steps (Pull Up)**:
1. 하위 클래스 메서드들이 동일한지 검사
2. 메서드 시그니처가 다르면 먼저 통일
3. 상위 클래스에 메서드 생성
4. 하위 클래스 메서드를 하나씩 제거
5. 각 제거 후 테스트 실행

**Risk Level**: Medium

---

### 12. Replace Inheritance with Composition

**When to Apply**:
- 하위 클래스가 상위 클래스 인터페이스의 일부만 사용
- IS-A 관계가 아닌 HAS-A 관계가 더 적합
- Liskov Substitution Principle 위반 (하위 클래스가 상위 클래스를 대체 불가)
- 다중 상속 문제 회피

**Before**:
```typescript
class Stack extends ArrayList {
    push(value: any) {
        this.add(value);
    }

    pop(): any {
        return this.remove(this.size() - 1);
    }
}
// Problem: Stack은 ArrayList의 모든 메서드 노출 (get, set, add at index 등)
// 클라이언트가 stack[5] = value로 스택 불변성을 깨뜨릴 수 있음
```

**After**:
```typescript
class Stack {
    private items: ArrayList = new ArrayList();

    push(value: any) {
        this.items.add(value);
    }

    pop(): any {
        return this.items.remove(this.items.size() - 1);
    }

    size(): number {
        return this.items.size();
    }
}
// 캡슐화: Stack의 공개 인터페이스만 노출
```

**Safety Steps**:
1. 하위 클래스에 상위 클래스 타입의 필드 추가
2. 하위 클래스 메서드들이 이 필드를 통해 상위 클래스 기능 사용하도록 수정
3. 테스트 실행
4. 상속 관계 제거
5. 불필요하게 노출된 메서드 제거

**Risk Level**: High

**Prerequisites**:
- 하위 클래스가 상위 클래스의 protected 멤버에 접근하면 먼저 public 메서드로 추출 필요
- 클라이언트가 상위 타입으로 캐스팅하는 경우 인터페이스 추출 먼저 수행

---

## Anti-Patterns to Avoid

리팩토링 시 피해야 할 실수들:

### 1. Premature Abstraction

**Problem**: 중복이 2번만 나타났는데 추상화를 시도
**Impact**: 불필요한 복잡도 증가, YAGNI 위반
**Better Approach**:
- **Rule of Three**: 중복이 3번 나타날 때 추상화 시작
- 패턴이 명확해질 때까지 기다림
- 잘못된 추상화는 중복보다 나쁨 (Sandi Metz)

**Example**:
```javascript
// Bad: 2번 중복으로 추상화
function processUserA() { validateEmail(); saveToDb(); }
function processUserB() { validateEmail(); saveToDb(); }
// 즉시 BaseUserProcessor 클래스 생성 - 너무 이름

// Good: 3번째 중복에서 추상화
// 세 경우를 보고 나서야 공통 패턴이 명확해짐
```

### 2. Big Bang Refactoring

**Problem**: 여러 리팩토링을 한 번에 수행
**Impact**:
- 테스트 실패 시 원인 파악 어려움
- 롤백이 어려움
- 리뷰가 불가능
- 병합 충돌 위험

**Better Approach**:
- 한 번에 하나의 리팩토링만 수행
- 각 단계마다 테스트 실행
- 각 리팩토링마다 별도 커밋
- 작은 단계로 나누어 점진적 개선

**Example**:
```
# Bad: 한 커밋에 모든 변경
- Extract Method 5개
- Rename Variables 10개
- Extract Class 2개
- 테스트 실패 - 어디서 잘못됐는지 모름

# Good: 단계별 커밋
Commit 1: Extract calculateTotal method
Commit 2: Rename price → unitPrice
Commit 3: Extract TaxCalculator class
각 커밋마다 테스트 통과 확인
```

### 3. Refactoring Without Tests

**Problem**: 테스트 없이 리팩토링 시작
**Impact**:
- 기능이 깨졌는지 확인 불가
- 회귀 버그 발생
- 자신감 부족으로 리팩토링 포기

**Better Approach**:
- 리팩토링 전 테스트가 반드시 존재해야 함
- 테스트가 없으면 먼저 Characterization Test 작성
- 리팩토링은 Red → Green → Refactor 사이클의 마지막 단계
- Legacy Code의 경우: Seam 찾기 → 테스트 작성 → 리팩토링

**Example**:
```python
# 레거시 코드 - 테스트 없음
def calculate_price(item):
    # 복잡한 로직 100줄
    ...

# Step 1: Characterization Test 작성 (현재 동작 캡처)
def test_calculate_price():
    assert calculate_price(item1) == 99.50  # 현재 결과값
    assert calculate_price(item2) == 150.00

# Step 2: 이제 안전하게 리팩토링 가능
```

### 4. Over-engineering

**Problem**: 필요 이상으로 많은 디자인 패턴 적용
**Impact**:
- 과도한 간접 참조로 코드 이해 어려움
- 유지보수 비용 증가
- YAGNI 위반

**Better Approach**:
- 가장 단순한 해결책부터 시작 (KISS)
- 실제 필요가 생길 때 패턴 적용
- "현재 문제"를 해결, "미래 문제"를 대비하지 말 것

**Example**:
```java
// Bad: 단순 계산에 Strategy + Factory + Builder
interface PriceCalculationStrategy { ... }
class PriceCalculatorFactory { ... }
class PriceBuilder { ... }

// Good: 지금 필요한 만큼만
double calculatePrice(int quantity, double unitPrice) {
    return quantity * unitPrice;
}
// 나중에 복잡해지면 그때 리팩토링
```

### 5. Ignoring Code Smells

**Problem**: 리팩토링 기회를 보고도 무시함
**Impact**: 기술 부채 누적, 나중에 리팩토링 비용 증가
**Better Approach**:
- Boy Scout Rule: 발견한 코드를 조금이라도 개선하고 떠남
- 작은 리팩토링은 즉시 수행 (Rename, Extract Method 등)
- 큰 리팩토링은 백로그에 등록하여 계획적 수행

### 6. Refactoring in Red State

**Problem**: 테스트가 실패한 상태에서 리팩토링
**Impact**: 기능 버그와 리팩토링 오류를 구분할 수 없음
**Better Approach**:
- Red → Green → Refactor 순서 엄수
- 테스트가 실패하면 먼저 통과시키고 나서 리팩토링

---

## Code Smell → Refactoring Decision Matrix

각 코드 스멜에 대해 적용할 리팩토링 패턴:

| Code Smell | Primary Refactoring | Alternative | When to Use Alternative |
|-----------|---------------------|-------------|------------------------|
| **Long Method** | Extract Method | Decompose Conditional | 조건문이 복잡한 경우 |
| **Large Class** | Extract Class | Extract Interface | 일부 기능만 사용하는 클라이언트가 있을 때 |
| **God Object** | Extract Class | Replace Inheritance with Composition | 잘못된 상속 구조인 경우 |
| **Feature Envy** | Move Method | Extract Class | 여러 메서드가 같은 클래스를 envy하면 |
| **Primitive Obsession** | Extract Class (Value Object) | Introduce Parameter Object | 파라미터 리스트에 나타나면 |
| **Long Parameter List** | Introduce Parameter Object | Replace Parameter with Query | 파라미터를 계산 가능하면 |
| **Data Clumps** | Extract Class | Introduce Parameter Object | 파라미터로만 나타나면 |
| **Shotgun Surgery** | Move Method/Field | Inline Class | 불필요한 클래스 분리인 경우 |
| **Divergent Change** | Extract Class | Extract Interface | 여러 구현이 필요하면 |
| **Switch Statements** | Replace Conditional with Polymorphism | Replace Parameter with Explicit Methods | 간단한 경우 |
| **Speculative Generality** | Inline Method/Class | Remove Parameter | 사용되지 않는 파라미터는 제거 |
| **Temporary Field** | Extract Class | Replace Method with Method Object | 복잡한 알고리즘인 경우 |
| **Message Chains** | Hide Delegate | Extract Method | 체인이 복잡한 계산이면 |
| **Middle Man** | Remove Middle Man | Inline Method | 단순 위임이면 |
| **Inappropriate Intimacy** | Move Method/Field | Extract Class | 양방향 친밀도면 중재자 추출 |
| **Duplicate Code** | Extract Method | Template Method | 상속 관계에서 중복이면 |
| **Dead Code** | Delete | - | 주저 없이 삭제 (VCS에 있음) |
| **Comments** | Extract Method | Rename Method/Variable | 변수명만으로 명확해지면 |

---

## Refactoring by Code Metrics

코드 메트릭스에 따른 리팩토링 우선순위:

| Metric | Threshold | Risk | Refactoring |
|--------|-----------|------|-------------|
| **Lines of Code (LOC)** | Method > 30 | Medium | Extract Method |
| | Class > 300 | High | Extract Class |
| **Cyclomatic Complexity** | > 10 | High | Decompose Conditional, Extract Method |
| **Number of Parameters** | > 4 | Medium | Introduce Parameter Object |
| **Depth of Inheritance** | > 4 | High | Replace Inheritance with Composition |
| **Coupling (Afferent)** | > 10 | High | Extract Interface, Move Method |
| **Lack of Cohesion (LCOM)** | > 0.5 | High | Extract Class |
| **Test Coverage** | < 80% | Critical | Write Tests First |
| **Duplicate Code** | > 6 lines | High | Extract Method |

---

## Language-Specific Considerations

### JavaScript/TypeScript

- **Async/Await**: Extract Method 시 async 함수 주의
- **Closure**: 변수 스코프 확인 필수
- **this 바인딩**: 메서드 추출 시 this 문제 주의 (arrow function 사용)

### Python

- **Indentation**: Extract Method 시 들여쓰기 정확히
- **Mutable Default Arguments**: 리팩토링 시 `def foo(x=[])` 패턴 주의
- **Duck Typing**: Extract Interface 대신 Protocol (PEP 544) 사용

### Java

- **Checked Exceptions**: 메서드 추출 시 throws 절 관리
- **Access Modifiers**: private → protected → public 순서로 점진적 공개
- **Generics**: 타입 파라미터 유지 확인

---

## Tools and Automation

리팩토링을 안전하게 수행하는 도구들:

### IDE Automated Refactoring

- **IntelliJ IDEA**: Rename, Extract Method/Variable, Move, Inline 등 자동화
- **VS Code**: TypeScript/JavaScript 리팩토리 지원
- **PyCharm**: Python 전용 리팩토링

**Tip**: IDE 자동 리팩토링은 대부분 안전. 수동보다 우선 사용

### Static Analysis

- **SonarQube**: 코드 스멜, 복잡도, 중복 탐지
- **ESLint/TSLint**: JavaScript/TypeScript 코드 품질
- **Pylint/Flake8**: Python 코드 품질
- **RuboCop**: Ruby 코드 스타일

### Test Coverage

- **Jest**: JavaScript 커버리지
- **pytest-cov**: Python 커버리지
- **JaCoCo**: Java 커버리지

**Target**: 리팩토링 대상 코드는 80% 이상 커버리지

---

## Summary

리팩토링 성공을 위한 체크리스트:

- [ ] 리팩토링 전 테스트가 모두 통과하는가?
- [ ] 한 번에 하나의 리팩토링만 수행하는가?
- [ ] 각 변경 후 테스트를 실행하는가?
- [ ] 테스트 통과 후 즉시 커밋하는가?
- [ ] 기능 추가와 리팩토링을 분리하는가?
- [ ] IDE 자동 리팩토링을 우선 사용하는가?
- [ ] Code Smell → Refactoring 매핑을 참고하는가?
- [ ] YAGNI 원칙을 지키는가? (과도한 추상화 회피)
- [ ] Rule of Three를 지키는가? (3번 중복 시 추상화)
- [ ] Boy Scout Rule을 실천하는가? (조금이라도 개선)

**Remember**:
- 완벽한 코드는 없습니다. 점진적 개선이 핵심입니다.
- 리팩토링은 기능을 추가하지 않습니다. 구조만 개선합니다.
- 테스트는 리팩토링의 안전망입니다. 절대 생략하지 마세요.
- 작은 단계로 나누면 항상 안전합니다.
