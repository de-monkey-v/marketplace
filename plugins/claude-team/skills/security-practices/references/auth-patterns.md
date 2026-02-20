# Authentication and Authorization Patterns

이 문서는 현대적인 인증 및 권한 관리 패턴에 대한 종합 가이드입니다. OAuth2, OIDC, JWT, MFA 등 주요 인증 메커니즘을 다룹니다.

## Authentication Methods Comparison

### Overview Table

| Method | Security | Complexity | Best For | Session State |
|--------|----------|-----------|----------|---------------|
| **Session-based** | High | Low | Traditional web apps, server-side rendering | Stateful (server) |
| **JWT** | Medium-High | Medium | SPA, Mobile, Microservices | Stateless (client) |
| **OAuth2 + OIDC** | High | High | Third-party auth, SSO, social login | Depends on flow |
| **API Key** | Low-Medium | Low | Server-to-server, simple APIs | Stateless |
| **mTLS** | Very High | High | Service mesh, B2B, microservices | Stateless |
| **SAML** | High | Very High | Enterprise SSO | Stateful |

### Detailed Comparison

#### Session-Based Authentication

**How it works**:
1. User submits credentials
2. Server validates and creates session
3. Session ID stored in cookie
4. Server validates session ID on each request

**Pros**:
- Simple to implement
- Easy to revoke sessions
- Proven security model
- Server controls session lifecycle

**Cons**:
- Requires server-side session storage
- Harder to scale horizontally
- CSRF protection needed
- Not suitable for mobile/SPA

**Use cases**: Traditional web applications, admin panels

#### JWT (JSON Web Token)

**How it works**:
1. User authenticates
2. Server issues signed JWT
3. Client stores JWT (httpOnly cookie or memory)
4. Client sends JWT in Authorization header
5. Server validates signature and claims

**Pros**:
- Stateless (no server-side storage)
- Scales horizontally
- Works across domains
- Contains user data (claims)

**Cons**:
- Cannot revoke before expiry (without additional infrastructure)
- Larger payload than session ID
- XSS risk if stored in localStorage
- Replay attacks if not properly secured

**Use cases**: SPAs, mobile apps, microservices

#### OAuth2 + OIDC

**How it works**:
1. User redirected to authorization server
2. User authenticates and consents
3. Authorization server issues authorization code
4. Client exchanges code for access token
5. Client uses access token to access resources

**Pros**:
- Industry standard
- Delegated authorization
- Third-party login support
- Refresh token for long-lived access
- Separation of concerns

**Cons**:
- Complex implementation
- Multiple flows for different scenarios
- Requires HTTPS
- State management

**Use cases**: Social login, SSO, third-party API access

#### API Key

**How it works**:
1. User generates API key from dashboard
2. API key sent in header (X-API-Key)
3. Server validates API key

**Pros**:
- Very simple
- Suitable for server-to-server
- Easy to rotate

**Cons**:
- No built-in expiration
- Risk if leaked
- No user context
- Limited authorization

**Use cases**: Public APIs, webhooks, server-to-server

#### mTLS (Mutual TLS)

**How it works**:
1. Client and server both present certificates
2. Both sides validate certificates
3. Encrypted channel established

**Pros**:
- Very strong authentication
- Encrypted transport
- No credentials to steal
- Works at transport layer

**Cons**:
- Certificate management complexity
- Not user-friendly
- Requires PKI infrastructure

**Use cases**: Service mesh, microservices, B2B integrations

---

## JWT Patterns

### JWT Structure

A JWT consists of three parts separated by dots (`.`):

```
Header.Payload.Signature
```

#### Header

```json
{
  "alg": "RS256",
  "typ": "JWT"
}
```

#### Payload (Claims)

```json
{
  "iss": "https://auth.example.com",
  "sub": "user123",
  "aud": "https://api.example.com",
  "exp": 1708416000,
  "iat": 1708412400,
  "jti": "unique-token-id",
  "roles": ["user", "editor"]
}
```

#### Signature

```
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret
)
```

### Standard JWT Claims

