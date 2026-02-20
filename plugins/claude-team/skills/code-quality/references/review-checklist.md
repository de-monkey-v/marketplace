# Code Review Checklist

체계적이고 포괄적인 코드 리뷰를 위한 7개 카테고리 체크리스트입니다.

## How to Use

1. **순차 검토**: 1번부터 7번까지 카테고리별로 순차 검토
2. **심각도 우선**: Critical → Important → Minor → Suggestion 순으로 우선순위 부여
3. **건설적 피드백**: 문제 지적과 함께 해결책 제안
4. **맥락 고려**: 모든 규칙에는 예외가 있음. 프로젝트 상황 고려

## 1. Correctness (정확성)

코드가 의도한 대로 동작하는지 검증합니다.

### 1.1 Logic Errors

- [ ] **조건문 로직**: if/else 분기가 모든 경우를 올바르게 처리하는가?
- [ ] **Boolean 표현식**: `&&`와 `||`의 우선순위가 올바른가?
- [ ] **부정 조건**: `!` 사용이 의도대로 동작하는가? (Double negative 주의)
- [ ] **Early Return**: 조기 반환 후 도달 불가능한 코드는 없는가?

**탐지 패턴**:
```javascript
// Bad: 조건 순서 오류
if (user.age > 18) {
  return "adult";
} else if (user.age > 65) {  // 절대 도달 불가
  return "senior";
}

// Good
if (user.age > 65) {
  return "senior";
} else if (user.age > 18) {
  return "adult";
}
```

### 1.2 Off-by-One Errors

- [ ] **배열 인덱스**: `array[i]` 접근 시 `0 <= i < array.length` 보장되는가?
- [ ] **루프 범위**: `for (i = 0; i < n; i++)` vs `i <= n` 의도 확인
- [ ] **슬라이싱**: `array.slice(start, end)`에서 end는 exclusive임을 고려했는가?
- [ ] **날짜 범위**: "3일 후"가 `+3`인가 `+2`인가? (오늘 포함 여부)

**탐지 패턴**:
```python
# Bad: 마지막 요소 누락
for i in range(len(items) - 1):  # 마지막 요소 처리 안 됨
    process(items[i])

# Good
for i in range(len(items)):
    process(items[i])
```

### 1.3 Null/Undefined Handling

- [ ] **Null 체크**: 객체 사용 전 null/undefined 체크가 있는가?
- [ ] **Optional Chaining**: `?.` 사용이 적절한가?
- [ ] **기본값**: `||`, `??`, 기본 파라미터 사용이 의도대로인가?
- [ ] **빈 배열/객체**: `array.length > 0` 체크가 필요한가?

**탐지 패턴**:
```typescript
// Bad: null 체크 누락
function getUserName(user: User): string {
  return user.profile.name;  // user 또는 profile이 null이면 크래시
}

// Good
function getUserName(user: User | null): string {
  return user?.profile?.name ?? "Unknown";
}
```

### 1.4 Race Conditions

- [ ] **비동기 순서**: async/await 사용이 올바른가?
- [ ] **상태 업데이트**: 여러 곳에서 동시에 같은 상태를 수정하지 않는가?
- [ ] **Lock/Mutex**: 공유 자원 접근 시 동기화가 필요한가?
- [ ] **이벤트 순서**: 이벤트 핸들러 실행 순서에 의존하지 않는가?

**탐지 패턴**:
```javascript
// Bad: Race condition
async function updateCounter() {
  const current = await getCounter();  // 1
  await setCounter(current + 1);       // 여러 요청이 동시에 1을 읽을 수 있음
}

// Good: Atomic operation
async function updateCounter() {
  await incrementCounter();  // DB 레벨에서 원자적 증가
}
```

### 1.5 Boundary Conditions

- [ ] **최소/최대값**: 0, 1, -1, MAX_INT, 빈 컬렉션에서 동작하는가?
- [ ] **첫 번째/마지막**: 첫 요소, 마지막 요소 처리가 올바른가?
- [ ] **빈 입력**: 빈 문자열, 빈 배열, null에 대한 처리가 있는가?
- [ ] **특수 문자**: 공백, 개행, 유니코드, 이스케이프 문자 처리가 올바른가?

