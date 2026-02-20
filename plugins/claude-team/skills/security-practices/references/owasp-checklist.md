# OWASP Top 10 (2021) Comprehensive Checklist

이 문서는 OWASP Top 10 2021 기반의 종합 보안 체크리스트입니다. 각 취약점에 대한 설명, 체크리스트, 탐지 방법, 방지 코드 예제를 제공합니다.

## A01:2021 — Broken Access Control

### Description

인증된 사용자에 대한 접근 제한이 제대로 적용되지 않아 권한 없는 정보 공개, 수정, 삭제가 가능한 취약점입니다.

### Common Vulnerabilities

- URL 변경을 통한 다른 사용자 데이터 접근
- API 엔드포인트에 대한 권한 검증 누락
- CORS 설정 오류로 인한 비인가 접근
- JWT 토큰 검증 부재
- Insecure Direct Object Reference (IDOR)

### Checklist

- [ ] **Deny by default**: 공개 리소스를 제외한 모든 접근 기본 거부
- [ ] **Server-side enforcement**: 클라이언트가 아닌 서버에서 접근 제어 강제
- [ ] **Record ownership validation**: 사용자가 자신의 데이터만 접근 가능하도록 검증
- [ ] **Rate limiting**: API 접근에 대한 속도 제한 적용
- [ ] **Disable directory listing**: 웹 서버의 디렉토리 목록 표시 비활성화
- [ ] **JWT invalidation**: 로그아웃 시 토큰 무효화 메커니즘 구현
- [ ] **CORS policy**: CORS 정책 올바르게 설정 (불필요한 origin 허용 금지)
- [ ] **Path traversal prevention**: 파일 경로 접근 시 `../` 패턴 검증
- [ ] **Function level access control**: 각 기능/API에 대한 권한 검증
- [ ] **Log access failures**: 접근 제어 실패 로깅 및 모니터링

### Detection Patterns

코드에서 다음 패턴을 검색하여 취약점을 찾을 수 있습니다:

```bash
# 권한 검증 없는 직접 객체 참조
grep -r "findById.*req.params" --include="*.ts" --include="*.js"

# 인증 미들웨어 누락 가능성
grep -r "router.get\|router.post" --include="*.ts" | grep -v "authenticate"

# CORS 전체 허용
grep -r "Access-Control-Allow-Origin.*\*" --include="*.ts"
```

### Prevention Code Examples

#### TypeScript/NestJS - IDOR Prevention

```typescript
// ❌ 취약한 코드
@Get(':id')
async getDocument(@Param('id') id: string) {
  return this.documentService.findById(id);
}

// ✅ 안전한 코드
@Get(':id')
@UseGuards(AuthGuard)
async getDocument(@Param('id') id: string, @CurrentUser() user: User) {
  const document = await this.documentService.findById(id);

  if (document.ownerId !== user.id && !user.roles.includes('admin')) {
    throw new ForbiddenException('You do not have access to this document');
  }

  return document;
}
```

#### Python/FastAPI - Role-Based Access Control

```python
# ✅ 안전한 코드
from fastapi import Depends, HTTPException, status

def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if required_role not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_role("admin"))
):
    return await user_service.delete(user_id)
```

#### Java/Spring - Method-Level Security

```java
// ✅ 안전한 코드
@PreAuthorize("hasRole('ADMIN') or @documentSecurity.isOwner(authentication, #id)")
@GetMapping("/documents/{id}")
public Document getDocument(@PathVariable Long id) {
    return documentService.findById(id);
}

@Component("documentSecurity")
public class DocumentSecurityService {
    public boolean isOwner(Authentication auth, Long documentId) {
        User user = (User) auth.getPrincipal();
        Document doc = documentService.findById(documentId);
        return doc.getOwnerId().equals(user.getId());
    }
}
```

---

## A02:2021 — Cryptographic Failures

### Description

민감한 데이터를 보호하지 못하거나 약한 암호화 알고리즘을 사용하여 데이터가 노출되는 취약점입니다.

### Common Vulnerabilities

- 평문으로 저장된 패스워드, 신용카드 정보
- HTTP를 통한 민감 데이터 전송
- 약한 암호화 알고리즘 사용 (MD5, SHA1, DES)
- 하드코딩된 암호화 키
- 적절하지 않은 키 관리