| Claim | Name | Description |
|-------|------|-------------|
| `iss` | Issuer | Who issued the token |
| `sub` | Subject | User ID or identifier |
| `aud` | Audience | Intended recipient |
| `exp` | Expiration | Token expiry timestamp |
| `iat` | Issued At | Token creation timestamp |
| `nbf` | Not Before | Token not valid before this time |
| `jti` | JWT ID | Unique token identifier (prevent replay) |

### JWT Best Practices

- [ ] **Short expiry**: Access token 15 minutes, refresh token 7 days
- [ ] **Asymmetric signing**: Use RS256 (RSA) for distributed systems, HS256 only for single server
- [ ] **httpOnly cookie**: Store in httpOnly cookie, NOT localStorage (XSS protection)
- [ ] **Include standard claims**: iss, sub, exp, iat, jti
- [ ] **Validate all claims**: Check expiry, audience, issuer on every request
- [ ] **Token refresh flow**: Implement refresh token mechanism
- [ ] **Token revocation**: Implement blacklist or short-lived tokens
- [ ] **Secure transmission**: Always use HTTPS
- [ ] **Minimal payload**: Only include necessary claims
- [ ] **Audience validation**: Verify token is for your service

### JWT Implementation Examples

#### TypeScript/NestJS - JWT Generation and Validation

```typescript
import { JwtService } from '@nestjs/jwt';
import { Injectable } from '@nestjs/common';

@Injectable()
export class AuthService {
  constructor(private jwtService: JwtService) {}

  async generateTokens(user: User) {
    const payload = {
      sub: user.id,
      email: user.email,
      roles: user.roles,
    };

    const accessToken = this.jwtService.sign(payload, {
      expiresIn: '15m',
      issuer: 'https://auth.example.com',
      audience: 'https://api.example.com',
    });

    const refreshToken = this.jwtService.sign(
      { sub: user.id, type: 'refresh' },
      {
        expiresIn: '7d',
        issuer: 'https://auth.example.com',
      }
    );

    return { accessToken, refreshToken };
  }

  async validateToken(token: string) {
    try {
      const payload = this.jwtService.verify(token, {
        issuer: 'https://auth.example.com',
        audience: 'https://api.example.com',
      });

      // Check if token is blacklisted (if using blacklist strategy)
      if (await this.isTokenBlacklisted(payload.jti)) {
        throw new Error('Token has been revoked');
      }

      return payload;
    } catch (error) {
      throw new Error('Invalid token');
    }
  }

  async refreshTokens(refreshToken: string) {
    const payload = await this.validateRefreshToken(refreshToken);
    const user = await this.userService.findById(payload.sub);
    return this.generateTokens(user);
  }
}
```

#### Python/FastAPI - JWT with httpOnly Cookies

```python
from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

app = FastAPI()
security = HTTPBearer()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": "https://auth.example.com",
        "aud": "https://api.example.com",
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer="https://auth.example.com",
            audience="https://api.example.com",
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/login")
async def login(username: str, password: str, response: Response):
    # Validate credentials
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.id, "email": user.email})

    # Set httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # HTTPS only
        samesite="strict",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {"message": "Login successful"}
```

### Token Refresh Flow

```
┌────────┐                                      ┌────────┐
│ Client │                                      │ Server │
└───┬────┘                                      └───┬────┘
    │                                               │
    │ 1. Request with access token                 │
    │──────────────────────────────────────────────>│
    │                                               │
    │ 2. 401 Unauthorized (token expired)          │
    │<──────────────────────────────────────────────│
    │                                               │
    │ 3. POST /auth/refresh (with refresh token)   │
    │──────────────────────────────────────────────>│
    │                                               │
    │ 4. Validate refresh token                    │
    │                                               │
    │ 5. New access + refresh tokens               │
    │<──────────────────────────────────────────────│
    │                                               │
    │ 6. Retry original request (with new token)   │
    │──────────────────────────────────────────────>│
    │                                               │
    │ 7. 200 OK (response)                         │
    │<──────────────────────────────────────────────│
```

#### Client-Side Token Refresh (React Example)