**탐지 패턴**:
```java
// Bad: 빈 배열 미처리
public int findMax(int[] numbers) {
  int max = numbers[0];  // 빈 배열이면 ArrayIndexOutOfBoundsException
  for (int num : numbers) {
    if (num > max) max = num;
  }
  return max;
}

// Good
public Integer findMax(int[] numbers) {
  if (numbers.length == 0) return null;
  int max = numbers[0];
  for (int num : numbers) {
    if (num > max) max = num;
  }
  return max;
}
```

## 2. Security (보안)

보안 취약점을 사전에 차단합니다.

### 2.1 Input Validation at Boundaries

- [ ] **검증 위치**: 입력은 시스템 경계(API endpoint, CLI argument)에서 검증되는가?
- [ ] **화이트리스트**: 허용 목록 방식을 사용하는가? (블랙리스트는 불완전)
- [ ] **타입 검증**: 예상한 타입(문자열, 숫자, 날짜)인가?
- [ ] **길이 제한**: 최대 길이가 강제되는가? (DoS 방지)
- [ ] **형식 검증**: 이메일, URL, 전화번호 등 형식이 올바른가?

**탐지 패턴**:
```python
# Bad: 검증 없음
@app.route('/user/<user_id>')
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection 취약
    return db.execute(query)

# Good: 입력 검증 + Parameterized query
@app.route('/user/<user_id>')
def get_user(user_id):
    if not user_id.isdigit() or int(user_id) <= 0:
        return "Invalid user ID", 400
    query = "SELECT * FROM users WHERE id = ?"
    return db.execute(query, (user_id,))
```

### 2.2 SQL Injection Prevention

- [ ] **Parameterized Queries**: Prepared statement 또는 ORM을 사용하는가?
- [ ] **문자열 연결 금지**: SQL 쿼리를 문자열 결합으로 만들지 않는가?
- [ ] **동적 쿼리**: 불가피한 경우 화이트리스트 기반 검증을 하는가?

**탐지 패턴**:
```java
// Bad: String concatenation
String query = "SELECT * FROM users WHERE name = '" + userName + "'";
statement.execute(query);

// Good: Prepared statement
String query = "SELECT * FROM users WHERE name = ?";
PreparedStatement stmt = connection.prepareStatement(query);
stmt.setString(1, userName);
stmt.execute();
```

### 2.3 XSS (Cross-Site Scripting) Prevention

- [ ] **Output Encoding**: 사용자 입력을 HTML에 출력 시 이스케이프하는가?
- [ ] **Context-aware Encoding**: HTML, JS, CSS, URL 컨텍스트별 인코딩이 다름을 고려했는가?
- [ ] **innerHTML 주의**: `innerHTML` 대신 `textContent` 사용을 고려했는가?
- [ ] **CSP 헤더**: Content-Security-Policy 헤더를 설정했는가?

**탐지 패턴**:
```javascript
// Bad: XSS 취약
const userName = getUserInput();
document.getElementById('greeting').innerHTML = `Hello, ${userName}`;
// userName이 "<script>alert('XSS')</script>"이면 실행됨

// Good: 안전한 텍스트 삽입
document.getElementById('greeting').textContent = `Hello, ${userName}`;
// 또는 템플릿 엔진의 자동 이스케이프 사용
```

### 2.4 CSRF (Cross-Site Request Forgery) Protection

- [ ] **CSRF 토큰**: 상태 변경 요청(POST/PUT/DELETE)에 CSRF 토큰이 있는가?
- [ ] **SameSite 쿠키**: 쿠키에 `SameSite=Strict` 또는 `Lax` 속성이 있는가?
- [ ] **Origin 검증**: `Referer` 또는 `Origin` 헤더를 검증하는가?

### 2.5 Authentication & Authorization

- [ ] **인증 확인**: 보호된 엔드포인트에 인증 체크가 있는가?
- [ ] **권한 확인**: 인증된 사용자가 해당 리소스에 접근 권한이 있는가?
- [ ] **수평적 권한 상승**: 사용자 A가 사용자 B의 데이터에 접근할 수 없는가?
- [ ] **수직적 권한 상승**: 일반 사용자가 관리자 기능에 접근할 수 없는가?

**탐지 패턴**:
```typescript
// Bad: 인증만 확인, 권한 미확인
@Get('/posts/:id')
@UseGuards(AuthGuard)  // 로그인만 확인
async getPost(@Param('id') id: string) {
  return this.postService.findOne(id);  // 다른 사용자의 비공개 글도 조회 가능
}

// Good: 소유권 확인
@Get('/posts/:id')
@UseGuards(AuthGuard)
async getPost(@Param('id') id: string, @User() user: User) {
  const post = await this.postService.findOne(id);
  if (post.authorId !== user.id && !post.isPublic) {
    throw new ForbiddenException();
  }
  return post;
}
```

