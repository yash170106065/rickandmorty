# Technology Tradeoffs & Decision Rationale

This document explains the reasoning behind major technology and architectural decisions, including tradeoffs and alternatives considered.

## Table of Contents

1. [Database Choice: SQLite](#database-choice-sqlite)
2. [API Client: GraphQL vs REST](#api-client-graphql-vs-rest)
3. [Vector Store: SQLite vs Dedicated Solutions](#vector-store-sqlite-vs-dedicated-solutions)
4. [Job Queue: In-Memory vs Cloud Queue](#job-queue-in-memory-vs-cloud-queue)
5. [Frontend Framework: Next.js vs Others](#frontend-framework-nextjs-vs-others)
6. [Architecture: Monolithic vs Microservices](#architecture-monolithic-vs-microservices)

## Database Choice: SQLite

### Decision: SQLite

**Chosen:** SQLite for all data persistence.

### Rationale

**Pros:**
- ✅ **Zero Configuration**: No database server needed
- ✅ **Portable**: Single file, easy to backup/restore
- ✅ **Fast for Small-Medium Data**: Excellent performance for < 100K records
- ✅ **Perfect for Demos**: No external dependencies
- ✅ **ACID Compliant**: Reliable transactions
- ✅ **Built-in Full-Text Search**: FTS5 extension available
- ✅ **Embedding Storage**: JSON storage works well for embeddings

**Cons:**
- ❌ **Concurrent Writes**: Limited write concurrency
- ❌ **No Network Access**: Single-machine only
- ❌ **Size Limits**: Theoretical 281TB, practical limits earlier
- ❌ **No Replication**: No built-in master-slave replication

### Alternatives Considered

#### PostgreSQL
**Pros:**
- Excellent JSON support
- Advanced vector search (pgvector extension)
- Better concurrency
- Production-ready at scale

**Cons:**
- Requires separate server process
- More complex setup
- Overkill for demo/prototype

**Decision**: PostgreSQL would be ideal for production (see [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md))

#### MongoDB
**Pros:**
- Great JSON/document storage
- Horizontal scaling
- Flexible schema

**Cons:**
- Overhead for relational data
- Complex setup
- Less mature vector search support

**Decision**: Not needed for current use case

### Migration Path

See [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) for migration strategy to PostgreSQL.

---

## API Client: GraphQL vs REST

### Decision: GraphQL

**Chosen:** GraphQL client for Rick & Morty API interactions.

### Rationale

**Pros:**
- ✅ **Efficient Data Fetching**: Request exactly what you need
- ✅ **Nested Queries**: Fetch locations with residents in one call
- ✅ **Type Safety**: Strong schema definitions
- ✅ **Single Endpoint**: Fewer network roundtrips
- ✅ **Rick & Morty API Native**: Official API provides GraphQL

**Cons:**
- ❌ **Learning Curve**: More complex than REST
- ❌ **Caching Complexity**: Harder to cache than REST endpoints
- ❌ **Over-fetching Risk**: Can request too much data

### Alternatives Considered

#### REST API
**Pros:**
- Simpler mental model
- Better HTTP caching
- More familiar to most developers

**Cons:**
- Multiple requests for related data
- Over-fetching (get entire resource when you need one field)
- N+1 query problems

**Example Comparison:**

**REST (Multiple Requests):**
```http
GET /api/location/1
GET /api/character/1
GET /api/character/2
GET /api/character/3
... (for all residents)
```

**GraphQL (Single Request):**
```graphql
query {
  location(id: 1) {
    name
    residents {
      name
      species
    }
  }
}
```

**Decision**: GraphQL's efficiency wins for this use case where we frequently need nested data.

---

## Vector Store: SQLite vs Dedicated Solutions

### Decision: SQLite (Custom Implementation)

**Chosen:** SQLite-based vector store using JSON column for embeddings.

### Rationale

**Pros:**
- ✅ **Zero Dependencies**: No additional services
- ✅ **Consistent Stack**: Same database for all data
- ✅ **Good Enough Performance**: Adequate for demo/prototype
- ✅ **Simple Implementation**: No infrastructure complexity

**Cons:**
- ❌ **Linear Search**: O(n) full table scan
- ❌ **Not Optimized**: No specialized vector indexes
- ❌ **Limited Scale**: Slows down with > 10K vectors
- ❌ **CPU Intensive**: Cosine similarity calculated in Python

### Alternatives Considered

#### PostgreSQL + pgvector
**Pros:**
- Specialized vector indexes (IVFFlat, HNSW)
- Fast approximate nearest neighbor search
- Production-ready at scale
- Integrated with existing data

**Cons:**
- Requires pgvector extension
- Additional setup complexity
- Overkill for demo

**Decision**: Best choice for production (see [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md))

#### Pinecone / Weaviate / Qdrant
**Pros:**
- Managed service (Pinecone)
- Highly optimized
- Scales automatically
- Great performance

**Cons:**
- External dependency
- Additional costs
- Network latency
- Vendor lock-in

**Decision**: Great for production, unnecessary for demo

#### Redis with RediSearch
**Pros:**
- In-memory speed
- Good performance
- Existing Redis infrastructure

**Cons:**
- Additional service
- Memory constraints
- Limited vector search features

**Decision**: Not chosen due to additional complexity

### Performance Comparison

| Solution | Setup Complexity | Search Speed | Scale Limit | Cost |
|----------|-----------------|-------------|-------------|------|
| SQLite (Current) | ⭐ Low | ⚠️ Slow (~100ms/1K vectors) | ~10K vectors | Free |
| PostgreSQL + pgvector | ⭐⭐ Medium | ✅ Fast (~10ms) | Millions | Free |
| Pinecone | ⭐ Low | ✅✅ Very Fast (~5ms) | Unlimited | $$ |
| Weaviate | ⭐⭐ Medium | ✅✅ Very Fast (~5ms) | Millions | Free/$$ |

**Current Decision**: SQLite is perfect for demo, but production should migrate to PostgreSQL + pgvector or managed service.

---

## Job Queue: In-Memory vs Cloud Queue

### Decision: In-Memory Async Queue

**Chosen:** In-memory job queue with async processing.

### Rationale

**Pros:**
- ✅ **Simple Implementation**: No external services
- ✅ **Zero Setup**: Works out of the box
- ✅ **Fast**: No network overhead
- ✅ **Sufficient for Demo**: Handles async evaluation jobs

**Cons:**
- ❌ **Not Persistent**: Jobs lost on restart
- ❌ **Single Process**: Can't scale horizontally
- ❌ **No Retry Logic**: Failed jobs are lost
- ❌ **Memory Bound**: Limited by process memory

### Alternatives Considered

#### AWS SQS / Google Cloud Tasks
**Pros:**
- Managed service
- Persistent
- Horizontal scaling
- Built-in retries
- Dead letter queues

**Cons:**
- External dependency
- Additional costs
- Network latency
- AWS/Google account needed

**Decision**: Overkill for demo, perfect for production

#### Redis Queue (RQ) / Celery
**Pros:**
- Persistent (if Redis persists)
- Better than in-memory
- Mature libraries
- Good for production

**Cons:**
- Additional service (Redis)
- More setup complexity

**Decision**: Good middle ground, see [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md)

#### Kafka / RabbitMQ
**Pros:**
- Highly scalable
- Distributed
- Production-grade

**Cons:**
- Significant complexity
- Overkill for this use case
- Steep learning curve

**Decision**: Not needed for current scale

### When to Migrate

See [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) for migration triggers:
- > 1000 jobs/hour
- Need job persistence
- Horizontal scaling required

---

## Frontend Framework: Next.js vs Others

### Decision: Next.js 14 (App Router)

**Chosen:** Next.js with App Router and TypeScript.

### Rationale

**Pros:**
- ✅ **Server Components**: Reduce client bundle size
- ✅ **Built-in Routing**: File-based routing
- ✅ **API Integration**: Easy backend integration
- ✅ **TypeScript Support**: First-class TypeScript
- ✅ **Great DX**: Hot reload, error messages
- ✅ **Production Ready**: Optimizations built-in

**Cons:**
- ❌ **Opinionated**: Less flexibility than raw React
- ❌ **Learning Curve**: App Router is relatively new
- ❌ **Bundle Size**: Larger than minimal React setup

### Alternatives Considered

#### Create React App (CRA)
**Pros:**
- Simple setup
- Familiar to many developers

**Cons:**
- Deprecated
- No server-side rendering
- Larger bundle sizes

**Decision**: Not chosen (CRA is deprecated)

#### Vite + React
**Pros:**
- Very fast dev server
- Small bundle size
- Flexible

**Cons:**
- No server components
- More manual setup
- Need to add routing, SSR manually

**Decision**: Great for simple apps, but Next.js features are valuable

#### Remix
**Pros:**
- Great form handling
- Simple data loading

**Cons:**
- Smaller ecosystem
- Less mature

**Decision**: Next.js has better ecosystem support

### Type Safety

**Decision**: TypeScript throughout frontend.

**Rationale**:
- Catch errors at compile time
- Better IDE support
- Self-documenting code
- Worth the small overhead

---

## Architecture: Monolithic vs Microservices

### Decision: Monolithic (for now)

**Chosen:** Single FastAPI application handling all concerns.

### Rationale

**Pros:**
- ✅ **Simple Development**: One codebase
- ✅ **Easy Deployment**: Single deployable unit
- ✅ **Low Latency**: No network calls between services
- ✅ **Easier Debugging**: All code in one place
- ✅ **Perfect for Demo**: No orchestration complexity

**Cons:**
- ❌ **Scaling Limits**: Can't scale components independently
- ❌ **Technology Lock-in**: Single tech stack
- ❌ **Deployment Risk**: Single point of failure

### When to Consider Microservices

See [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) for breakdown strategy:

**Potential Services:**
- **API Gateway**: Request routing
- **Character Service**: Character-related operations
- **Generation Service**: AI content generation
- **Search Service**: Vector search
- **Evaluation Service**: Content scoring

**Triggers for Migration:**
- Team size > 10 developers
- Need to scale services independently
- Different tech stacks per service
- Clear service boundaries emerge

**Current Decision**: Monolithic is correct choice for current scale.

---

## Summary Table

| Decision | Chosen | Alternative | When to Revisit |
|----------|--------|------------|-----------------|
| Database | SQLite | PostgreSQL | Production deployment |
| Vector Store | SQLite | pgvector/Pinecone | > 10K embeddings |
| Job Queue | In-memory | SQS/Celery | Need persistence/scale |
| API Client | GraphQL | REST | N/A (API provides GraphQL) |
| Frontend | Next.js | Vite/Remix | Simpler needs |
| Architecture | Monolithic | Microservices | Team > 10 or scale needs |

---

## Decision Framework

When evaluating technologies, we consider:

1. **Current Needs**: What works for demo/prototype?
2. **Future Needs**: What will we need in production?
3. **Team Expertise**: Can the team maintain it?
4. **Cost**: Both monetary and complexity cost
5. **Migration Path**: Can we migrate later?

**Philosophy**: Start simple, optimize when needed.

---

**Key Insight**: Every technology choice is a tradeoff. The current stack prioritizes:
- ✅ Simplicity (easy setup)
- ✅ Demo-readiness (works immediately)
- ✅ Clear migration paths (can upgrade later)

Production deployments should follow recommendations in [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md).