```typescript
// axios interceptor for automatic token refresh
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Call refresh endpoint
        const response = await axios.post('/auth/refresh', {
          refreshToken: getRefreshToken(),
        });

        const { accessToken, refreshToken } = response.data;

        // Store new tokens
        setAccessToken(accessToken);
        setRefreshToken(refreshToken);

        // Retry original request with new token
        originalRequest.headers['Authorization'] = `Bearer ${accessToken}`;
        return axios(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

---

## OAuth2 Flows

### Flow Comparison

| Flow | Use Case | Security | Complexity |
|------|----------|----------|-----------|
| **Authorization Code + PKCE** | SPA, Mobile | High (recommended) | Medium |
| **Authorization Code** | Server-side web app | High | Medium |
| **Client Credentials** | Machine-to-machine | Medium | Low |
| **Device Code** | Smart TV, CLI, IoT | Medium | Low |
| **Implicit** | Legacy SPA | Low (deprecated) | Low |
| **Resource Owner Password** | Trusted first-party apps | Low (not recommended) | Low |

### Authorization Code + PKCE Flow

PKCE (Proof Key for Code Exchange) prevents authorization code interception attacks. **This is the recommended flow for SPAs and mobile apps.**

#### Flow Diagram

```
┌────────┐                                 ┌──────────┐                      ┌──────────┐
│ Client │                                 │ Auth     │                      │ Resource │
│        │                                 │ Server   │                      │ Server   │
└───┬────┘                                 └────┬─────┘                      └────┬─────┘
    │                                           │                                 │
    │ 1. Generate code_verifier (random)       │                                 │
    │    code_challenge = SHA256(verifier)     │                                 │
    │                                           │                                 │
    │ 2. GET /authorize?                        │                                 │
    │    response_type=code&                    │                                 │
    │    client_id=xxx&                         │                                 │
    │    redirect_uri=xxx&                      │                                 │
    │    code_challenge=xxx&                    │                                 │
    │    code_challenge_method=S256             │                                 │
    │──────────────────────────────────────────>│                                 │
    │                                           │                                 │
    │ 3. User authenticates + consents          │                                 │
    │                                           │                                 │
    │ 4. Redirect to redirect_uri?code=xxx     │                                 │
    │<──────────────────────────────────────────│                                 │
    │                                           │                                 │
    │ 5. POST /token                            │                                 │
    │    grant_type=authorization_code&         │                                 │
    │    code=xxx&                              │                                 │
    │    redirect_uri=xxx&                      │                                 │
    │    code_verifier=xxx                      │                                 │
    │──────────────────────────────────────────>│                                 │
    │                                           │                                 │
    │                                           │ 6. Verify code_challenge        │
    │                                           │    matches code_verifier        │
    │                                           │                                 │
    │ 7. Access token + Refresh token          │                                 │
    │<──────────────────────────────────────────│                                 │
    │                                           │                                 │
    │ 8. GET /api/resource                      │                                 │
    │    Authorization: Bearer {access_token}   │                                 │
    │───────────────────────────────────────────────────────────────────────────>│
    │                                           │                                 │
    │ 9. Protected resource                     │                                 │
    │<───────────────────────────────────────────────────────────────────────────│
```

#### Implementation Example

```typescript
// Client-side PKCE implementation
class OAuth2Client {
  private codeVerifier: string;
  private codeChallenge: string;

  async initiateLogin() {
    // 1. Generate code verifier (random string)
    this.codeVerifier = this.generateRandomString(128);

    // 2. Generate code challenge (SHA256 hash)
    this.codeChallenge = await this.sha256(this.codeVerifier);

    // 3. Store code_verifier in session storage (temporary)
    sessionStorage.setItem('code_verifier', this.codeVerifier);

    // 4. Redirect to authorization endpoint
    const authUrl = new URL('https://auth.example.com/authorize');
    authUrl.searchParams.set('response_type', 'code');
    authUrl.searchParams.set('client_id', 'your-client-id');
    authUrl.searchParams.set('redirect_uri', 'https://app.example.com/callback');
    authUrl.searchParams.set('scope', 'openid profile email');
    authUrl.searchParams.set('code_challenge', this.codeChallenge);
    authUrl.searchParams.set('code_challenge_method', 'S256');
    authUrl.searchParams.set('state', this.generateRandomString(32)); // CSRF protection

    window.location.href = authUrl.toString();
  }