### 2.6 Sensitive Data Exposure

- [ ] **하드코딩 금지**: API 키, 비밀번호, 토큰이 코드에 하드코딩되지 않았는가?
- [ ] **환경 변수**: 민감 정보는 환경 변수 또는 시크릿 관리 도구를 사용하는가?
- [ ] **로그 노출**: 비밀번호, 토큰, 개인정보가 로그에 기록되지 않는가?
- [ ] **에러 메시지**: 스택 트레이스, 내부 경로가 사용자에게 노출되지 않는가?
- [ ] **암호화**: 민감 데이터(비밀번호, 카드 번호)가 암호화되어 저장되는가?

**탐지 패턴**:
```python
# Bad: 하드코딩, 로그 노출
API_KEY = "sk_live_abc123def456"  # 하드코딩
logger.info(f"User login: {username} / {password}")  # 비밀번호 로그

# Good
API_KEY = os.getenv("STRIPE_API_KEY")
logger.info(f"User login: {username}")  # 비밀번호 제외
```

### 2.7 OWASP Top 10 Quick Reference

| Rank | Vulnerability | 탐지 패턴 | 방어 방법 |
|------|---------------|-----------|-----------|
| A01 | Broken Access Control | 권한 체크 누락 | 모든 요청에 인가 확인 |
| A02 | Cryptographic Failures | 평문 저장, 약한 알고리즘 | bcrypt/Argon2, TLS 1.3 |
| A03 | Injection | 문자열 연결 쿼리 | Parameterized query, ORM |
| A04 | Insecure Design | 설계 단계 결함 | Threat modeling, 보안 리뷰 |
| A05 | Security Misconfiguration | 기본 설정, 불필요한 기능 | 최소 권한, 하드닝 |
| A06 | Vulnerable Components | 오래된 라이브러리 | 의존성 스캔, 정기 업데이트 |
| A07 | Identification Failures | 약한 인증 | MFA, 강력한 세션 관리 |
| A08 | Software & Data Integrity | 무결성 미검증 | 서명 검증, CI/CD 보안 |
| A09 | Security Logging Failures | 로그 부재/불충분 | 중요 이벤트 로깅, 모니터링 |
| A10 | Server-Side Request Forgery | URL 검증 누락 | URL 화이트리스트, 네트워크 격리 |

## 3. Performance (성능)

성능 병목과 자원 낭비를 식별합니다.

### 3.1 Algorithm Complexity

- [ ] **시간 복잡도**: O(n²) 이상의 중첩 루프가 있는가? 더 효율적인 알고리즘이 있는가?
- [ ] **불필요한 순회**: 같은 배열을 여러 번 순회하지 않는가?
- [ ] **조기 종료**: 찾으면 즉시 반환하는가? (모든 요소를 순회하지 않음)
- [ ] **적절한 자료구조**: 검색이 빈번하면 배열보다 Set/Map을 사용하는가?

**탐지 패턴**:
```javascript
// Bad: O(n²) - 중첩 루프
function findDuplicates(arr) {
  const duplicates = [];
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (arr[i] === arr[j]) duplicates.push(arr[i]);
    }
  }
  return duplicates;
}

// Good: O(n) - Set 사용
function findDuplicates(arr) {
  const seen = new Set();
  const duplicates = new Set();
  for (const item of arr) {
    if (seen.has(item)) duplicates.add(item);
    seen.add(item);
  }
  return Array.from(duplicates);
}
```

### 3.2 N+1 Query Problem

- [ ] **Eager Loading**: 관련 데이터를 한 번에 로드하는가?
- [ ] **Batch Loading**: 루프 안에서 개별 쿼리를 실행하지 않는가?
- [ ] **DataLoader**: GraphQL 사용 시 DataLoader 패턴을 적용했는가?

**탐지 패턴**:
```python
# Bad: N+1 쿼리
posts = Post.query.all()  # 1개 쿼리
for post in posts:
    author = post.author  # N개 쿼리 (lazy loading)
    print(f"{post.title} by {author.name}")

# Good: Eager loading
posts = Post.query.options(joinedload(Post.author)).all()  # 1개 쿼리 (JOIN)
for post in posts:
    print(f"{post.title} by {post.author.name}")
```

