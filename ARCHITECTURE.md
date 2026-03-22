# Flick Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Service Architecture](#service-architecture)
4. [Data Flow](#data-flow)
5. [Inter-Service Communication](#inter-service-communication)
6. [Database Schema](#database-schema)
7. [Caching Strategy](#caching-strategy)
8. [Security Architecture](#security-architecture)
9. [Deployment Architecture](#deployment-architecture)

---

## System Overview

Flick is a microservices-based streaming platform consisting of 7 independent services:

| Service | Responsibility | Port | Scale Target |
|---------|----------------|------|--------------|
| Gateway | Frontend, routing, proxy | 8000 | 3+ instances |
| Auth | Authentication, profile | 8001 | 2+ instances |
| Catalog | Movies, metadata | 8002 | 2+ instances |
| Access | Subscriptions, payments | 8003 | 2+ instances |
| Streaming | Video delivery, HLS | 8004 | 3+ instances |
| Recommendation | ML recommendations | 8005 | 2+ instances |
| Notification | Email, alerts | 8006 | 1-2 instances |

---

## Architecture Principles

### 1. Service Independence
Each service is:
- Independently deployable
- Has its own database (logical separation)
- Owns its data model
- Communicates via HTTP APIs

### 2. Horizontal Scalability
- All services are stateless
- Sessions stored in Redis
- Shared nothing architecture

### 3. Fault Tolerance
- Circuit breaker pattern for inter-service calls
- Retry logic with exponential backoff
- Health checks for all services
- NGINX rate limiting

### 4. Security First
- JWT authentication
- BCrypt password hashing
- Security headers (HSTS, CSP, X-Frame-Options)
- CORS control

---

## Service Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTS                                   │
│              (Web, Mobile, Smart TV)                             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NGINX LOAD BALANCER                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ Rate Limit  │ │ Gzip        │ │ Proxy Cache │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
└─────────────────────────┬───────────────────────────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
        ▼                                   ▼
┌───────────────┐                   ┌───────────────┐
│  GATEWAY     │ ◄──────────────── │  GATEWAY     │
│  (Instance 1)│                   │  (Instance N) │
└───────┬───────┘                   └───────┬───────┘
        │
        ├──────────────┬──────────────┬──────────────┐
        │              │              │              │
        ▼              ▼              ▼              ▼
   ┌─────────┐    ┌──────────┐  ┌──────────┐  ┌──────────┐
   │  AUTH   │    │ CATALOG   │  │  ACCESS  │  │STREAMING │
   └─────────┘    └───────────┘  └──────────┘  └──────────┘
                          │              │
                          ▼              ▼
                   ┌──────────┐  ┌──────────┐
                   │RECOMMEND │  │ NOTIFY   │
                   └──────────┘  └──────────┘
                          │
         ┌────────────────┴────────────────┐
         ▼                                 ▼
   ┌──────────┐                      ┌──────────┐
   │  REDIS   │                      │  CELERY  │
   │ (Cache)  │                      │ (Workers)│
   └──────────┘                      └──────────┘
```

---

## Data Flow

### Authentication Flow
```
1. User → Gateway (/login)
2. Gateway → Auth Service (/api/auth/login/)
3. Auth Service → Validate credentials
4. Auth Service → Return JWT
5. Gateway → Set HTTP-only cookie
6. Gateway → Redirect to home
```

### Content Browse Flow
```
1. User → Gateway (/browse)
2. Gateway → Check Redis cache
3. Cache hit → Return cached response
4. Cache miss → Gateway → Catalog Service
5. Catalog Service → Return movies
6. Gateway → Cache response (5 min TTL)
7. Gateway → Render template
```

### Streaming Flow
```
1. User → Gateway (/player/<slug>)
2. Gateway → Verify subscription (Access Service)
3. Access OK → Gateway → Catalog (get video URL)
4. Catalog → Return video metadata
5. Gateway → Render player
6. Player → Streaming Service (HLS chunks)
7. Streaming Service → Transcode/serve video
```

### Recommendation Flow
```
1. User visits content
2. Gateway → Auth Service (track watch history)
3. Background: Celery worker → Process history
4. Celery → Recommendation Engine
5. Recommendation Service → Update user preferences
6. Next request → Personalized recommendations
```

---

## Inter-Service Communication

### Proxy Pattern (Gateway)
The Gateway proxies all requests to backend services:

```python
# Example: Frontend calls /proxy/catalog/movies/
# Gateway forwards to http://catalog_service:8002/api/catalog/movies/
```

### Circuit Breaker
Implemented in `gateway/frontend/circuit_breaker.py`:

```python
class CircuitBreaker:
    failure_threshold = 5    # Open after 5 failures
    recovery_timeout = 30   # Try again after 30s
    half_open_max_calls = 1 # One test request
```

### Retry Logic
```python
MAX_RETRIES = 2
RETRY_DELAY = 0.5  # seconds
```

---

## Database Schema

### Auth Service
```sql
-- Users table
CREATE TABLE auth_user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(150) UNIQUE,
    email VARCHAR(254) UNIQUE,
    password_hash VARCHAR(128),
    is_active BOOLEAN,
    date_joined DATETIME
);

-- Watchlist
CREATE TABLE watchlist (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    movie_id INTEGER
);

-- Watch History
CREATE TABLE watch_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    movie_id INTEGER,
    progress INTEGER,
    last_watched DATETIME
);
```

### Catalog Service
```sql
-- Movies
CREATE TABLE movie (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200),
    slug VARCHAR(200) UNIQUE,
    description TEXT,
    poster_url VARCHAR(500),
    video_url VARCHAR(500),
    release_date DATE,
    duration INTEGER,
    created_at DATETIME
);

-- Genres
CREATE TABLE genre (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50)
);

-- Movie-Genre relationship
CREATE TABLE movie_genre (
    movie_id REFERENCES movie(id),
    genre_id REFERENCES genre(id)
);
```

### Access Service
```sql
-- Subscriptions
CREATE TABLE subscription (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    plan VARCHAR(20),
    status VARCHAR(20),
    start_date DATE,
    end_date DATE
);
```

---

## Caching Strategy

### Redis Usage
| Cache Key | TTL | Content |
|-----------|-----|---------|
| `session:{session_id}` | 7 days | User session data |
| `view:home:{user_id}` | 5 min | Home page |
| `view:browse:{user_id}` | 2 min | Browse page |
| `catalog:movies:{page}` | 5 min | Movie list |
| `catalog:movie:{id}` | 10 min | Movie detail |

### Cache Invalidation
- On content update → Invalidate catalog cache
- On user action → Invalidate user-specific cache
- Redis LRU eviction when memory exceeds 256MB

---

## Security Architecture

### Authentication
- JWT with RS256 signing
- Access token: 15 min expiry
- Refresh token: 7 day expiry (stored in httpOnly cookie)

### Security Headers
```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Rate Limiting (NGINX)
- API routes: 100 requests/second
- Auth routes: 20 requests/second
- Burst allowance for spikes

### Password Security
```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]
```

---

## Deployment Architecture

### Docker Compose (Development)
```yaml
services:
  nginx:          # Load balancer
  gateway:        # 1+ instances
  auth_service:   # 1+ instances
  catalog_service:
  access_service:
  streaming_service:
  recommendation_service:
  notification_service:
  redis:          # Cache + broker
  celery_*:        # Background workers
```

### Render Blueprint (Production)
- 7 Web Services (auto-scaling capable)
- 1 Redis instance (256MB)
- Private networking between services

### NGINX Configuration
```nginx
upstream backend {
    server service:port;
    keepalive 32;
}

location /api/ {
    limit_req zone=api burst=50;
    proxy_pass http://backend;
}
```

---

## Monitoring & Observability

### Health Checks
- `/health/` - Returns service status + dependencies
- `/metrics/` - Request counter (basic)

### Headers
- `X-Request-ID` - Correlation ID for tracing
- `X-Response-Time` - Request duration

### Logging
- JSON formatted logs
- Request/response logging
- Error tracking

---

## Future Enhancements

1. **WebRTC** - Real-time streaming
2. **GraphQL** - Single endpoint for data fetching
3. **gRPC** - Lower latency inter-service calls
4. **Prometheus/Grafana** - Metrics and dashboards
5. **Jaeger** - Distributed tracing
6. **Kafka** - Event streaming

---

*Document Version: 2.0.0*
*Last Updated: 2026-03-23*