  async handleCallback(code: string) {
    // 5. Retrieve code_verifier from storage
    const codeVerifier = sessionStorage.getItem('code_verifier');
    if (!codeVerifier) {
      throw new Error('Code verifier not found');
    }

    // 6. Exchange authorization code for tokens
    const response = await fetch('https://auth.example.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        code,
        redirect_uri: 'https://app.example.com/callback',
        client_id: 'your-client-id',
        code_verifier: codeVerifier,
      }),
    });

    const tokens = await response.json();
    // { access_token, refresh_token, id_token, expires_in }

    // 7. Clear code_verifier
    sessionStorage.removeItem('code_verifier');

    return tokens;
  }

  private generateRandomString(length: number): string {
    const array = new Uint8Array(length);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  private async sha256(plain: string): Promise<string> {
    const encoder = new TextEncoder();
    const data = encoder.encode(plain);
    const hash = await crypto.subtle.digest('SHA-256', data);
    return btoa(String.fromCharCode(...new Uint8Array(hash)))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, ''); // Base64URL encoding
  }
}
```

### Client Credentials Flow

For server-to-server authentication (no user context).

```typescript
async function getAccessToken() {
  const response = await fetch('https://auth.example.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'client_credentials',
      client_id: 'your-client-id',
      client_secret: 'your-client-secret',
      scope: 'api.read api.write',
    }),
  });

  const { access_token, expires_in } = await response.json();
  return access_token;
}
```

---

## OIDC (OpenID Connect)

OpenID Connect is an identity layer on top of OAuth2. It adds:
- **ID Token**: JWT containing user identity information
- **UserInfo Endpoint**: Retrieve user profile data
- **Standard Scopes**: `openid`, `profile`, `email`

### ID Token vs Access Token

| Aspect | ID Token | Access Token |
|--------|----------|--------------|
| **Purpose** | Authenticate user | Authorize access to resources |
| **Format** | Always JWT | Opaque or JWT |
| **Audience** | Client application | Resource server |
| **Contains** | User identity (email, name) | Permissions, scopes |
| **Validation** | Client validates | Resource server validates |

### Standard OIDC Scopes

| Scope | Claims Included |
|-------|----------------|
| `openid` | Required for OIDC, returns `sub` (user ID) |
| `profile` | `name`, `family_name`, `given_name`, `picture`, `locale` |
| `email` | `email`, `email_verified` |
| `address` | `address` (formatted address) |
| `phone` | `phone_number`, `phone_number_verified` |

### ID Token Example

```json
{
  "iss": "https://auth.example.com",
  "sub": "user123",
  "aud": "your-client-id",
  "exp": 1708416000,
  "iat": 1708412400,
  "auth_time": 1708412400,
  "nonce": "random-nonce",
  "email": "user@example.com",
  "email_verified": true,
  "name": "John Doe",
  "picture": "https://example.com/photo.jpg"
}
```

### UserInfo Endpoint

```typescript
async function getUserInfo(accessToken: string) {
  const response = await fetch('https://auth.example.com/userinfo', {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
  });

  const userInfo = await response.json();
  // { sub, email, name, picture, ... }
  return userInfo;
}
```

---

## Authorization Patterns

### RBAC (Role-Based Access Control)

Users are assigned roles, and roles have permissions.

```typescript
// Define roles and permissions
const roles = {
  admin: ['read', 'write', 'delete', 'manage_users', 'manage_roles'],
  editor: ['read', 'write', 'delete'],
  viewer: ['read'],
};

class RBACService {
  hasPermission(user: User, permission: string): boolean {
    return user.roles.some(role =>
      roles[role]?.includes(permission)
    );
  }

  hasRole(user: User, requiredRole: string): boolean {
    return user.roles.includes(requiredRole);
  }
}

// Middleware
function requirePermission(permission: string) {
  return (req, res, next) => {
    if (!rbacService.hasPermission(req.user, permission)) {
      return res.status(403).json({ error: 'Forbidden' });
    }
    next();
  };
}

// Usage
app.delete('/documents/:id', requirePermission('delete'), deleteDocument);
```

### ABAC (Attribute-Based Access Control)

Access decisions based on attributes of user, resource, and environment.

```typescript
interface Policy {
  resource: string;
  action: string;
  condition: (user: User, resource: any, context: any) => boolean;
}