### 3.3 Memory Leaks

- [ ] **이벤트 리스너**: 컴포넌트 제거 시 리스너를 해제하는가?
- [ ] **타이머**: setInterval/setTimeout을 clear하는가?
- [ ] **클로저**: 불필요한 변수를 클로저가 참조하지 않는가?
- [ ] **캐시**: 무한정 커지는 캐시에 크기 제한이 있는가?

**탐지 패턴**:
```javascript
// Bad: 메모리 누수
class Component {
  constructor() {
    window.addEventListener('resize', this.handleResize);
  }
  // removeEventListener가 없음 - 컴포넌트 제거 후에도 핸들러 남음
}

// Good: 정리 코드
class Component {
  constructor() {
    this.handleResize = this.handleResize.bind(this);
    window.addEventListener('resize', this.handleResize);
  }
  destroy() {
    window.removeEventListener('resize', this.handleResize);
  }
}
```

### 3.4 Unnecessary Re-renders (React Specific)

- [ ] **memo/useMemo**: 비싼 계산을 메모이제이션하는가?
- [ ] **useCallback**: 함수를 props로 전달 시 useCallback을 사용하는가?
- [ ] **key prop**: 리스트 렌더링 시 안정적인 key를 사용하는가? (인덱스 금지)
- [ ] **객체/배열 생성**: 렌더링마다 새 객체/배열을 생성하지 않는가?

**탐지 패턴**:
```jsx
// Bad: 매 렌더링마다 새 함수 생성
function Parent() {
  const [count, setCount] = useState(0);
  return <Child onClick={() => console.log(count)} />;  // 매번 새 함수
}

// Good: useCallback
function Parent() {
  const [count, setCount] = useState(0);
  const handleClick = useCallback(() => console.log(count), [count]);
  return <Child onClick={handleClick} />;
}
```

### 3.5 Bundle Size Impact

- [ ] **Tree Shaking**: 사용하지 않는 코드가 번들에 포함되지 않는가?
- [ ] **Code Splitting**: 라우트별/기능별로 코드를 분할하는가?
- [ ] **Dynamic Import**: 조건부로 필요한 모듈을 동적 import하는가?
- [ ] **라이브러리 선택**: 큰 라이브러리 대신 작은 대안이 있는가? (moment → date-fns)

### 3.6 Caching Opportunities

- [ ] **API 응답**: 변하지 않는 데이터는 캐싱하는가?
- [ ] **계산 결과**: 비싼 계산은 메모이제이션하는가?
- [ ] **정적 자산**: 이미지, CSS, JS에 캐시 헤더가 있는가?
- [ ] **CDN**: 정적 파일을 CDN에서 제공하는가?

## 4. Maintainability (유지보수성)

코드를 이해하고 수정하기 쉬운지 평가합니다.

### 4.1 SOLID Principles Checklist

**Single Responsibility Principle**
- [ ] 클래스/모듈이 하나의 변경 이유만 가지는가?
- [ ] "이 클래스는 무엇을 하는가?"라는 질문에 "그리고"를 사용하지 않고 답할 수 있는가?
- [ ] 다른 팀원이 수정할 이유가 겹치지 않는가?

**Open/Closed Principle**
- [ ] 새 기능 추가 시 기존 코드를 수정하지 않고 확장 가능한가?
- [ ] 전략 패턴, 플러그인 구조 등 확장 메커니즘이 있는가?
- [ ] if/switch 문으로 타입을 분기하지 않는가?

**Liskov Substitution Principle**
- [ ] 하위 타입이 상위 타입의 계약을 위반하지 않는가?
- [ ] 하위 클래스가 상위 클래스보다 강한 사전 조건을 요구하지 않는가?
- [ ] 하위 클래스가 상위 클래스보다 약한 사후 조건을 제공하지 않는가?

**Interface Segregation Principle**
- [ ] 인터페이스가 클라이언트별로 세분화되어 있는가?
- [ ] 구현 클래스가 사용하지 않는 메서드를 강제로 구현하지 않는가?
- [ ] 인터페이스가 너무 비대하지 않은가? (5개 이상 메서드는 의심)