### Checklist

- [ ] **No plaintext sensitive data**: 민감 데이터는 암호화하여 저장
- [ ] **TLS 1.2+ enforced**: 전송 중 데이터는 TLS 1.2 이상 사용
- [ ] **Strong algorithms**: AES-256, SHA-256 이상의 강력한 알고리즘 사용
- [ ] **No deprecated algorithms**: MD5, SHA-1, DES, 3DES 사용 금지
- [ ] **Proper key management**: 키는 환경변수 또는 Key Vault에 저장
- [ ] **No secrets in source code**: 소스 코드에 API 키, 패스워드 등 하드코딩 금지
- [ ] **Password hashing**: bcrypt, scrypt, argon2를 사용한 패스워드 해싱
- [ ] **Encryption at rest**: 데이터베이스 레벨 암호화 (TDE) 적용
- [ ] **Perfect Forward Secrecy**: TLS 설정에서 PFS 활성화
- [ ] **Certificate validation**: SSL/TLS 인증서 유효성 검증

### Detection Patterns

```bash
# 하드코딩된 시크릿
grep -rE "(password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]" --include="*.ts" --include="*.py"

# 약한 해싱 알고리즘
grep -rE "md5|sha1|des" --include="*.ts" --include="*.py" --include="*.java"

# HTTP URL (HTTPS 아님)
grep -r "http://" --include="*.ts" --include="*.py"
```

### Prevention Code Examples

#### TypeScript - Secure Password Hashing

```typescript
import * as bcrypt from 'bcrypt';

// ✅ 안전한 코드
const SALT_ROUNDS = 12;

async function hashPassword(plainPassword: string): Promise<string> {
  return bcrypt.hash(plainPassword, SALT_ROUNDS);
}

async function verifyPassword(plainPassword: string, hashedPassword: string): Promise<boolean> {
  return bcrypt.compare(plainPassword, hashedPassword);
}
```

#### Python - AES Encryption

```python
from cryptography.fernet import Fernet
import os

# ✅ 안전한 코드
class EncryptionService:
    def __init__(self):
        # Key should be stored in environment variable or key vault
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY not found")
        self.cipher = Fernet(key.encode())

    def encrypt(self, plaintext: str) -> bytes:
        return self.cipher.encrypt(plaintext.encode())

    def decrypt(self, ciphertext: bytes) -> str:
        return self.cipher.decrypt(ciphertext).decode()
```

#### Java/Spring - Configuration Encryption

```java
// ✅ 안전한 코드 - application.yml
// jasypt를 사용한 설정 암호화
spring:
  datasource:
    password: ENC(encrypted_password_here)

// Configuration
@Configuration
@EnableEncryptableProperties
public class SecurityConfig {

    @Bean
    public StringEncryptor stringEncryptor() {
        PooledPBEStringEncryptor encryptor = new PooledPBEStringEncryptor();
        SimpleStringPBEConfig config = new SimpleStringPBEConfig();
        config.setPassword(System.getenv("JASYPT_PASSWORD"));
        config.setAlgorithm("PBEWithHMACSHA512AndAES_256");
        config.setPoolSize("1");
        encryptor.setConfig(config);
        return encryptor;
    }
}
```

---

## A03:2021 — Injection

### Description

신뢰할 수 없는 데이터가 명령어나 쿼리의 일부로 전송되어 의도하지 않은 명령이 실행되는 취약점입니다.

### Types of Injection

- SQL Injection
- NoSQL Injection
- OS Command Injection
- LDAP Injection
- XPath Injection
- XML Injection

### Checklist

- [ ] **Parameterized queries**: SQL은 항상 파라미터화된 쿼리 사용
- [ ] **ORM usage**: ORM을 사용하여 안전한 데이터베이스 접근
- [ ] **Input validation**: 허용 목록 기반 입력 검증
- [ ] **Escape special characters**: 출력 컨텍스트에 맞는 이스케이프 처리
- [ ] **No dynamic query construction**: 사용자 입력으로 동적 쿼리 생성 금지
- [ ] **Stored procedures**: 가능한 경우 저장 프로시저 사용
- [ ] **Least privilege DB user**: 데이터베이스 사용자에게 최소 권한만 부여
- [ ] **NoSQL query validation**: NoSQL 쿼리도 파라미터화 및 검증
- [ ] **Command injection prevention**: 외부 명령 실행 시 입력 검증 및 제한
- [ ] **Error handling**: 상세한 오류 메시지 노출 방지