const policies: Policy[] = [
  {
    resource: 'document',
    action: 'edit',
    condition: (user, document, context) =>
      // User can edit if they are the owner OR have editor role
      user.id === document.ownerId || user.roles.includes('editor'),
  },
  {
    resource: 'document',
    action: 'delete',
    condition: (user, document, context) =>
      // User can delete only if they are the owner AND document is not published
      user.id === document.ownerId && !document.published,
  },
  {
    resource: 'admin_panel',
    action: 'access',
    condition: (user, resource, context) =>
      // Only admins can access from corporate network
      user.roles.includes('admin') && context.ipRange === 'corporate',
  },
];

class ABACService {
  canAccess(user: User, resource: any, action: string, context: any): boolean {
    const policy = policies.find(p =>
      p.resource === resource.type && p.action === action
    );

    if (!policy) {
      return false; // Deny by default
    }

    return policy.condition(user, resource, context);
  }
}

// Usage
app.put('/documents/:id', async (req, res) => {
  const document = await documentService.findById(req.params.id);
  const context = { ipRange: getIpRange(req.ip) };

  if (!abacService.canAccess(req.user, document, 'edit', context)) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  // Proceed with update
});
```

---

## MFA (Multi-Factor Authentication)

### MFA Methods Comparison

| Method | Security | UX | Cost | Phishing Resistant |
|--------|----------|-----|------|-------------------|
| **TOTP (Authenticator App)** | High | Good | Free | No |
| **WebAuthn/FIDO2** | Very High | Excellent | Low-Medium | Yes |
| **SMS OTP** | Low-Medium | Good | High | No |
| **Email OTP** | Low | Good | Free | No |
| **Push Notification** | Medium-High | Excellent | Medium | No |
| **Hardware Token** | Very High | Medium | High | Yes |

### TOTP (Time-based One-Time Password)

Used by Google Authenticator, Authy, etc.

```typescript
import * as speakeasy from 'speakeasy';
import * as QRCode from 'qrcode';

class TOTPService {
  async generateSecret(user: User) {
    const secret = speakeasy.generateSecret({
      name: `MyApp (${user.email})`,
      issuer: 'MyApp',
    });

    // Generate QR code for user to scan
    const qrCodeUrl = await QRCode.toDataURL(secret.otpauth_url);

    // Store secret in database (encrypted)
    await userService.updateMfaSecret(user.id, secret.base32);

    return {
      secret: secret.base32,
      qrCode: qrCodeUrl,
    };
  }

  verifyToken(secret: string, token: string): boolean {
    return speakeasy.totp.verify({
      secret,
      encoding: 'base32',
      token,
      window: 1, // Allow 1 step before/after for clock drift
    });
  }

  async enableMfa(user: User, token: string) {
    if (!this.verifyToken(user.mfaSecret, token)) {
      throw new Error('Invalid token');
    }

    await userService.enableMfa(user.id);
  }
}

// Login flow with MFA
app.post('/login', async (req, res) => {
  const { email, password, mfaToken } = req.body;

  const user = await userService.findByEmail(email);
  if (!user || !await bcrypt.compare(password, user.password)) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  if (user.mfaEnabled) {
    if (!mfaToken) {
      return res.status(200).json({ requireMfa: true });
    }

    if (!totpService.verifyToken(user.mfaSecret, mfaToken)) {
      return res.status(401).json({ error: 'Invalid MFA token' });
    }
  }

  // Generate session or JWT
  const accessToken = generateAccessToken(user);
  res.json({ accessToken });
});
```

### WebAuthn / FIDO2

Passwordless authentication using biometrics or hardware keys.

```typescript
import { generateRegistrationOptions, verifyRegistrationResponse } from '@simplewebauthn/server';

class WebAuthnService {
  async generateRegistrationOptions(user: User) {
    const options = await generateRegistrationOptions({
      rpName: 'MyApp',
      rpID: 'example.com',
      userID: user.id,
      userName: user.email,
      attestationType: 'none',
      authenticatorSelection: {
        residentKey: 'preferred',
        userVerification: 'preferred',
      },
    });

    // Store challenge temporarily
    await redis.set(`webauthn:${user.id}`, options.challenge, 'EX', 300);

    return options;
  }