**Dependency Inversion Principle**
- [ ] 고수준 모듈이 저수준 모듈에 직접 의존하지 않는가?
- [ ] 구체 클래스 대신 인터페이스/추상 클래스에 의존하는가?
- [ ] DI (Dependency Injection) 패턴을 사용하는가?

### 4.2 Code Smells Detection

아래 테이블을 참고하여 코드 스멜을 탐지합니다:

| Code Smell | 탐지 패턴 | 심각도 | 리팩토링 |
|-----------|-----------|--------|----------|
| **Long Method** | 메서드 30줄 이상 | Medium | Extract Method |
| **Large Class** | 클래스 300줄 이상, 10+ 메서드 | High | Extract Class, Extract Interface |
| **God Object** | 한 클래스가 시스템의 대부분 담당 | Critical | Decompose, Extract Class |
| **Feature Envy** | 다른 클래스의 getter를 과도하게 호출 | Medium | Move Method |
| **Primitive Obsession** | 도메인 개념을 int, String으로 표현 | Low | Value Object, Extract Class |
| **Long Parameter List** | 파라미터 4개 이상 | Medium | Parameter Object, Builder |
| **Data Clumps** | 같은 파라미터 그룹 반복 | Low | Extract Class |
| **Shotgun Surgery** | 한 변경이 여러 클래스 수정 요구 | High | Move Method/Field, Inline Class |
| **Divergent Change** | 한 클래스가 여러 이유로 변경 | High | Extract Class (SRP 위반) |
| **Switch Statements** | 타입 기반 switch/if 체인 | Medium | Polymorphism, Strategy Pattern |
| **Speculative Generality** | 사용되지 않는 추상화 | Low | Inline Class, Remove Parameter |
| **Temporary Field** | 특정 상황에만 사용되는 필드 | Medium | Extract Class, Replace Temp |
| **Message Chains** | a.b().c().d() 형태 | Medium | Hide Delegate |
| **Middle Man** | 위임만 하는 클래스 | Low | Remove Middle Man, Inline Method |
| **Inappropriate Intimacy** | 클래스 간 과도한 private 접근 | High | Move Method, Extract Class |
| **Duplicate Code** | 중복된 로직 | High | Extract Method/Class, Template Method |
| **Dead Code** | 사용되지 않는 코드 | Low | Delete |
| **Comments** | 코드를 설명하는 주석 | Low | Rename, Extract Method |

### 4.3 Naming Conventions

- [ ] **의도 드러내기**: 이름만 보고 무엇을 하는지 알 수 있는가?
- [ ] **일관성**: 프로젝트 전체에서 동일한 개념에 동일한 용어를 사용하는가?
- [ ] **발음 가능**: 팀원과 대화할 때 자연스럽게 말할 수 있는가?
- [ ] **검색 가능**: 단일 문자 변수(e, i, j 제외)를 피했는가?
- [ ] **인코딩 회피**: 헝가리안 표기법, 타입 접두사를 피했는가?

**Good vs Bad Examples**:
```typescript
// Bad
const d: number;  // elapsed time in days
const yyyymmdd: string;
const theList: any[];

// Good
const elapsedTimeInDays: number;
const timestamp: string;
const activeUsers: User[];
```

### 4.4 Documentation

- [ ] **Public API**: 모든 공개 함수/클래스에 JSDoc/Docstring이 있는가?
- [ ] **Why, Not What**: 주석은 "무엇"보다 "왜"를 설명하는가?
- [ ] **최신성**: 주석이 코드와 동기화되어 있는가? (틀린 주석은 없는 것보다 나쁨)
- [ ] **README**: 프로젝트 설정, 실행 방법이 문서화되어 있는가?
- [ ] **Architecture Decision Records**: 중요한 설계 결정이 기록되어 있는가?

## 5. Architecture Alignment (아키텍처 정렬)

설계 원칙과 아키텍처 패턴을 준수하는지 확인합니다.

### 5.1 Module Boundary Respect

- [ ] **경계 위반**: 모듈이 다른 모듈의 내부 구현을 직접 참조하지 않는가?
- [ ] **Public API**: 모듈 간 통신은 명시된 공개 인터페이스를 통하는가?
- [ ] **캡슐화**: 모듈의 내부 상태가 외부에 노출되지 않는가?

### 5.2 Dependency Direction (Inward)

- [ ] **의존성 방향**: 의존성이 안쪽(핵심 비즈니스 로직)으로 향하는가?
- [ ] **Dependency Inversion**: 인프라(DB, API)가 비즈니스 로직에 의존하는가?
- [ ] **Ports and Adapters**: 외부 시스템과의 통합이 인터페이스를 통하는가?