### Detection Patterns

```bash
# SQL Injection 위험 패턴
grep -rE "execute.*\+.*req\.|query.*\+.*params" --include="*.ts" --include="*.js"

# Command Injection 위험
grep -rE "exec\(|spawn\(|system\(" --include="*.ts" --include="*.py"

# String concatenation in queries
grep -rE "SELECT.*\+|INSERT.*\+|UPDATE.*\+" --include="*.ts"
```

### Prevention Code Examples

#### TypeScript - SQL Injection Prevention

```typescript
import { Pool } from 'pg';

// ❌ 취약한 코드
async function getUserByName(username: string) {
  const query = `SELECT * FROM users WHERE username = '${username}'`;
  return pool.query(query);
}

// ✅ 안전한 코드 - Parameterized Query
async function getUserByName(username: string) {
  const query = 'SELECT * FROM users WHERE username = $1';
  return pool.query(query, [username]);
}

// ✅ 안전한 코드 - ORM (TypeORM)
async function getUserByName(username: string) {
  return userRepository.findOne({ where: { username } });
}
```

#### Python - SQL Injection Prevention

```python
import psycopg2

# ❌ 취약한 코드
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)

# ✅ 안전한 코드 - Parameterized Query
def get_user(username):
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))

# ✅ 안전한 코드 - ORM (SQLAlchemy)
def get_user(username):
    return session.query(User).filter(User.username == username).first()
```

#### Python - NoSQL Injection Prevention

```python
from pymongo import MongoClient

# ❌ 취약한 코드
def find_user(username):
    return collection.find_one({"username": username})
    # username이 {"$ne": null}이면 모든 사용자 반환

# ✅ 안전한 코드
def find_user(username):
    if not isinstance(username, str):
        raise ValueError("Username must be a string")
    return collection.find_one({"username": username})
```

#### Java - Command Injection Prevention

```java
// ❌ 취약한 코드
public void processFile(String filename) {
    Runtime.getRuntime().exec("convert " + filename + " output.pdf");
}

// ✅ 안전한 코드
public void processFile(String filename) {
    // Input validation
    if (!filename.matches("^[a-zA-Z0-9_-]+\\.(jpg|png)$")) {
        throw new IllegalArgumentException("Invalid filename");
    }

    // Use ProcessBuilder with separate arguments
    ProcessBuilder pb = new ProcessBuilder("convert", filename, "output.pdf");
    pb.start();
}
```

---

## A04:2021 — Insecure Design

### Description

설계 단계에서 보안이 고려되지 않아 발생하는 근본적인 취약점입니다.

### Key Concepts

- **위협 모델링**: 잠재적 위협을 식별하고 완화 방안 수립
- **보안 설계 패턴**: 검증된 보안 패턴 적용
- **Abuse Case**: 시스템을 악용하는 시나리오 고려

### Checklist

- [ ] **Threat modeling**: 설계 단계에서 위협 모델링 수행
- [ ] **Security requirements**: 기능 요구사항과 함께 보안 요구사항 정의
- [ ] **Abuse cases**: 오남용 시나리오 문서화 및 테스트
- [ ] **Secure design patterns**: Circuit Breaker, Rate Limiting 등 패턴 적용
- [ ] **Defense in depth**: 여러 계층의 보안 통제
- [ ] **Principle of least privilege**: 최소 권한 원칙 적용
- [ ] **Separation of duties**: 중요 작업에 대한 권한 분리
- [ ] **Security review**: 설계 검토 시 보안 전문가 참여
- [ ] **Resource limits**: 리소스 사용 제한 (메모리, CPU, 연결 수)
- [ ] **Business logic security**: 비즈니스 로직 악용 방지

### Secure Design Patterns

#### Rate Limiting Pattern

