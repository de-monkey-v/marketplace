# REST API Design Patterns

Comprehensive guide to designing robust, scalable, and maintainable REST APIs.

## Table of Contents
- [Resource Naming Conventions](#resource-naming-conventions)
- [HTTP Methods](#http-methods)
- [Status Code Guide](#status-code-guide)
- [Error Response Format](#error-response-format)
- [Pagination Patterns](#pagination-patterns)
- [Filtering, Sorting, Field Selection](#filtering-sorting-field-selection)
- [Versioning Strategies](#versioning-strategies)
- [Rate Limiting](#rate-limiting)
- [Authentication & Authorization](#authentication--authorization)
- [HATEOAS](#hateoas-optional)
- [API Design Checklist](#api-design-checklist)

## Resource Naming Conventions

### Core Rules

1. **Use Nouns, Not Verbs**
   - Good: `/users`, `/posts`, `/orders`
   - Bad: `/getUsers`, `/createPost`, `/deleteOrder`

2. **Use Plural Nouns**
   - Good: `/users` (even for single resource: `/users/123`)
   - Bad: `/user`, `/user/123`

3. **Use Kebab-Case for Multi-Word Resources**
   - Good: `/user-profiles`, `/order-items`, `/shipping-addresses`
   - Bad: `/userProfiles`, `/order_items`, `/ShippingAddresses`

4. **Nested Resources for Relationships**
   - Good: `/users/{userId}/orders`
   - Good: `/posts/{postId}/comments`
   - Avoid: More than 3 levels deep

5. **Use Query Parameters Instead of Deep Nesting**
   - Good: `/comments?postId=123&userId=456`
   - Bad: `/users/456/posts/123/comments`

### Examples

```
# Users
GET    /users              # List all users
POST   /users              # Create a new user
GET    /users/{id}         # Get a specific user
PUT    /users/{id}         # Replace a user
PATCH  /users/{id}         # Update a user
DELETE /users/{id}         # Delete a user

# User's Orders (nested resource)
GET    /users/{id}/orders  # Get all orders for a user
POST   /users/{id}/orders  # Create an order for a user

# Orders (top-level resource)
GET    /orders             # List all orders (with filtering)
GET    /orders/{id}        # Get a specific order
PUT    /orders/{id}        # Update an order
DELETE /orders/{id}        # Cancel an order

# Order Items (avoid deep nesting)
GET    /order-items?orderId=123  # Better than /orders/123/items
```

### Anti-Patterns

```
# Bad: Verbs in URLs
POST /users/create
GET  /users/get/123
POST /orders/123/cancel

# Good: Use HTTP methods
POST   /users
GET    /users/123
DELETE /orders/123

# Bad: Mixing singular and plural
GET /user/123
GET /posts

# Good: Consistent plural
GET /users/123
GET /posts

# Bad: Deep nesting
GET /users/123/orders/456/items/789/details

# Good: Flatten with query params
GET /order-items/789?include=details
```

## HTTP Methods

| Method | CRUD Operation | Idempotent | Safe | Request Body | Response Body | Use Case |
|--------|---------------|------------|------|--------------|---------------|----------|
| GET | Read | Yes | Yes | No | Resource(s) | Retrieve data |
| POST | Create | No | No | Yes | Created resource | Create new resource |
| PUT | Replace | Yes | No | Yes | Updated resource | Replace entire resource |
| PATCH | Partial Update | No | No | Yes | Updated resource | Update specific fields |
| DELETE | Delete | Yes | No | Optional | 204 or deleted resource | Remove resource |
| HEAD | Read metadata | Yes | Yes | No | No body (headers only) | Check existence |
| OPTIONS | Get allowed methods | Yes | Yes | No | Allowed methods | CORS preflight |

### Method Details

#### GET
```http
GET /users?status=active&role=admin&limit=20

Response: 200 OK
{
  "data": [
    { "id": 1, "name": "Alice", "status": "active", "role": "admin" }
  ],
  "meta": {
    "total": 100,
    "page": 1,
    "limit": 20
  }
}
```

#### POST (Create)
```http
POST /users
Content-Type: application/json

{
  "name": "Bob",
  "email": "bob@example.com",
  "role": "user"
}

Response: 201 Created
Location: /users/123
{
  "id": 123,
  "name": "Bob",
  "email": "bob@example.com",
  "role": "user",
  "createdAt": "2026-02-20T10:00:00Z"
}
```

#### PUT (Replace)
```http
PUT /users/123
Content-Type: application/json

{
  "name": "Bob Smith",
  "email": "bob.smith@example.com",
  "role": "admin"
}

Response: 200 OK
{
  "id": 123,
  "name": "Bob Smith",
  "email": "bob.smith@example.com",
  "role": "admin",
  "updatedAt": "2026-02-20T11:00:00Z"
}
```

#### PATCH (Partial Update)
```http
PATCH /users/123
Content-Type: application/json

{
  "role": "admin"
}

Response: 200 OK
{
  "id": 123,
  "name": "Bob",
  "email": "bob@example.com",
  "role": "admin",
  "updatedAt": "2026-02-20T11:00:00Z"
}
```

#### DELETE
```http
DELETE /users/123

Response: 204 No Content
```

## Status Code Guide

### 2xx Success
| Code | Name | When to Use | Response Body |
|------|------|-------------|---------------|
| 200 | OK | Successful GET, PUT, PATCH, or DELETE with body | Resource data |
| 201 | Created | Successful POST creating a resource | Created resource |
| 202 | Accepted | Request accepted for async processing | Status/tracking info |
| 204 | No Content | Successful DELETE or update with no body | None |

### 3xx Redirection
| Code | Name | When to Use | Headers |
|------|------|-------------|---------|
| 301 | Moved Permanently | Resource permanently moved | Location |
| 302 | Found | Temporary redirect | Location |
| 304 | Not Modified | Resource not changed (caching) | ETag |

### 4xx Client Errors
| Code | Name | When to Use | Example |
|------|------|-------------|---------|
| 400 | Bad Request | Malformed request, validation errors | Invalid JSON syntax |
| 401 | Unauthorized | Missing or invalid authentication | No API key provided |
| 403 | Forbidden | Authenticated but not authorized | User role insufficient |
| 404 | Not Found | Resource doesn't exist | User ID not found |
| 405 | Method Not Allowed | HTTP method not supported | POST on read-only resource |
| 406 | Not Acceptable | Requested format unavailable | Accept: application/xml (if XML not supported) |
| 409 | Conflict | Resource conflict | Duplicate email address |
| 410 | Gone | Resource permanently deleted | Account closed |
| 422 | Unprocessable Entity | Valid syntax but semantic errors | Age must be positive |
| 429 | Too Many Requests | Rate limit exceeded | 100 requests/min exceeded |

### 5xx Server Errors
| Code | Name | When to Use | Example |
|------|------|-------------|---------|
| 500 | Internal Server Error | Unexpected server error | Unhandled exception |
| 501 | Not Implemented | Feature not implemented | Future API version |
| 502 | Bad Gateway | Upstream server error | Database connection failed |
| 503 | Service Unavailable | Temporary downtime | Maintenance mode |
| 504 | Gateway Timeout | Upstream timeout | Database query timeout |

### Status Code Decision Tree

```
Is the request successful?
├─ Yes
│  ├─ Created a new resource? → 201 Created
│  ├─ Async processing? → 202 Accepted
│  ├─ No content to return? → 204 No Content
│  └─ Default → 200 OK
│
└─ No
   ├─ Client error?
   │  ├─ Missing/invalid auth? → 401 Unauthorized
   │  ├─ Auth valid but forbidden? → 403 Forbidden
   │  ├─ Resource not found? → 404 Not Found
   │  ├─ Validation error? → 400 Bad Request or 422 Unprocessable Entity
   │  ├─ Conflict (duplicate)? → 409 Conflict
   │  └─ Rate limited? → 429 Too Many Requests
   │
   └─ Server error?
      ├─ Upstream failure? → 502 Bad Gateway or 504 Gateway Timeout
      ├─ Temporary unavailable? → 503 Service Unavailable
      └─ Unexpected error? → 500 Internal Server Error
```

## Error Response Format

### Standard Structure

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed for one or more fields",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "value": "not-an-email"
      },
      {
        "field": "age",
        "message": "Must be a positive integer",
        "value": -5
      }
    ],
    "timestamp": "2026-02-20T10:00:00Z",
    "traceId": "abc-123-def-456",
    "path": "/users",
    "requestId": "req-789"
  }
}
```

### Error Code Taxonomy

```
Format: CATEGORY_SPECIFIC_ERROR

Categories:
- VALIDATION_*: Input validation errors
- AUTH_*: Authentication errors
- AUTHZ_*: Authorization errors
- RESOURCE_*: Resource-related errors
- RATE_LIMIT_*: Rate limiting errors
- EXTERNAL_*: External service errors
```

### Examples by Status Code

#### 400 Bad Request
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Request body must be valid JSON",
    "timestamp": "2026-02-20T10:00:00Z",
    "traceId": "abc-123"
  }
}
```

#### 401 Unauthorized
```json
{
  "error": {
    "code": "AUTH_TOKEN_MISSING",
    "message": "Authentication token is required",
    "details": [
      {
        "header": "Authorization",
        "message": "Missing 'Authorization' header"
      }
    ],
    "timestamp": "2026-02-20T10:00:00Z",
    "traceId": "abc-123"
  }
}
```

#### 403 Forbidden
```json
{
  "error": {
    "code": "AUTHZ_INSUFFICIENT_PERMISSIONS",
    "message": "You do not have permission to perform this action",
    "details": [
      {
        "required": "admin",
        "actual": "user"
      }
    ],
    "timestamp": "2026-02-20T10:00:00Z",
    "traceId": "abc-123"
  }
}
```

#### 404 Not Found
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "User not found",
    "details": [
      {
        "resource": "user",
        "id": "123"
      }
    ],
    "timestamp": "2026-02-20T10:00:00Z",
    "traceId": "abc-123"
  }
}
```

#### 409 Conflict
```json
{
  "error": {
    "code": "RESOURCE_CONFLICT",
    "message": "A user with this email already exists",
    "details": [
      {
        "field": "email",
        "value": "alice@example.com",
        "conflictingResourceId": "456"
      }
    ],
    "timestamp": "2026-02-20T10:00:00Z",
    "traceId": "abc-123"
  }
}
```

#### 422 Unprocessable Entity
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "value": "not-an-email"
      }
    ],
    "timestamp": "2026-02-20T10:00:00Z",
    "traceId": "abc-123"
  }
}
```

#### 429 Too Many Requests
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "details": [
      {
        "limit": 100,
        "window": "1 minute",
        "retryAfter": 45
      }
    ],
    "timestamp": "2026-02-20T10:00:00Z",
    "traceId": "abc-123"
  }
}
```

#### 500 Internal Server Error
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred. Please contact support.",
    "timestamp": "2026-02-20T10:00:00Z",
    "traceId": "abc-123"
  }
}
```

## Pagination Patterns

### Offset-Based Pagination

**Pros**: Simple, supports random page access, familiar to users
**Cons**: Slow for large offsets, inconsistent when data changes, poor performance at scale

```http
GET /users?page=2&limit=20

Response:
{
  "data": [...],
  "meta": {
    "page": 2,
    "limit": 20,
    "total": 1000,
    "totalPages": 50
  },
  "links": {
    "first": "/users?page=1&limit=20",
    "prev": "/users?page=1&limit=20",
    "self": "/users?page=2&limit=20",
    "next": "/users?page=3&limit=20",
    "last": "/users?page=50&limit=20"
  }
}
```

**Implementation**:
```sql
SELECT * FROM users
ORDER BY created_at DESC
LIMIT 20 OFFSET 20;  -- page 2, limit 20
```

**Best for**: Admin UIs, small datasets, reports with page numbers

### Cursor-Based Pagination

**Pros**: Consistent results, performant, handles real-time updates well
**Cons**: No random access, harder to implement

```http
GET /users?limit=20&cursor=eyJpZCI6MTIzfQ==

Response:
{
  "data": [...],
  "meta": {
    "limit": 20,
    "hasMore": true
  },
  "pagination": {
    "next": "/users?limit=20&cursor=eyJpZCI6MTQzfQ==",
    "prev": "/users?limit=20&cursor=eyJpZCI6MTAzfQ=="
  }
}
```

**Cursor Format** (Base64 encoded JSON):
```json
// Decoded: {"id": 123, "createdAt": "2026-02-20T10:00:00Z"}
// Encoded: eyJpZCI6MTIzLCJjcmVhdGVkQXQiOiIyMDI2LTAyLTIwVDEwOjAwOjAwWiJ9
```

**Implementation**:
```sql
-- First page
SELECT * FROM users
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Next page (cursor contains last item's created_at and id)
SELECT * FROM users
WHERE (created_at, id) < ('2026-02-20T10:00:00Z', 123)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

**Best for**: Infinite scroll, mobile apps, large datasets, real-time feeds

### Keyset-Based Pagination

**Pros**: Extremely performant, stable, works with indexes
**Cons**: Limited sorting options, requires unique sequential key

```http
GET /users?limit=20&since_id=123

Response:
{
  "data": [...],
  "meta": {
    "limit": 20,
    "sinceId": 123,
    "maxId": 143
  },
  "links": {
    "next": "/users?limit=20&since_id=143"
  }
}
```

**Implementation**:
```sql
-- First page
SELECT * FROM users
ORDER BY id DESC
LIMIT 20;

-- Next page
SELECT * FROM users
WHERE id < 123
ORDER BY id DESC
LIMIT 20;
```

**Best for**: High-volume APIs, time-series data, event logs

### Comparison Table

| Feature | Offset | Cursor | Keyset |
|---------|--------|--------|--------|
| Performance (small dataset) | Good | Good | Good |
| Performance (large dataset) | Poor | Good | Excellent |
| Random page access | Yes | No | No |
| Consistent results | No | Yes | Yes |
| Implementation complexity | Low | Medium | Low |
| Handles data changes | Poor | Good | Excellent |
| Sorting flexibility | High | Medium | Low |
| Database support | Universal | Universal | Requires indexed columns |

## Filtering, Sorting, Field Selection

### Filtering

```http
# Single filter
GET /users?status=active

# Multiple filters (AND)
GET /users?status=active&role=admin

# Range filters
GET /products?price_min=10&price_max=100

# Date range
GET /orders?created_after=2026-01-01&created_before=2026-02-01

# In operator
GET /users?id=1,2,3,4,5

# Pattern matching (search)
GET /users?q=john
GET /products?name_contains=phone
```

### Sorting

```http
# Single field ascending
GET /users?sort=name

# Single field descending (minus prefix)
GET /users?sort=-created_at

# Multiple fields
GET /users?sort=-created_at,name

# Alternative: explicit direction
GET /users?sort=created_at:desc,name:asc
```

### Field Selection (Sparse Fieldsets)

```http
# Select specific fields
GET /users?fields=id,name,email

# Nested resources
GET /users?fields=id,name&fields[posts]=title,created_at

# Response:
{
  "data": [
    { "id": 1, "name": "Alice", "email": "alice@example.com" }
  ]
}
```

### Search

```http
# Full-text search
GET /products?q=wireless+headphones

# Field-specific search
GET /users?search[name]=john&search[email]=@example.com
```

### Combined Example

```http
GET /products?category=electronics&price_min=50&price_max=500&q=wireless&sort=-rating,price&fields=id,name,price,rating&limit=20&page=1
```

## Versioning Strategies

| Strategy | Format | Pros | Cons | Best For |
|----------|--------|------|------|----------|
| URL Path | `/v1/users` | Clear, easy routing, cache-friendly | URL pollution, rigid | Public APIs |
| Header | `Accept: application/vnd.api+json;version=1` | Clean URLs, flexible | Hidden, complex client code | Internal APIs |
| Query Param | `?version=1` | Simple, optional default | Caching issues | Gradual migration |
| Content Negotiation | `Accept: application/vnd.api.v1+json` | RESTful, standards-based | Complex | Enterprise APIs |

### URL Path Versioning

```http
GET /v1/users
GET /v2/users

# Pros:
- Explicit and visible
- Easy to route in API gateway
- Cache-friendly

# Cons:
- Duplicates endpoints
- URL structure changes
```

### Header Versioning

```http
GET /users
Accept: application/vnd.myapi.v1+json

GET /users
Accept: application/vnd.myapi.v2+json

# Pros:
- Clean URLs
- Same endpoint, different versions
- Follows REST principles

# Cons:
- Harder to test in browser
- Requires client to set headers
```

### Query Parameter Versioning

```http
GET /users?version=1
GET /users?version=2

# Pros:
- Simple to implement
- Easy to test
- Optional (can default to latest)

# Cons:
- Query params typically for filtering
- Caching complexity
```

### Best Practices

1. **Version from Day One**: Even if v1 is your only version
2. **Support Multiple Versions**: Don't immediately deprecate old versions
3. **Document Deprecation Timeline**: Give clients time to migrate
4. **Use Semantic Versioning**: Major.Minor.Patch
5. **Breaking Changes = New Major Version**:
   - Removing fields
   - Changing field types
   - Changing authentication
6. **Non-Breaking Changes = Same Version**:
   - Adding optional fields
   - Adding new endpoints
   - Deprecating (but not removing) fields

## Rate Limiting

### Response Headers

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1645358400
X-RateLimit-Window: 60
```

### 429 Response

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 45
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1645358400

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 45 seconds.",
    "details": {
      "limit": 100,
      "window": "1 minute",
      "retryAfter": 45
    }
  }
}
```

### Rate Limiting Strategies

| Strategy | How It Works | Pros | Cons |
|----------|--------------|------|------|
| Fixed Window | 100 req per minute starting at :00 | Simple | Burst at window edge |
| Sliding Window | 100 req in any 60-second period | Smooth | Complex implementation |
| Token Bucket | Refill tokens at fixed rate | Handles bursts | Harder to understand |
| Leaky Bucket | Process requests at fixed rate | Smooth traffic | Can delay valid requests |

### Implementation Examples

#### Fixed Window
```
Window: 10:00:00 - 10:01:00
Limit: 100 requests
Current: 95 requests
Remaining: 5 requests
Reset: 10:01:00
```

#### Sliding Window
```
Time: 10:00:45
Limit: 100 requests per 60 seconds
Window: 09:59:45 - 10:00:45
Count: 95 requests in window
Remaining: 5 requests
```

## Authentication & Authorization

### Authentication Methods

| Method | Use Case | Pros | Cons |
|--------|----------|------|------|
| API Keys | Service-to-service | Simple | No user context |
| OAuth 2.0 | User authorization | Standard, delegated auth | Complex |
| JWT | Stateless auth | No server-side session | Token size, revocation |
| Session | Traditional web apps | Familiar, revocable | Requires server state |

### Authorization Header Formats

```http
# API Key
Authorization: ApiKey YOUR_API_KEY

# Bearer Token (JWT, OAuth)
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Basic Auth
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```

### JWT Structure

```json
// Header
{
  "alg": "HS256",
  "typ": "JWT"
}

// Payload
{
  "sub": "user123",
  "name": "Alice",
  "role": "admin",
  "iat": 1645358400,
  "exp": 1645444800
}

// Signature
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

## HATEOAS (Optional)

Hypermedia As The Engine Of Application State - clients navigate API through links provided by server.

```json
{
  "id": 1,
  "name": "Alice",
  "email": "alice@example.com",
  "_links": {
    "self": {
      "href": "/users/1"
    },
    "orders": {
      "href": "/users/1/orders"
    },
    "edit": {
      "href": "/users/1",
      "method": "PUT"
    },
    "delete": {
      "href": "/users/1",
      "method": "DELETE"
    }
  }
}
```

**Pros**: Self-documenting, clients adaptable to changes
**Cons**: Verbose responses, not widely adopted

## API Design Checklist

### Planning
- [ ] API purpose and scope clearly defined
- [ ] Target audience identified (public, internal, partners)
- [ ] Authentication method chosen
- [ ] Versioning strategy selected
- [ ] Rate limiting requirements determined

### Design
- [ ] Resources are nouns (not verbs)
- [ ] Consistent plural naming for collections
- [ ] HTTP methods used correctly (GET, POST, PUT, PATCH, DELETE)
- [ ] Status codes follow standard semantics
- [ ] Pagination strategy chosen for list endpoints
- [ ] Filtering and sorting parameters defined
- [ ] Error response format standardized

### Security
- [ ] Authentication required on all protected endpoints
- [ ] Authorization checks implemented
- [ ] Input validation on all user input
- [ ] Rate limiting configured
- [ ] HTTPS enforced
- [ ] CORS properly configured
- [ ] Sensitive data not logged

### Performance
- [ ] Pagination implemented for lists
- [ ] Caching headers configured (ETag, Cache-Control)
- [ ] Database queries optimized (N+1 prevention)
- [ ] Response compression enabled
- [ ] Connection pooling configured

### Documentation
- [ ] OpenAPI/Swagger specification created
- [ ] All endpoints documented
- [ ] Request/response examples provided
- [ ] Authentication flow documented
- [ ] Error codes documented
- [ ] Changelog maintained

### Testing
- [ ] Unit tests for business logic
- [ ] Integration tests for endpoints
- [ ] Authentication/authorization tests
- [ ] Error handling tests
- [ ] Load testing performed
- [ ] Security testing (OWASP Top 10)

### Monitoring
- [ ] Logging configured
- [ ] Metrics collected (request count, latency, errors)
- [ ] Alerting set up for errors and performance
- [ ] Health check endpoint implemented
- [ ] API analytics dashboard created

### Deployment
- [ ] Versioning enforced in production
- [ ] Rollback plan documented
- [ ] Deprecation policy defined
- [ ] API changelog published
- [ ] Client migration guide provided