**Clean Architecture 의존성 방향**:
```
UI → Application → Domain ← Infrastructure
     (컨트롤러)   (유스케이스)   (엔티티)  (리포지토리 구현)
```

### 5.3 Layer Separation

- [ ] **계층 건너뛰기 금지**: UI가 DB를 직접 호출하지 않는가?
- [ ] **단방향 의존성**: 하위 계층이 상위 계층을 모르는가?
- [ ] **계층별 책임**: Presentation / Business / Data Access 책임이 분리되어 있는가?

### 5.4 Circular Dependencies

- [ ] **순환 의존성**: A → B → A 형태의 순환이 없는가?
- [ ] **탐지**: 빌드 도구 또는 분석 도구로 순환 의존성을 검사했는가?
- [ ] **해결**: Interface 추출, 중재자 패턴 등으로 순환을 끊었는가?

### 5.5 Consistent Error Handling

- [ ] **일관된 전략**: 프로젝트 전체에서 동일한 에러 처리 방식을 사용하는가?
- [ ] **예외 vs 결과 타입**: 언제 예외를 던지고 언제 Result<T, E>를 반환하는가?
- [ ] **에러 전파**: 하위 계층의 에러가 적절히 변환되어 상위로 전파되는가?
- [ ] **복구 가능성**: 복구 가능한 에러와 불가능한 에러가 구분되는가?

## 6. Testing (테스트)

테스트 코드의 존재와 품질을 검증합니다.

### 6.1 Test Exists

- [ ] **새 코드**: 변경된 코드에 대한 테스트가 추가되었는가?
- [ ] **커버리지**: 핵심 비즈니스 로직의 테스트 커버리지가 80% 이상인가?
- [ ] **테스트 타입**: Unit / Integration / E2E 중 적절한 레벨의 테스트인가?

### 6.2 Test Coverage

- [ ] **Happy Path**: 정상 시나리오를 테스트하는가?
- [ ] **Error Path**: 예외/에러 상황을 테스트하는가?
- [ ] **Edge Cases**: 경계 조건(빈 배열, null, 0, 최대값)을 테스트하는가?
- [ ] **Branch Coverage**: 모든 if/switch 분기를 테스트하는가?

### 6.3 Test is Deterministic

- [ ] **일관성**: 동일한 입력에 대해 항상 동일한 결과를 반환하는가?
- [ ] **순서 독립성**: 테스트 실행 순서가 결과에 영향을 주지 않는가?
- [ ] **시간 의존성**: 현재 시간에 의존하지 않는가? (Mock 사용)
- [ ] **랜덤 값**: 랜덤 값을 사용하지 않거나 seed를 고정했는가?

### 6.4 Proper Assertions

- [ ] **명확한 검증**: `expect(result).toBe(true)` 대신 구체적 값을 검증하는가?
- [ ] **의미 있는 메시지**: 실패 시 무엇이 잘못되었는지 알 수 있는가?
- [ ] **Smoke Test 지양**: 단순히 "에러가 안 나면 OK"가 아닌가?
- [ ] **One Assertion Per Test**: 하나의 테스트는 하나만 검증하는가?

**Good vs Bad**:
```javascript
// Bad: Smoke test
test('user creation works', () => {
  createUser('John');  // 에러만 안 나면 통과
});

// Good: Proper assertion
test('createUser returns user with correct name', () => {
  const user = createUser('John');
  expect(user.name).toBe('John');
  expect(user.id).toBeDefined();
});
```

### 6.5 Mock Boundaries

- [ ] **경계에서 Mock**: 외부 시스템(DB, API)과의 경계에서 Mock하는가?
- [ ] **과도한 Mock 회피**: 내부 로직까지 Mock하지 않는가?
- [ ] **Mock 검증**: Mock 호출 횟수, 인자를 검증하는가?

## 7. Code Style (코드 스타일)

일관성 있고 읽기 쉬운 코드를 작성합니다.

### 7.1 Consistency

- [ ] **포맷팅**: Prettier/Black 등 자동 포맷터를 사용하는가?
- [ ] **Lint**: ESLint/Pylint 경고가 없는가?
- [ ] **네이밍**: 프로젝트의 네이밍 규칙을 따르는가?
- [ ] **파일 구조**: 프로젝트의 디렉토리 구조를 따르는가?