```typescript
// ✅ Token Bucket Algorithm
class RateLimiter {
  private tokens: Map<string, { count: number; resetTime: number }> = new Map();

  constructor(
    private maxRequests: number,
    private windowMs: number
  ) {}

  async checkLimit(key: string): Promise<boolean> {
    const now = Date.now();
    const userLimit = this.tokens.get(key);

    if (!userLimit || now > userLimit.resetTime) {
      this.tokens.set(key, {
        count: 1,
        resetTime: now + this.windowMs
      });
      return true;
    }

    if (userLimit.count >= this.maxRequests) {
      return false;
    }

    userLimit.count++;
    return true;
  }
}

// Usage
const limiter = new RateLimiter(100, 60000); // 100 requests per minute

app.use(async (req, res, next) => {
  const key = req.ip;
  if (await limiter.checkLimit(key)) {
    next();
  } else {
    res.status(429).json({ error: 'Too many requests' });
  }
});
```

#### Circuit Breaker Pattern

```typescript
// ✅ Circuit Breaker for External Services
class CircuitBreaker {
  private failures = 0;
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';
  private nextAttempt = Date.now();

  constructor(
    private threshold: number,
    private timeout: number
  ) {}

  async call<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() < this.nextAttempt) {
        throw new Error('Circuit breaker is OPEN');
      }
      this.state = 'HALF_OPEN';
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess() {
    this.failures = 0;
    this.state = 'CLOSED';
  }

  private onFailure() {
    this.failures++;
    if (this.failures >= this.threshold) {
      this.state = 'OPEN';
      this.nextAttempt = Date.now() + this.timeout;
    }
  }
}
```

---

## A05:2021 — Security Misconfiguration

### Description

보안 설정이 잘못되거나 기본값을 사용하여 발생하는 취약점입니다.

### Checklist

- [ ] **Default credentials removed**: 기본 계정 및 패스워드 제거
- [ ] **Error handling**: 스택 트레이스 및 상세 오류 정보 노출 방지
- [ ] **Security headers**: CSP, HSTS, X-Frame-Options 등 설정
- [ ] **Unnecessary features disabled**: 불필요한 기능, 포트, 서비스 비활성화
- [ ] **Latest patches**: 시스템 및 프레임워크 최신 보안 패치 적용
- [ ] **Secure defaults**: 안전한 기본 설정 사용
- [ ] **Principle of least functionality**: 필요한 기능만 활성화
- [ ] **Segmentation**: 네트워크 세그멘테이션 및 방화벽 설정
- [ ] **Automated security scanning**: 보안 설정 자동 검증
- [ ] **Cloud security**: 클라우드 리소스의 보안 그룹, IAM 정책 검토

### Security Headers Quick Reference

| Header | Value | Purpose |
|--------|-------|---------|
| `Content-Security-Policy` | `default-src 'self'; script-src 'self' 'unsafe-inline'; object-src 'none'` | XSS 및 데이터 주입 공격 방지 |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | HTTPS 강제 적용 |
| `X-Content-Type-Options` | `nosniff` | MIME 타입 스니핑 방지 |
| `X-Frame-Options` | `DENY` or `SAMEORIGIN` | 클릭재킹 방지 |
| `X-XSS-Protection` | `1; mode=block` | XSS 필터 활성화 (레거시 브라우저용) |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Referrer 정보 노출 제한 |
| `Permissions-Policy` | `geolocation=(), microphone=(), camera=()` | 브라우저 기능 접근 제한 |

### Implementation Examples

#### Express.js - Security Headers

```typescript
import helmet from 'helmet';

// ✅ Helmet을 사용한 보안 헤더 설정
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'"],
      fontSrc: ["'self'"],
      objectSrc: ["'none'"],
      mediaSrc: ["'self'"],
      frameSrc: ["'none'"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true,
  },
  frameguard: {
    action: 'deny',
  },
}));
```

#### NestJS - Global Error Filter

```typescript
// ✅ 안전한 에러 처리 - 스택 트레이스 노출 방지
@Catch()
export class GlobalExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse();
    const request = ctx.getRequest();

    const status = exception instanceof HttpException
      ? exception.getStatus()
      : HttpStatus.INTERNAL_SERVER_ERROR;

    // Log full error for debugging
    console.error('Exception:', exception);

    // Return sanitized error to client
    response.status(status).json({
      statusCode: status,
      timestamp: new Date().toISOString(),
      path: request.url,
      message: exception instanceof HttpException
        ? exception.message
        : 'Internal server error',
      // ❌ Do NOT include: stack trace, sensitive details
    });
  }
}
```

