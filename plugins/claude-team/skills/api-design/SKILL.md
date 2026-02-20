---
name: api-design
description: "API 설계 레퍼런스. REST 패턴, 상태코드, 페이지네이션, GraphQL 스키마 설계, N+1 방지 전략을 제공합니다."
version: 1.0.0
---

# API Design Reference

API 설계를 위한 전문 레퍼런스 스킬입니다. REST API 패턴부터 GraphQL 스키마 설계, 그리고 성능 최적화까지 포괄적인 가이드를 제공합니다.

## Overview

현대적인 API 설계는 단순히 엔드포인트를 노출하는 것을 넘어서, 확장 가능하고 유지보수 가능하며 성능이 우수한 인터페이스를 만드는 것입니다. 이 스킬은 다음을 제공합니다:

- **REST API 설계 패턴**: 리소스 네이밍, HTTP 메서드, 상태 코드, 페이지네이션 전략
- **GraphQL 스키마 설계**: 타입 시스템, 쿼리 최적화, N+1 문제 해결
- **API 아키텍처 결정**: REST vs GraphQL vs gRPC 선택 가이드
- **보안 및 성능**: 인증/인가, 속도 제한, 캐싱 전략

## API Architecture Comparison

| Aspect | REST | GraphQL | gRPC |
|--------|------|---------|------|
| **Protocol** | HTTP/1.1 | HTTP/1.1, HTTP/2 | HTTP/2 |
| **Data Format** | JSON, XML | JSON | Protocol Buffers |
| **Schema** | OpenAPI (optional) | Strongly typed (required) | Protocol Buffers (required) |
| **Versioning** | URL/Header versioning | Schema evolution | Protocol evolution |
| **Caching** | HTTP caching (native) | Custom/complex | Limited |
| **Real-time** | Polling, SSE, WebSocket | Subscriptions | Bidirectional streaming |
| **Learning Curve** | Low | Medium | Medium-High |
| **Tooling** | Mature | Growing | Growing |
| **Browser Support** | Native | Native | Requires gRPC-Web |
| **Performance** | Good | Very Good | Excellent |
| **Bandwidth** | Medium | Low (precise queries) | Very Low (binary) |

## When to Use Each

### REST
**Best for:**
- Public APIs with broad client compatibility
- Simple CRUD operations
- Resource-oriented domains
- APIs requiring HTTP caching
- Teams familiar with HTTP standards

**Avoid when:**
- Clients need flexible data fetching
- Over-fetching/under-fetching is a problem
- Real-time updates are critical
- Extremely high performance required

### GraphQL
**Best for:**
- Multiple clients with different data needs (mobile, web, etc.)
- Complex, interconnected data models
- Rapid frontend iteration without backend changes
- Applications requiring real-time subscriptions
- Reducing over-fetching and network requests

**Avoid when:**
- Simple CRUD APIs
- File upload/download is primary use case
- Team lacks GraphQL expertise
- Caching complexity is unacceptable

### gRPC
**Best for:**
- Microservice communication
- High-performance, low-latency requirements
- Polyglot environments (multiple languages)
- Streaming data (bidirectional)
- Internal APIs with controlled clients

**Avoid when:**
- Browser clients (without gRPC-Web)
- Public APIs requiring wide compatibility
- Human-readable APIs needed
- Team lacks Protocol Buffers expertise

## Key Concepts

### REST API Design
REST APIs organize around resources (nouns) and use HTTP methods to perform operations. Key principles:

1. **Resource-Oriented**: URLs represent resources, not actions
2. **Stateless**: Each request contains all information needed
3. **Uniform Interface**: Standard HTTP methods and status codes
4. **Layered System**: Client unaware of intermediate layers

### GraphQL Schema Design
GraphQL provides a type system for your API:

1. **Schema-First**: Define types before implementation
2. **Client-Driven**: Clients request exactly what they need
3. **Single Endpoint**: All queries go through one URL
4. **Strongly Typed**: Type safety from schema to resolvers

### Common API Patterns

#### Pagination
- **Offset-based**: Simple but can be inconsistent with data changes
- **Cursor-based**: Stable pagination, ideal for infinite scroll
- **Keyset-based**: High performance for sorted data

#### Authentication
- **API Keys**: Simple, for service-to-service
- **OAuth 2.0**: Standard for user authorization
- **JWT**: Stateless, portable tokens
- **Session-based**: Traditional, requires server-side state

#### Error Handling
- **Consistent Format**: Standardized error response structure
- **Actionable Messages**: Clear guidance for clients
- **Error Codes**: Machine-readable error identifiers
- **Validation Details**: Field-level error information

#### Versioning
- **URL Versioning**: `/v1/users` - explicit, easy routing
- **Header Versioning**: `Accept: application/vnd.api.v1+json` - clean URLs
- **Query Parameter**: `?version=1` - simple but caching issues