### 7.2 No Dead Code

- [ ] **사용되지 않는 함수**: IDE나 도구로 unreachable code를 검사했는가?
- [ ] **사용되지 않는 import**: 불필요한 import가 없는가?
- [ ] **주석 처리된 코드**: 버전 관리에 있으므로 주석 코드를 삭제했는가?
- [ ] **Feature Flag**: 오래된 feature flag를 정리했는가?

### 7.3 Error Messages

- [ ] **실행 가능**: 사용자가 무엇을 해야 하는지 알 수 있는가?
- [ ] **맥락 포함**: 어떤 상황에서 발생했는지 알 수 있는가?
- [ ] **기술 용어 회피**: 사용자 대상 메시지는 쉬운 언어를 사용하는가?

**Good vs Bad**:
```python
# Bad
raise ValueError("Invalid input")

# Good
raise ValueError(
    f"Email '{email}' is invalid. "
    "Expected format: user@example.com"
)
```

### 7.4 Magic Numbers

- [ ] **Named Constants**: 숫자 리터럴 대신 의미 있는 상수를 사용하는가?
- [ ] **설명**: 상수의 의미가 명확한가?
- [ ] **중앙화**: 관련 상수를 한 곳에 모았는가?

**Good vs Bad**:
```java
// Bad
if (user.age >= 18) { ... }
sleep(86400000);

// Good
private static final int LEGAL_AGE = 18;
private static final int MILLISECONDS_PER_DAY = 24 * 60 * 60 * 1000;

if (user.age >= LEGAL_AGE) { ... }
sleep(MILLISECONDS_PER_DAY);
```

---

## Finding Severity Classification

리뷰 코멘트의 심각도를 분류하여 우선순위를 정합니다:

| Severity | Definition | Action | Examples |
|----------|------------|--------|----------|
| **Critical** | 반드시 수정해야 함.<br>배포 시 심각한 문제 발생 | 머지 블록 | - SQL injection 취약점<br>- 데이터 손실 가능성<br>- 크래시 유발 버그<br>- 보안 취약점 |
| **Important** | 수정을 강력히 권장.<br>비즈니스 로직 문제 | 수정 요청 | - 로직 오류 (잘못된 계산)<br>- 입력 검증 누락<br>- Race condition<br>- 심각한 성능 문제 (O(n³)) |
| **Minor** | 수정하면 좋음.<br>품질 향상 | 코멘트 | - 스타일 불일치<br>- 네이밍 개선 여지<br>- 경미한 중복 코드<br>- 테스트 부족 |
| **Suggestion** | 선택 사항.<br>더 나은 방법 제안 | 참고용 노트 | - 대안 패턴 소개<br>- 리팩토링 기회<br>- 문서화 개선<br>- 최적화 아이디어 |

### Severity 판단 기준

1. **Critical 판단**:
   - 사용자 데이터에 영향을 주는가?
   - 보안 취약점인가?
   - 시스템 크래시를 유발하는가?
   - 법적/규제 문제를 일으키는가?

2. **Important 판단**:
   - 비즈니스 로직이 틀렸는가?
   - 특정 조건에서 실패하는가?
   - 성능이 심각하게 저하되는가?

3. **Minor 판단**:
   - 동작은 올바르나 품질이 낮은가?
   - 유지보수성이 떨어지는가?
   - 팀 규칙을 위반하는가?

4. **Suggestion 판단**:
   - 현재도 괜찮지만 더 나은 방법이 있는가?
   - 배울 만한 패턴이 있는가?

---

## Review Process

효과적인 리뷰를 위한 권장 프로세스:

1. **첫 번째 패스**: Critical/Important 이슈에 집중 (10분)
   - Correctness, Security 섹션 집중 검토
   - 명백한 버그, 보안 취약점 찾기

2. **두 번째 패스**: Maintainability, Architecture (15분)
   - SOLID 원칙, 코드 스멜 확인
   - 아키텍처 패턴 준수 여부

3. **세 번째 패스**: Testing, Style (5분)
   - 테스트 존재 및 품질 확인
   - 스타일 일관성 검토

4. **종합 의견**: (5분)
   - 발견한 이슈를 심각도별로 정리
   - 전체적인 코드 품질 평가
   - 개선 방향 제안

**Total Time**: 약 35분 (복잡도에 따라 조정)