---

## A06:2021 — Vulnerable and Outdated Components

### Description

취약점이 있는 라이브러리, 프레임워크, 기타 소프트웨어 컴포넌트를 사용하여 발생하는 보안 문제입니다.

### Checklist

- [ ] **Component inventory**: 사용 중인 모든 컴포넌트 및 버전 목록 유지
- [ ] **Dependency scanning**: npm audit, safety, OWASP Dependency-Check 실행
- [ ] **Automated updates**: Dependabot, Renovate 등 자동 업데이트 도구 사용
- [ ] **Remove unused dependencies**: 사용하지 않는 의존성 제거
- [ ] **Secure sources**: 공식 리포지토리에서만 컴포넌트 다운로드
- [ ] **Vulnerability monitoring**: CVE 알림 구독 및 모니터링
- [ ] **Update strategy**: 보안 패치 적용 프로세스 수립
- [ ] **License compliance**: 라이선스 검토 및 준수
- [ ] **SBOM (Software Bill of Materials)**: 소프트웨어 구성 명세서 생성
- [ ] **Version pinning**: 의존성 버전 고정 및 관리

### Tools and Commands

```bash
# Node.js - npm audit
npm audit
npm audit fix

# Python - safety
pip install safety
safety check

# Java - OWASP Dependency Check
mvn org.owasp:dependency-check-maven:check

# Automated scanning in CI/CD
- name: Run security audit
  run: |
    npm audit --audit-level=high
    npm outdated
```

### Dependabot Configuration

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    labels:
      - "dependencies"
      - "security"
```

---

## A07:2021 — Identification and Authentication Failures

### Description

인증 메커니즘의 취약점으로 공격자가 다른 사용자의 계정을 탈취할 수 있는 문제입니다.

### Checklist

- [ ] **Multi-factor authentication**: 중요 계정에 MFA 적용
- [ ] **Strong password policy**: 최소 8자, 복잡도 요구사항
- [ ] **Credential stuffing protection**: Breached password 데이터베이스 검증
- [ ] **Session management**: 로그인 후 세션 ID 재생성
- [ ] **Brute force protection**: 로그인 시도 횟수 제한
- [ ] **Account lockout**: N회 실패 시 계정 잠금
- [ ] **Secure password recovery**: 안전한 패스워드 재설정 플로우
- [ ] **Session timeout**: 유휴 시간 및 절대 시간 초과 설정
- [ ] **Secure credential storage**: 패스워드는 bcrypt/argon2로 해싱
- [ ] **CAPTCHA**: 자동화 공격 방지

### Implementation Examples

#### Password Hashing - bcrypt

```typescript
import * as bcrypt from 'bcrypt';

const SALT_ROUNDS = 12;
const MAX_LOGIN_ATTEMPTS = 5;
const LOCKOUT_TIME = 15 * 60 * 1000; // 15 minutes

