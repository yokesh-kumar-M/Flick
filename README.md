# Flick 🎬

Flick is a microservices-based streaming platform backend built with Django, Django REST Framework, Redis, and Celery.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FLICK STREAMING PLATFORM                       │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ┌──────────────┐
                                    │   CLIENTS     │
                                    │ (Web/Mobile)  │
                                    └───────┬──────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               API GATEWAY                                    │
│                         (Port 8000 - Gateway)                              │
│                    Routes requests, serves frontend                         │
└─────────────────────────────────────────────────────────────────────────────┘
        │              │              │              │              │              │
        ▼              ▼              ▼              ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│    AUTH     │ │   CATALOG   │ │   ACCESS    │ │  STREAMING  │ │RECOMMENDATION│
│  SERVICE    │ │  SERVICE    │ │  SERVICE    │ │  SERVICE    │ │   SERVICE   │
│  (8001)     │ │  (8002)     │ │  (8003)     │ │  (8004)     │ │   (8005)    │
│             │ │             │ │             │ │             │ │             │
│ - Register  │ │ - Movies    │ │ - Subs      │ │ - Stream    │ │ - ML Engine │
│ - Login     │ │ - TV Shows  │ │ - Payments  │ │ - HLS       │ │ - Trending  │
│ - JWT       │ │ - Metadata  │ │ - Access    │ │ - Progress  │ │ - Personal  │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
        │                                                                 │
        │                                         ┌─────────────┐
        │                                         │ NOTIFICATION│
        │                                         │  SERVICE    │
        │                                         │  (8006)     │
        │                                         │             │
        │                                         │ - Email     │
        │                                         │ - Alerts    │
        └─────────────────────────────────────────┴─────────────┘

                                    ┌──────────────┐
                                    │    REDIS     │
                                    │  (Cache/Broker)│
                                    └──────────────┘
```

## Services Overview

| Service | Port | Description |
|---------|------|-------------|
| Gateway | 8000 | API Gateway, Frontend routing, Request proxying |
| Auth | 8001 | User authentication, JWT tokens, Profile management |
| Catalog | 8002 | Movies, TV shows, Metadata management |
| Access | 8003 | Subscription management, Payment verification |
| Streaming | 8004 | Video streaming, Progress tracking |
| Recommendation | 8005 | ML-powered recommendations, Trending analysis |
| Notification | 8006 | Email alerts, User notifications |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string (Supabase/custom) | `sqlite:///db.sqlite3` |
| `SECRET_KEY` | Django secret key for cryptographic signing | Dev fallback |
| `DEBUG` | Enable debug mode | `True` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins | `http://localhost:3000,http://localhost:8000` |
| `SUPABASE_URL` | Supabase project URL | - |
| `SUPABASE_KEY` | Supabase API key | - |
| `CELERY_BROKER_URL` | Celery message broker URL | `redis://localhost:6379/1` |
| `CELERY_RESULT_BACKEND` | Celery result storage URL | `redis://localhost:6379/2` |

### Service-specific URLs

| Variable | Description | Default |
|----------|-------------|---------|
| `AUTH_SERVICE_URL` | Auth service base URL | `http://localhost:8001` |
| `CATALOG_SERVICE_URL` | Catalog service base URL | `http://localhost:8002` |
| `ACCESS_SERVICE_URL` | Access service base URL | `http://localhost:8003` |
| `STREAMING_SERVICE_URL` | Streaming service base URL | `http://localhost:8004` |
| `RECOMMENDATION_SERVICE_URL` | Recommendation service base URL | `http://localhost:8005` |
| `NOTIFICATION_SERVICE_URL` | Notification service base URL | `http://localhost:8006` |

## API Endpoints

### Gateway (Port 8000)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health/` | GET | Health check |
| `/` | GET | Frontend |
| `/api/` | GET | API info |

### Auth Service (Port 8001)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health/` | GET | Health check |
| `/api/auth/register/` | POST | User registration |
| `/api/auth/login/` | POST | User login |
| `/api/auth/logout/` | POST | User logout |
| `/api/auth/refresh/` | POST | Refresh access token |
| `/api/auth/profile/` | GET/PUT | User profile |
| `/api/auth/watchlist/` | GET/POST | Watchlist management |
| `/api/auth/watch-history/` | GET | Watch history |
| `/api/auth/stats/` | GET | User statistics |

### Catalog Service (Port 8002)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health/` | GET | Health check |
| `/api/catalog/movies/` | GET | List movies |
| `/api/catalog/movies/<id>/` | GET | Movie details |
| `/api/catalog/genres/` | GET | List genres |
| `/api/catalog/search/` | GET | Search content |

### Access Service (Port 8003)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health/` | GET | Health check |
| `/api/access/subscribe/` | POST | Subscribe to plan |
| `/api/access/verify/` | GET | Verify subscription |
| `/api/access/plans/` | GET | List subscription plans |

### Streaming Service (Port 8004)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health/` | GET | Health check |
| `/api/streaming/video/<id>/` | GET | Stream video |
| `/api/streaming/progress/` | POST | Update watch progress |

### Recommendation Service (Port 8005)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health/` | GET | Health check |
| `/api/recommendations/` | GET | Get recommendations |
| `/api/recommendations/similar/<id>/` | GET | Similar movies |
| `/api/recommendations/trending/` | GET | Trending content |

### Notification Service (Port 8006)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health/` | GET | Health check |
| `/api/notifications/` | GET | List notifications |
| `/api/notifications/read/<id>/` | POST | Mark as read |

## Deployment

### Render (Recommended for microservices)
Flick includes a `render.yaml` Blueprint which automatically provisions the 7 web services and 1 Redis instance.
1. Connect this repository to Render
2. Click "New Blueprint" to deploy the entire stack automatically
3. Set `DATABASE_URL` to your Supabase or PostgreSQL connection string

### Vercel
Alternatively, if you wish to run the Gateway on Vercel as serverless functions, you can configure Vercel to run the `gateway` WSGI application via `vercel.json` (serverless python execution).

## Local Development

To run locally, simply use the provided batch script:
```bash
./run_all.bat
```
*(Requires Python, Pip, and optionally Redis for caching/Celery jobs).*

## CI/CD

The project includes GitHub Actions workflows for:
- Linting with flake8
- Django system checks for all services
- Deployment notifications on successful builds

## Tech Stack

- **Backend**: Django 5.1, Django REST Framework 3.15
- **Authentication**: PyJWT, bcrypt
- **Caching/Message Broker**: Redis 5.0
- **Task Queue**: Celery 5.3
- **Static Files**: WhiteNoise 6.7
- **ML**: scikit-learn, pandas, numpy
- **Database**: PostgreSQL (via Supabase) / SQLite (dev)