  async verifyRegistration(user: User, response: any) {
    const expectedChallenge = await redis.get(`webauthn:${user.id}`);

    const verification = await verifyRegistrationResponse({
      response,
      expectedChallenge,
      expectedOrigin: 'https://example.com',
      expectedRPID: 'example.com',
    });

    if (verification.verified) {
      // Store credential in database
      await userService.addWebAuthnCredential(user.id, {
        credentialID: verification.registrationInfo.credentialID,
        credentialPublicKey: verification.registrationInfo.credentialPublicKey,
        counter: verification.registrationInfo.counter,
      });
    }

    return verification.verified;
  }
}
```

---

## Session Security

### Secure Cookie Configuration

```typescript
app.use(session({
  secret: process.env.SESSION_SECRET,
  name: 'sessionId', // Don't use default 'connect.sid'
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,      // Prevents JavaScript access (XSS protection)
    secure: true,        // HTTPS only
    sameSite: 'strict',  // CSRF protection
    maxAge: 3600000,     // 1 hour
    domain: '.example.com', // Allow subdomains
  },
  store: new RedisStore({ client: redisClient }), // Use external session store
}));
```

### Session Management Best Practices

```typescript
class SessionService {
  async createSession(user: User, req: Request) {
    // 1. Regenerate session ID after login (prevent session fixation)
    await this.regenerateSessionId(req);

    // 2. Store session data
    req.session.userId = user.id;
    req.session.createdAt = Date.now();
    req.session.lastActivityAt = Date.now();
    req.session.ipAddress = req.ip;
    req.session.userAgent = req.headers['user-agent'];

    // 3. Set absolute timeout
    req.session.cookie.expires = new Date(Date.now() + 8 * 3600000); // 8 hours
  }

  async validateSession(req: Request) {
    if (!req.session.userId) {
      throw new Error('Not authenticated');
    }

    // Check idle timeout (30 minutes)
    const idleTime = Date.now() - req.session.lastActivityAt;
    if (idleTime > 30 * 60 * 1000) {
      await this.destroySession(req);
      throw new Error('Session expired due to inactivity');
    }

    // Check absolute timeout (8 hours)
    const sessionAge = Date.now() - req.session.createdAt;
    if (sessionAge > 8 * 3600000) {
      await this.destroySession(req);
      throw new Error('Session expired');
    }

    // Detect session hijacking (IP or User-Agent change)
    if (req.session.ipAddress !== req.ip ||
        req.session.userAgent !== req.headers['user-agent']) {
      await this.destroySession(req);
      throw new Error('Session validation failed');
    }

    // Update last activity
    req.session.lastActivityAt = Date.now();
  }

  async destroySession(req: Request) {
    return new Promise((resolve, reject) => {
      req.session.destroy(err => {
        if (err) reject(err);
        else resolve();
      });
    });
  }

  private async regenerateSessionId(req: Request) {
    const oldData = { ...req.session };
    return new Promise((resolve, reject) => {
      req.session.regenerate(err => {
        if (err) reject(err);
        Object.assign(req.session, oldData);
        resolve();
      });
    });
  }
}
```

---

## Password Security

### Password Hashing Algorithms

| Algorithm | Recommendation | Computational Cost |
|-----------|---------------|-------------------|
| **argon2** | Best (winner of PHC) | Adjustable (memory-hard) |
| **bcrypt** | Good | Adjustable (work factor) |
| **scrypt** | Good | Adjustable (memory-hard) |
| **PBKDF2** | Acceptable | Adjustable (iterations) |
| **SHA-256** | Bad (too fast) | Fixed |
| **MD5** | Insecure | Fixed |

### Password Policy

```typescript
class PasswordService {
  private MIN_LENGTH = 8;
  private MAX_LENGTH = 128;

  validatePasswordStrength(password: string): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (password.length < this.MIN_LENGTH) {
      errors.push(`Password must be at least ${this.MIN_LENGTH} characters`);
    }

    if (password.length > this.MAX_LENGTH) {
      errors.push(`Password must not exceed ${this.MAX_LENGTH} characters`);
    }

    if (!/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }

    if (!/[a-z]/.test(password)) {
      errors.push('Password must contain at least one lowercase letter');
    }