class AuthService {
  async register(username: string, password: string) {
    // Check password strength
    if (!this.isStrongPassword(password)) {
      throw new Error('Password does not meet requirements');
    }

    // Check against breached passwords (use haveibeenpwned API)
    if (await this.isBreachedPassword(password)) {
      throw new Error('This password has been exposed in a data breach');
    }

    const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);
    return userRepository.create({ username, password: hashedPassword });
  }

  async login(username: string, password: string) {
    const user = await userRepository.findByUsername(username);

    if (!user) {
      // Use same timing to prevent user enumeration
      await bcrypt.hash(password, SALT_ROUNDS);
      throw new Error('Invalid credentials');
    }

    // Check if account is locked
    if (user.lockedUntil && user.lockedUntil > new Date()) {
      throw new Error('Account is temporarily locked');
    }

    const isValid = await bcrypt.compare(password, user.password);

    if (!isValid) {
      await this.handleFailedLogin(user);
      throw new Error('Invalid credentials');
    }

    await this.handleSuccessfulLogin(user);
    return this.generateSession(user);
  }

  private async handleFailedLogin(user: User) {
    user.loginAttempts++;

    if (user.loginAttempts >= MAX_LOGIN_ATTEMPTS) {
      user.lockedUntil = new Date(Date.now() + LOCKOUT_TIME);
      // Send alert email
    }

    await userRepository.save(user);
  }

  private async handleSuccessfulLogin(user: User) {
    user.loginAttempts = 0;
    user.lockedUntil = null;
    user.lastLoginAt = new Date();
    await userRepository.save(user);
  }

  private isStrongPassword(password: string): boolean {
    return password.length >= 8 &&
      /[A-Z]/.test(password) &&
      /[a-z]/.test(password) &&
      /[0-9]/.test(password) &&
      /[^A-Za-z0-9]/.test(password);
  }
}
```

---

## A08:2021 — Software and Data Integrity Failures

### Description

소프트웨어 업데이트, CI/CD 파이프라인, 역직렬화 과정에서 무결성 검증이 부족하여 발생하는 취약점입니다.

### Checklist

- [ ] **CI/CD pipeline security**: 파이프라인 접근 제어 및 감사
- [ ] **Dependency integrity**: 의존성 무결성 검증 (lock files, checksums)
- [ ] **Code signing**: 배포 아티팩트에 디지털 서명
- [ ] **Insecure deserialization prevention**: 신뢰할 수 없는 데이터 역직렬화 방지
- [ ] **SRI (Subresource Integrity)**: CDN 리소스 무결성 검증
- [ ] **Auto-update verification**: 자동 업데이트 시 서명 검증
- [ ] **Supply chain security**: 공급망 공격 방지
- [ ] **Artifact repository security**: 내부 아티팩트 저장소 보안
- [ ] **Secrets management**: CI/CD 시크릿 안전하게 관리
- [ ] **Build reproducibility**: 재현 가능한 빌드

### Implementation Examples

#### Subresource Integrity (SRI)

```html
<!-- ✅ CDN 스크립트에 무결성 검증 추가 -->
<script
  src="https://cdn.example.com/library.js"
  integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
  crossorigin="anonymous">
</script>
```

#### Package Lock File Verification

```bash
# ✅ package-lock.json을 사용한 의존성 무결성 검증
npm ci  # package-lock.json을 정확히 따름 (npm install 대신)

# ✅ Python requirements.txt에 해시 포함
# requirements.txt
requests==2.31.0 \
    --hash=sha256:942c5a758f98d0e8e7bcac8d82c4fb5e5b5e0e0c9c8c8d8c8c8c8c8c8c8c8c
```

---

## A09:2021 — Security Logging and Monitoring Failures

### Description

보안 관련 이벤트의 로깅 및 모니터링이 부족하여 공격 탐지 및 대응이 지연되는 문제입니다.

### Checklist

- [ ] **Login attempts logged**: 모든 로그인 시도 (성공/실패) 로깅
- [ ] **Access control failures logged**: 권한 거부 이벤트 로깅
- [ ] **Input validation failures**: 검증 실패 로깅
- [ ] **Alerting configured**: 비정상 패턴 알림 설정
- [ ] **Tamper-proof logs**: 로그 변조 방지 (중앙 집중식 로깅)
- [ ] **Log retention**: 법적 요구사항에 맞는 로그 보관 기간
- [ ] **Sensitive data redaction**: 로그에 민감 정보 (패스워드, 카드번호) 제외
- [ ] **Structured logging**: 파싱 가능한 구조화된 로그 (JSON)
- [ ] **High-value transaction logging**: 중요 트랜잭션 감사 추적
- [ ] **Security monitoring tools**: SIEM 도구 연동

### Implementation Examples

#### Structured Security Logging

```typescript
import * as winston from 'winston';

const logger = winston.createLogger({
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'security.log' }),
  ],
});

// ✅ 보안 이벤트 로깅
class SecurityLogger {
  logLoginAttempt(username: string, success: boolean, ip: string) {
    logger.info('LOGIN_ATTEMPT', {
      event: 'login_attempt',
      username,
      success,
      ip,
      timestamp: new Date().toISOString(),
      // ❌ Do NOT log: password
    });
  }

  logAccessDenied(userId: string, resource: string, action: string) {
    logger.warn('ACCESS_DENIED', {
      event: 'access_denied',
      userId,
      resource,
      action,
      timestamp: new Date().toISOString(),
    });
  }