## References

This skill provides detailed references in two main areas:

### 1. REST Patterns (`references/rest-patterns.md`)
Comprehensive guide to REST API design including:
- Resource naming conventions
- HTTP methods and status codes
- Pagination strategies (offset, cursor, keyset)
- Filtering, sorting, and field selection
- Error response formats
- Rate limiting
- API versioning
- Security best practices
- Design checklist

### 2. GraphQL Patterns (`references/graphql-patterns.md`)
In-depth GraphQL schema design and optimization:
- Schema design principles
- Type system patterns (Connection, Edge, Node)
- Query and mutation design
- N+1 problem prevention (DataLoader, etc.)
- Performance optimization
- Query complexity analysis
- Security (depth limiting, field authorization)
- Anti-patterns to avoid

## Usage Examples

### Designing a REST API
```markdown
User: I need to design a REST API for a blog platform with posts, comments, and users.

Response:
1. Resource naming:
   - `/users` - User collection
   - `/users/{id}` - Single user
   - `/posts` - Post collection
   - `/posts/{id}` - Single post
   - `/posts/{id}/comments` - Comments for a post

2. Key endpoints:
   GET    /posts?page=1&limit=20&sort=-created_at
   POST   /posts
   GET    /posts/{id}
   PUT    /posts/{id}
   DELETE /posts/{id}
   GET    /posts/{id}/comments
   POST   /posts/{id}/comments

3. Pagination: Use cursor-based for main feeds
4. Authentication: JWT tokens
5. Rate limiting: 100 req/min per user
```

### Optimizing GraphQL Queries
```markdown
User: Our GraphQL API has N+1 problems when fetching users and their posts.

Response:
Implement DataLoader pattern:

1. Create loaders:
   - userLoader: Batches user queries
   - postsLoader: Batches posts-by-user queries

2. Use in resolvers:
   Query.users -> db query
   User.posts -> postsLoader.load(user.id)

3. Configure per-request context:
   context: () => ({
     loaders: { userLoader, postsLoader }
   })

4. Measure improvement: 100+ queries -> 2-3 queries
```

## Related Agents

This skill is particularly valuable for the following specialized agents:

- **api-designer**: API 설계 전문가, REST/GraphQL/gRPC 아키텍처 설계
- **backend**: 백엔드 개발 전문가, 서버 로직 및 API 구현
- **fastapi-expert**: FastAPI 프레임워크 전문가, Python 비동기 API 개발
- **nestjs-expert**: NestJS 프레임워크 전문가, TypeScript 기반 서버 개발
- **spring-expert**: Spring Boot 전문가, Java/Kotlin 엔터프라이즈 개발
- **security-architect**: 보안 아키텍처 전문가, 안전한 API 설계

## Best Practices Summary

### Design Principles
1. **Consistency**: Use consistent naming, response formats, and patterns
2. **Simplicity**: Keep APIs intuitive and easy to understand
3. **Documentation**: Maintain up-to-date API documentation (OpenAPI, GraphQL schema)
4. **Versioning**: Plan for evolution from day one
5. **Security**: Authentication, authorization, and validation on all endpoints
6. **Performance**: Pagination, caching, and query optimization
7. **Error Handling**: Clear, actionable error messages
8. **Testing**: Comprehensive API testing coverage

### Common Pitfalls
- **Exposing Implementation Details**: Design for clients, not database structure
- **Inconsistent Naming**: Mix of camelCase, snake_case, PascalCase
- **Missing Pagination**: Large list responses without pagination
- **Poor Error Messages**: Generic "Error occurred" messages
- **No Rate Limiting**: Vulnerable to abuse
- **Ignoring HTTP Semantics**: Using POST for read operations
- **Breaking Changes**: Modifying existing fields without versioning

## Additional Resources

### Tools
- **REST**: Postman, Insomnia, Swagger/OpenAPI
- **GraphQL**: GraphiQL, Apollo Studio, GraphQL Playground
- **gRPC**: Postman, BloomRPC, grpcurl
- **Documentation**: Stoplight, Redoc, GraphQL Voyager
- **Testing**: REST Assured, Pact, Apollo Client Testing

### Standards
- **REST**: RFC 7231 (HTTP Semantics), JSON API specification
- **GraphQL**: GraphQL Specification, Apollo Federation
- **gRPC**: Protocol Buffers Language Guide
- **Authentication**: OAuth 2.0 (RFC 6749), OpenID Connect
- **Security**: OWASP API Security Top 10

## Conclusion

Effective API design balances multiple concerns: client needs, performance, security, and maintainability. Use this skill as a reference to make informed decisions, avoid common pitfalls, and create APIs that stand the test of time.

Remember: The best API is one that is intuitive for clients, performant under load, secure by default, and evolvable without breaking changes.