    if (!/[0-9]/.test(password)) {
      errors.push('Password must contain at least one number');
    }

    if (!/[^A-Za-z0-9]/.test(password)) {
      errors.push('Password must contain at least one special character');
    }

    // Check against common passwords
    if (this.isCommonPassword(password)) {
      errors.push('This password is too common');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  async isBreachedPassword(password: string): Promise<boolean> {
    // Use HaveIBeenPwned API (k-anonymity model)
    const sha1Hash = crypto.createHash('sha1').update(password).digest('hex').toUpperCase();
    const prefix = sha1Hash.substring(0, 5);
    const suffix = sha1Hash.substring(5);

    const response = await fetch(`https://api.pwnedpasswords.com/range/${prefix}`);
    const hashes = await response.text();

    return hashes.split('\n').some(line => line.startsWith(suffix));
  }

  async hashPassword(password: string): Promise<string> {
    const validation = this.validatePasswordStrength(password);
    if (!validation.valid) {
      throw new Error(validation.errors.join(', '));
    }

    if (await this.isBreachedPassword(password)) {
      throw new Error('This password has been exposed in a data breach');
    }

    return bcrypt.hash(password, 12); // 12 rounds
  }
}
```

---

## Security Decision Matrix

Choose the right authentication method based on your use case:

| Scenario | Recommended Auth | Reason | Implementation |
|----------|-----------------|--------|----------------|
| **SPA + Own Backend** | JWT (httpOnly cookie) + PKCE | Stateless, XSS safe, mobile-friendly | Access token in httpOnly cookie, refresh token in secure storage |
| **Traditional MPA** | Session-based | Simple, secure, server-controlled | Session ID in httpOnly cookie, server-side storage |
| **Mobile App** | OAuth2 + PKCE + JWT | Standard, refresh tokens, secure | Authorization Code + PKCE flow, store tokens in secure keychain |
| **Microservices (Internal)** | JWT with service accounts | Stateless, distributed verification | Short-lived JWT signed with RS256, service-to-service |
| **Microservices (Edge)** | API Gateway + JWT | Centralized authentication | Gateway validates token, passes claims to services |
| **Third-party Login** | OIDC (OAuth2) | Standard identity protocol | Google, GitHub, Azure AD integration |
| **API for Partners** | API Key + OAuth2 | Flexible, trackable, revocable | API key for identification, OAuth2 for authorization |
| **Admin Panel** | Session + MFA | High security, audit trail | Session-based with TOTP or WebAuthn |
| **IoT Device** | Device Code Flow | No browser, limited input | OAuth2 Device Code Flow |
| **CLI Tool** | Device Code or Personal Access Token | User-friendly for CLI | GitHub-style personal access tokens |

---

## Summary: Best Practices

### General Guidelines

1. **Always use HTTPS** in production
2. **Never store passwords in plaintext**
3. **Use bcrypt/argon2** for password hashing
4. **Implement MFA** for sensitive operations
5. **Use short-lived access tokens** (15 minutes)
6. **Implement token refresh** mechanism
7. **Validate all tokens** on every request
8. **Use httpOnly cookies** for web apps (prevent XSS)
9. **Implement rate limiting** on authentication endpoints
10. **Log all authentication events** (success and failures)
11. **Use secure session management** (regenerate session ID, set timeouts)
12. **Check for breached passwords** during registration
13. **Implement account lockout** after failed attempts
14. **Use PKCE** for OAuth2 in SPAs and mobile apps
15. **Revoke tokens** on logout

### Anti-Patterns to Avoid

- Storing JWT in localStorage (XSS risk)
- Using GET requests for sensitive operations
- Long-lived access tokens without refresh mechanism
- Weak password policies
- No rate limiting on login
- Exposing detailed error messages (user enumeration)
- Using MD5 or SHA-1 for password hashing
- OAuth2 Implicit Flow (use Authorization Code + PKCE instead)
- Trusting client-side validation only
- No MFA for admin accounts

---

## Additional Resources

- [OAuth 2.0 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
- [OpenID Connect Specification](https://openid.net/specs/openid-connect-core-1_0.html)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [WebAuthn Guide](https://webauthn.guide/)