  logSensitiveOperation(userId: string, operation: string, details: any) {
    logger.info('SENSITIVE_OPERATION', {
      event: 'sensitive_operation',
      userId,
      operation,
      details: this.redactSensitiveData(details),
      timestamp: new Date().toISOString(),
    });
  }

  private redactSensitiveData(data: any): any {
    // Redact passwords, credit cards, etc.
    const redacted = { ...data };
    if (redacted.password) redacted.password = '[REDACTED]';
    if (redacted.creditCard) redacted.creditCard = '[REDACTED]';
    return redacted;
  }
}
```

---

## A10:2021 — Server-Side Request Forgery (SSRF)

### Description

웹 애플리케이션이 사용자가 제공한 URL을 검증하지 않고 요청하여 내부 시스템에 접근하는 취약점입니다.

### Checklist

- [ ] **URL validation**: 사용자 제공 URL 검증 및 제한
- [ ] **Allowlisted destinations**: 허용된 도메인/IP만 접근 가능
- [ ] **Network segmentation**: 내부 네트워크 세그멘테이션
- [ ] **Disable redirects**: HTTP 리다이렉트 비활성화 또는 제한
- [ ] **Deny private IP ranges**: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 차단
- [ ] **Deny localhost**: 127.0.0.1, ::1 접근 차단
- [ ] **Deny metadata endpoints**: 169.254.169.254 (AWS, Azure, GCP 메타데이터) 차단
- [ ] **Response validation**: 응답 타입 및 크기 검증
- [ ] **Timeout enforcement**: 요청 타임아웃 설정
- [ ] **Authentication required**: 외부 요청에 인증 요구

### Implementation Examples

#### SSRF Prevention

```typescript
import * as url from 'url';
import axios from 'axios';

class SafeHttpClient {
  private allowedDomains = ['api.example.com', 'trusted-service.com'];
  private blockedIpRanges = [
    /^127\./,  // localhost
    /^10\./,   // private
    /^172\.(1[6-9]|2[0-9]|3[0-1])\./,  // private
    /^192\.168\./,  // private
    /^169\.254\./,  // link-local, cloud metadata
  ];

  async fetch(targetUrl: string): Promise<any> {
    const parsed = url.parse(targetUrl);

    // ✅ Validate protocol
    if (parsed.protocol !== 'https:') {
      throw new Error('Only HTTPS is allowed');
    }

    // ✅ Validate domain allowlist
    if (!this.allowedDomains.includes(parsed.hostname)) {
      throw new Error('Domain not in allowlist');
    }

    // ✅ Block private IP ranges
    const ip = await this.resolveHostname(parsed.hostname);
    if (this.isBlockedIp(ip)) {
      throw new Error('Access to private IP ranges is forbidden');
    }

    // ✅ Make request with timeout and size limit
    const response = await axios.get(targetUrl, {
      timeout: 5000,
      maxContentLength: 10 * 1024 * 1024, // 10MB
      maxRedirects: 0,  // Disable redirects
    });

    return response.data;
  }

  private isBlockedIp(ip: string): boolean {
    return this.blockedIpRanges.some(pattern => pattern.test(ip));
  }

  private async resolveHostname(hostname: string): Promise<string> {
    // Implement DNS resolution
    // This is a simplified example
    return hostname;
  }
}
```

---

## Summary Table: OWASP Top 10 Quick Reference

| Rank | Vulnerability | Key Prevention |
|------|--------------|----------------|
| A01 | Broken Access Control | Server-side enforcement, deny by default |
| A02 | Cryptographic Failures | TLS 1.2+, strong algorithms, proper key management |
| A03 | Injection | Parameterized queries, input validation |
| A04 | Insecure Design | Threat modeling, secure patterns |
| A05 | Security Misconfiguration | Secure defaults, security headers |
| A06 | Vulnerable Components | Dependency scanning, automated updates |
| A07 | Authentication Failures | MFA, strong passwords, brute force protection |
| A08 | Data Integrity Failures | Code signing, SRI, secure deserialization |
| A09 | Logging Failures | Log security events, tamper-proof storage |
| A10 | SSRF | URL validation, allowlist, block private IPs |

---

## Additional Resources

- [OWASP Top 10 2021 Official](https://owasp.org/Top10/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [SANS Top 25](https://www.sans.org/top25-software-errors/)
