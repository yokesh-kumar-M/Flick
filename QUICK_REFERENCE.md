# Flick — Quick Reference

## Architecture
7 microservices communicating via REST + JWT cookies.

| Service | Port | Purpose |
|---------|------|---------|
| Gateway | 8000 | Frontend + API proxy |
| Auth | 8001 | Users, JWT, watchlist, watch history |
| Catalog | 8002 | Movies, genres, categories, reviews |
| Access | 8003 | Access control, payments |
| Streaming | 8004 | HLS streaming, transcoding |
| Recommendation | 8005 | Personalized recommendations |
| Notification | 8006 | User notifications |

## Start
```bash
run_all.bat
```

## Frontend Routes

| URL | Page |
|-----|------|
| `/` | Home (hero, carousels, orbital genres) |
| `/browse/` | Browse with mood engine + filters |
| `/search/` | Search with autocomplete + recent history |
| `/movie/<slug>/` | Movie detail + reviews |
| `/watch/<slug>/` | Video player with access guard |
| `/profile/` | Profile (overview, account, security, history, watchlist, reviews) |
| `/genre/<slug>/` | Genre page with stats + sorting |
| `/playlist/<slug>/` | Playlist page |
| `/payment/` | Payment portal |
| `/admin-panel/` | Admin dashboard |
| `/login/` `/register/` | Auth pages |

## Key Features
- **5 movie card variants**: standard, hero, compact, banner, spotlight
- **Super Access**: Admin-granted unlimited access
- **Payment system**: Mock payment flow for per-movie access
- **Reviews & Ratings**: 1-10 scale, spoiler flags, likes, sorting
- **Server-side watchlist**: Synced across devices
- **Player access guard**: Checks access before allowing playback
- **Autocomplete search**: Real-time suggestions, recent searches
- **Mood-based browsing**: 8 mood categories (Intense, Chill, Dark, etc.)
- **Orbital genre ring**: Visual genre navigation on homepage
- **Theme engine**: Dynamic colors extracted from movie posters
- **Audio engine**: EQ, visualizer, spatial audio in player
- **Notifications**: Auto-sent on register, access approve/deny, new reviews

## Databases (SQLite per service)

### Auth Service
- `FlickUser` — users with bcrypt passwords, avatars, super_access
- `WatchHistory` — per-user movie progress tracking
- `UserWatchlist` — server-side saved movies
- `GenreStats` — per-user genre watch stats

### Catalog Service
- `Category`, `Genre`, `Movie`, `Playlist`
- `Review` — user reviews (1-10 rating, spoiler flag, likes)

### Access Service
- `AccessRequest` — payment flow tracking
- `AccessGrant` — active access codes

### Streaming Service
- `StreamSession` — active stream tracking
- `TranscodeJob` — FFmpeg HLS transcoding

### Recommendation Service
- `MovieFeature`, `UserInteraction`, `CachedRecommendation`

### Notification Service
- `Notification` — with types, links, read status

## Shared Utilities (`shared/`)
- `jwt_utils.py` — JWT create/decode, access codes, signed URLs
- `auth_middleware.py` — JWT middleware + decorators
- `service_client.py` — Inter-service HTTP + `send_notification()` helper
