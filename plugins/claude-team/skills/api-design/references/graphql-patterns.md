# GraphQL Schema Design and Optimization Patterns

Comprehensive guide to designing efficient, scalable, and maintainable GraphQL APIs.

## Table of Contents
- [Schema Design Principles](#schema-design-principles)
- [Type Design Patterns](#type-design-patterns)
- [Query Design](#query-design)
- [Mutation Patterns](#mutation-patterns)
- [N+1 Problem Prevention](#n1-problem-prevention)
- [Performance Optimization](#performance-optimization)
- [Security](#security)
- [Anti-Patterns](#anti-patterns)
- [Best Practices](#best-practices)

## Schema Design Principles

### 1. Design for Client Needs, Not Database Structure

```graphql
# Bad: Exposing database structure
type User {
  id: ID!
  user_name: String!  # Snake case from DB
  email_addr: String!
  created_ts: String!
  user_role_id: Int!
}

# Good: Clean, client-friendly interface
type User {
  id: ID!
  name: String!
  email: String!
  createdAt: DateTime!
  role: Role!  # Resolved relationship, not foreign key
}
```

### 2. Use Descriptive, Specific Types

```graphql
# Bad: Generic types
type User {
  id: ID!
  name: String!
  metadata: JSON  # Avoid opaque types
}

# Good: Explicit types
type User {
  id: ID!
  name: String!
  profile: UserProfile!
  settings: UserSettings!
}

type UserProfile {
  bio: String
  avatar: URL
  location: String
}

type UserSettings {
  theme: Theme!
  emailNotifications: Boolean!
  language: Language!
}
```

### 3. Prefer Input Types for Mutations

```graphql
# Bad: Inline arguments
type Mutation {
  createUser(
    name: String!
    email: String!
    role: String!
    bio: String
    avatar: String
  ): User!
}

# Good: Input type
input CreateUserInput {
  name: String!
  email: String!
  role: Role!
  profile: UserProfileInput
}

input UserProfileInput {
  bio: String
  avatar: URL
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
}
```

### 4. Use Enums for Fixed Sets

```graphql
# Bad: String with no validation
type User {
  role: String!  # Could be anything
  status: String!
}

# Good: Explicit enums
enum Role {
  ADMIN
  USER
  GUEST
}

enum UserStatus {
  ACTIVE
  INACTIVE
  SUSPENDED
  DELETED
}

type User {
  role: Role!
  status: UserStatus!
}
```

## Type Design Patterns

### Connection Pattern (Relay-Style Pagination)

```graphql
# Core pagination types
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

# Generic connection pattern
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  node: User!
  cursor: String!
}

# Query using connection
type Query {
  users(
    first: Int
    after: String
    last: Int
    before: String
    filter: UserFilter
  ): UserConnection!
}

# Example query
query {
  users(first: 10, after: "cursor123") {
    edges {
      node {
        id
        name
        email
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
    totalCount
  }
}
```

### Node Interface (Global Object Identification)

```graphql
interface Node {
  id: ID!
}

type User implements Node {
  id: ID!
  name: String!
  email: String!
}

type Post implements Node {
  id: ID!
  title: String!
  content: String!
  author: User!
}

type Query {
  node(id: ID!): Node
  nodes(ids: [ID!]!): [Node]!
}

# Example: Fetch any object by ID
query {
  node(id: "VXNlcjox") {
    id
    ... on User {
      name
      email
    }
    ... on Post {
      title
      author { name }
    }
  }
}
```

### Union Types for Heterogeneous Results

```graphql
type User {
  id: ID!
  name: String!
}

type Post {
  id: ID!
  title: String!
}

type Comment {
  id: ID!
  text: String!
}

union SearchResult = User | Post | Comment

type Query {
  search(query: String!): [SearchResult!]!
}

# Example query
query {
  search(query: "graphql") {
    __typename
    ... on User {
      id
      name
    }
    ... on Post {
      id
      title
    }
    ... on Comment {
      id
      text
    }
  }
}
```

### Error Union Pattern

```graphql
type User {
  id: ID!
  name: String!
  email: String!
}

type ValidationError {
  field: String!
  message: String!
}

type NotFoundError {
  message: String!
  resourceType: String!
  resourceId: ID!
}

union UserResult = User | ValidationError | NotFoundError

type Query {
  user(id: ID!): UserResult!
}

# Example query
query {
  user(id: "123") {
    __typename
    ... on User {
      id
      name
      email
    }
    ... on NotFoundError {
      message
      resourceType
    }
  }
}
```

## Query Design

### Nullable vs Non-Nullable Fields

```graphql
type User {
  # Non-nullable: Field always exists
  id: ID!
  createdAt: DateTime!

  # Nullable: Field might not exist
  email: String  # User might not have email
  deletedAt: DateTime  # Only exists for deleted users

  # Non-null list with nullable items: List always exists, items might be null
  posts: [Post]!

  # Non-null list with non-null items: List and items always exist
  roles: [Role!]!
}
```

**Guidelines**:
- Use `!` for fields that always exist
- Leave nullable for optional fields or fields that might fail to resolve
- Consider client impact: non-null failures bubble up

### Field-Level Authorization

```graphql
type User {
  id: ID!
  name: String!
  email: String!  # Only accessible to user or admin
  privateNotes: String  # Only accessible to user
}

# Resolver implementation
const resolvers = {
  User: {
    email: (user, args, context) => {
      if (context.userId === user.id || context.role === 'ADMIN') {
        return user.email;
      }
      throw new Error('Unauthorized');
    },
    privateNotes: (user, args, context) => {
      if (context.userId !== user.id) {
        return null;  // Or throw error
      }
      return user.privateNotes;
    }
  }
};
```

### Query Complexity Analysis

```graphql
# Each field has a complexity score
type Query {
  users: [User!]!  # Complexity: 10
  user(id: ID!): User  # Complexity: 1
}

type User {
  id: ID!  # Complexity: 0
  name: String!  # Complexity: 0
  posts: [Post!]!  # Complexity: 5
}

# Query complexity calculation
query {
  users {  # 10
    id  # 0
    name  # 0
    posts {  # 10 * 5 = 50 (multiplied by parent)
      title  # 0
    }
  }
}
# Total: 60

# Limit queries above threshold (e.g., 1000)
```

### Depth Limiting

```graphql
# Without depth limiting, clients can create expensive queries
query {
  user {
    posts {
      author {
        posts {
          author {
            posts {
              # ... infinite nesting
            }
          }
        }
      }
    }
  }
}

# Implement max depth (e.g., 5 levels)
```

## Mutation Patterns

### Input/Payload Pattern

```graphql
# Input type for mutation arguments
input CreateUserInput {
  name: String!
  email: String!
  role: Role!
}

# Payload type for mutation response
type CreateUserPayload {
  user: User
  errors: [UserError!]!
  success: Boolean!
}

type UserError {
  field: String!
  message: String!
  code: String!
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
}
```

**Example usage**:
```graphql
mutation {
  createUser(input: {
    name: "Alice"
    email: "alice@example.com"
    role: ADMIN
  }) {
    user {
      id
      name
      email
    }
    errors {
      field
      message
    }
    success
  }
}
```

**Response (success)**:
```json
{
  "data": {
    "createUser": {
      "user": {
        "id": "1",
        "name": "Alice",
        "email": "alice@example.com"
      },
      "errors": [],
      "success": true
    }
  }
}
```

**Response (error)**:
```json
{
  "data": {
    "createUser": {
      "user": null,
      "errors": [
        {
          "field": "email",
          "message": "Email already exists",
          "code": "DUPLICATE_EMAIL"
        }
      ],
      "success": false
    }
  }
}
```

### Optimistic Response Pattern

```graphql
type Mutation {
  likePost(postId: ID!): LikePostPayload!
}

type LikePostPayload {
  post: Post!
  liked: Boolean!
}

# Client can optimistically update UI before server responds
```

### Idempotent Mutations

```graphql
type Mutation {
  # Idempotent: calling multiple times has same effect
  createUser(input: CreateUserInput!, idempotencyKey: String!): CreateUserPayload!
}

# Server stores idempotency key
# If same key sent again, returns cached response
```

## N+1 Problem Prevention

### The N+1 Problem

```graphql
query {
  posts {  # 1 query to get all posts
    title
    author {  # N queries (one per post) to get each author
      name
    }
  }
}

# Without optimization:
# SELECT * FROM posts;  -- 1 query
# SELECT * FROM users WHERE id = 1;  -- Query per post
# SELECT * FROM users WHERE id = 2;
# SELECT * FROM users WHERE id = 3;
# ... (N queries for N posts)
```

### Solution 1: DataLoader

```typescript
import DataLoader from 'dataloader';

// Create loader
const userLoader = new DataLoader(async (userIds: string[]) => {
  // Batch load all users in one query
  const users = await db.user.findMany({
    where: { id: { in: userIds } }
  });

  // Return users in same order as requested IDs
  return userIds.map(id => users.find(u => u.id === id));
});

// Use in resolver
const resolvers = {
  Post: {
    author: (post, args, context) => {
      return context.loaders.userLoader.load(post.authorId);
    }
  }
};

// Context setup (per-request)
const context = () => ({
  loaders: {
    userLoader: new DataLoader(batchLoadUsers)
  }
});

// Result: 2 queries total (1 for posts, 1 batched for all authors)
```

### Solution 2: Join Monster (SQL)

```typescript
import joinMonster from 'join-monster';

const User = new GraphQLObjectType({
  name: 'User',
  sqlTable: 'users',
  uniqueKey: 'id',
  fields: {
    id: { type: GraphQLInt },
    name: { type: GraphQLString }
  }
});

const Post = new GraphQLObjectType({
  name: 'Post',
  sqlTable: 'posts',
  uniqueKey: 'id',
  fields: {
    id: { type: GraphQLInt },
    title: { type: GraphQLString },
    author: {
      type: User,
      sqlJoin: (posts, users) => `${posts}.author_id = ${users}.id`
    }
  }
});

// Generates single SQL query with JOIN
// SELECT posts.*, users.* FROM posts LEFT JOIN users ON posts.author_id = users.id
```

### Solution 3: Prisma (ORM with Built-in Optimization)

```typescript
const resolvers = {
  Query: {
    posts: () => {
      return prisma.post.findMany({
        include: {
          author: true  // Prisma automatically optimizes this
        }
      });
    }
  }
};

// Prisma generates optimized query
// Often uses JOINs or batching automatically
```

### Solution 4: Field-Level Caching

```typescript
const resolvers = {
  Post: {
    author: async (post, args, context) => {
      // Cache authors in request context
      if (!context.authorCache) {
        context.authorCache = new Map();
      }

      if (context.authorCache.has(post.authorId)) {
        return context.authorCache.get(post.authorId);
      }

      const author = await db.user.findUnique({
        where: { id: post.authorId }
      });

      context.authorCache.set(post.authorId, author);
      return author;
    }
  }
};

// Still N queries, but manual deduplication
// DataLoader is better - use this only if DataLoader not available
```

### DataLoader Advanced Patterns

```typescript
// Loader with error handling
const userLoader = new DataLoader(async (ids: string[]) => {
  const users = await db.user.findMany({ where: { id: { in: ids } } });
  return ids.map(id => {
    const user = users.find(u => u.id === id);
    return user || new Error(`User ${id} not found`);
  });
});

// Loader with custom cache key
const userByEmailLoader = new DataLoader(
  async (emails: string[]) => {
    const users = await db.user.findMany({ where: { email: { in: emails } } });
    return emails.map(email => users.find(u => u.email === email));
  },
  { cacheKeyFn: (email) => email.toLowerCase() }
);

// Prime loader cache (useful after mutations)
const user = await createUser(input);
context.loaders.userLoader.prime(user.id, user);

// Clear loader cache
context.loaders.userLoader.clear(userId);
context.loaders.userLoader.clearAll();
```

## Performance Optimization

### Query Complexity Scoring

```typescript
import { createComplexityLimitRule } from 'graphql-validation-complexity';

const schema = makeExecutableSchema({
  typeDefs,
  resolvers
});

const complexityLimit = createComplexityLimitRule(1000, {
  scalarCost: 0,
  objectCost: 1,
  listFactor: 10,
  introspectionListFactor: 2
});

// Use in GraphQL server
const server = new ApolloServer({
  schema,
  validationRules: [complexityLimit]
});
```

### Persisted Queries

```typescript
// Client sends query hash instead of full query
const queryId = 'abc123';  // SHA-256 of query

// Request
{
  "query": null,
  "queryId": "abc123",
  "variables": { "userId": "1" }
}

// Server configuration
const persistedQueries = {
  'abc123': 'query GetUser($userId: ID!) { user(id: $userId) { name } }'
};

// Benefits:
// - Smaller request size
// - Prevents arbitrary queries (security)
// - Better caching
```

### Automatic Persisted Queries (APQ)

```typescript
import { ApolloServer } from 'apollo-server';

const server = new ApolloServer({
  schema,
  persistedQueries: {
    cache: new Map()  // Or Redis for production
  }
});

// Client automatically:
// 1. Sends query hash on first request
// 2. Server responds with "PersistedQueryNotFound"
// 3. Client sends full query with hash
// 4. Server caches it
// 5. Subsequent requests only send hash
```

### Response Caching

```typescript
import responseCachePlugin from 'apollo-server-plugin-response-cache';

const server = new ApolloServer({
  schema,
  plugins: [
    responseCachePlugin({
      sessionId: (context) => context.userId,
      shouldReadFromCache: (context) => context.cacheControl !== 'no-cache',
      shouldWriteToCache: (context) => !context.error
    })
  ]
});

// In schema, add cache hints
type Query {
  user(id: ID!): User @cacheControl(maxAge: 60)
  posts: [Post!]! @cacheControl(maxAge: 30)
}
```

### Subscriptions vs Polling

| Feature | Subscriptions | Polling |
|---------|--------------|---------|
| Real-time updates | Immediate | Delayed |
| Server load | Lower (push) | Higher (repeated queries) |
| Network usage | Lower | Higher |
| Complexity | High | Low |
| Scalability | Requires WebSocket infrastructure | Easy |
| Best for | Live updates, chat, notifications | Periodic updates, dashboards |

**Subscription example**:
```graphql
type Subscription {
  postCreated: Post!
  commentAdded(postId: ID!): Comment!
}

subscription {
  commentAdded(postId: "123") {
    id
    text
    author { name }
  }
}
```

## Security

### Query Depth Limiting

```typescript
import depthLimit from 'graphql-depth-limit';

const server = new ApolloServer({
  schema,
  validationRules: [depthLimit(5)]
});

// Rejects queries deeper than 5 levels
```

### Field-Level Authorization

```typescript
import { shield, rule } from 'graphql-shield';

const isAuthenticated = rule()(async (parent, args, context) => {
  return context.userId !== null;
});

const isAdmin = rule()(async (parent, args, context) => {
  return context.role === 'ADMIN';
});

const isOwner = rule()(async (parent, args, context) => {
  return parent.userId === context.userId;
});

const permissions = shield({
  Query: {
    users: isAdmin,
    user: isAuthenticated
  },
  Mutation: {
    createUser: isAdmin,
    updateUser: isOwner
  },
  User: {
    email: isOwner
  }
});

const server = new ApolloServer({
  schema: applyMiddleware(schema, permissions)
});
```

### Rate Limiting by Complexity

```typescript
import { RateLimiter } from 'graphql-rate-limit';

const rateLimiter = new RateLimiter({
  identifyContext: (context) => context.userId,
  points: 1000,  // Complexity points
  duration: 60   // Per 60 seconds
});

const resolvers = {
  Query: {
    users: async (parent, args, context) => {
      await rateLimiter.consume(context, 10);  // Cost: 10 points
      return getUsers();
    }
  }
};
```

### Disable Introspection in Production

```typescript
import { NoSchemaIntrospectionCustomRule } from 'graphql';

const server = new ApolloServer({
  schema,
  validationRules: process.env.NODE_ENV === 'production'
    ? [NoSchemaIntrospectionCustomRule]
    : []
});

// Prevents attackers from exploring schema
```

### Input Validation

```typescript
import * as yup from 'yup';

const createUserSchema = yup.object({
  name: yup.string().required().min(2).max(50),
  email: yup.string().required().email(),
  age: yup.number().positive().integer().max(120)
});

const resolvers = {
  Mutation: {
    createUser: async (parent, { input }, context) => {
      try {
        await createUserSchema.validate(input);
      } catch (error) {
        throw new Error(`Validation failed: ${error.message}`);
      }

      return createUser(input);
    }
  }
};
```

## Anti-Patterns

### 1. Exposing Database Schema Directly

**Anti-pattern**:
```graphql
type user_table {
  user_id: Int!
  user_name: String!
  email_addr: String!
  created_ts: String!
  updated_ts: String!
  is_deleted: Int!
}
```

**Solution**:
```graphql
type User {
  id: ID!
  name: String!
  email: String!
  createdAt: DateTime!
  updatedAt: DateTime!
}
```

### 2. God Query (Single Query for Everything)

**Anti-pattern**:
```graphql
type Query {
  everything: Everything!
}

type Everything {
  users: [User!]!
  posts: [Post!]!
  comments: [Comment!]!
  settings: Settings!
  analytics: Analytics!
}
```

**Solution**:
```graphql
type Query {
  users(filter: UserFilter): UserConnection!
  posts(filter: PostFilter): PostConnection!
  comments(filter: CommentFilter): CommentConnection!
  settings: Settings!
  analytics(timeRange: TimeRange!): Analytics!
}
```

### 3. Over-Nesting

**Anti-pattern**:
```graphql
type Query {
  company: Company
}

type Company {
  departments: [Department!]!
}

type Department {
  teams: [Team!]!
}

type Team {
  members: [User!]!
}

# Forces deep resolver chains
```

**Solution**:
```graphql
type Query {
  company(id: ID!): Company
  department(id: ID!): Department
  team(id: ID!): Team
  user(id: ID!): User
}

# Allow direct access to resources
```

### 4. No Error Typing (Generic Errors)

**Anti-pattern**:
```graphql
type Mutation {
  createUser(input: CreateUserInput!): User
}

# Errors thrown as exceptions, not typed
```

**Solution**:
```graphql
type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
}

type CreateUserPayload {
  user: User
  errors: [UserError!]!
}

interface Error {
  message: String!
  code: String!
}

type UserError implements Error {
  message: String!
  code: String!
  field: String!
}
```

### 5. Nullable Everything

**Anti-pattern**:
```graphql
type User {
  id: ID
  name: String
  email: String
  createdAt: DateTime
}

# Client must check every field for null
```

**Solution**:
```graphql
type User {
  id: ID!
  name: String!
  email: String  # Truly optional
  createdAt: DateTime!
}

# Use ! for fields that always exist
```

### 6. List Without Pagination

**Anti-pattern**:
```graphql
type Query {
  users: [User!]!  # Could return 1 million users
}
```

**Solution**:
```graphql
type Query {
  users(
    first: Int
    after: String
    filter: UserFilter
  ): UserConnection!
}
```

## Best Practices

### Schema Organization

```graphql
# 1. Split schema by domain
# user.graphql
type User {
  id: ID!
  name: String!
}

extend type Query {
  user(id: ID!): User
}

# post.graphql
type Post {
  id: ID!
  title: String!
  author: User!
}

extend type Query {
  post(id: ID!): Post
}

# 2. Use consistent naming
# - Types: PascalCase (User, Post)
# - Fields: camelCase (createdAt, userId)
# - Enums: SCREAMING_SNAKE_CASE (USER_ROLE, POST_STATUS)
# - Input types: PascalCase + "Input" (CreateUserInput)
# - Payload types: PascalCase + "Payload" (CreateUserPayload)

# 3. Document with descriptions
"""
Represents a user in the system.
"""
type User {
  """
  Unique identifier for the user.
  """
  id: ID!

  """
  Full name of the user.
  """
  name: String!
}
```

### Testing

```typescript
import { graphql } from 'graphql';
import { schema } from './schema';

describe('User queries', () => {
  it('should fetch user by ID', async () => {
    const query = `
      query GetUser($id: ID!) {
        user(id: $id) {
          id
          name
          email
        }
      }
    `;

    const result = await graphql({
      schema,
      source: query,
      variableValues: { id: '1' },
      contextValue: { userId: '1' }
    });

    expect(result.data?.user).toEqual({
      id: '1',
      name: 'Alice',
      email: 'alice@example.com'
    });
  });
});
```

### Monitoring

```typescript
import { ApolloServer } from 'apollo-server';
import { ApolloServerPluginUsageReporting } from 'apollo-server-core';

const server = new ApolloServer({
  schema,
  plugins: [
    ApolloServerPluginUsageReporting({
      sendVariableValues: { all: true },
      sendHeaders: { all: true }
    }),
    {
      requestDidStart() {
        const start = Date.now();
        return {
          willSendResponse({ metrics, response }) {
            metrics.queryPlanTrace;  // Log slow queries
            console.log(`Query took ${Date.now() - start}ms`);
          }
        };
      }
    }
  ]
});
```

## Summary

Key takeaways for GraphQL API design:

1. **Design schema for clients**, not database structure
2. **Use strong types** (enums, input types, interfaces)
3. **Prevent N+1** with DataLoader or similar batching
4. **Implement pagination** for all list fields
5. **Add security layers** (depth limit, complexity, auth)
6. **Monitor performance** (query complexity, resolver timing)
7. **Document everything** with descriptions
8. **Version carefully** through schema evolution, not breaking changes
9. **Test thoroughly** (queries, mutations, error cases)
10. **Use unions and interfaces** for flexible, typed errors

GraphQL's power lies in its flexibility and type safety. Use these patterns to build APIs that are both developer-friendly and production-ready.
