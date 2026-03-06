from celery import shared_task
import json
import logging
import os

logger = logging.getLogger(__name__)


@shared_task
def recalculate_all_recommendations():
    """Periodic task: Recalculate recommendations for all users."""
    from .models import MovieFeature, UserInteraction, CachedRecommendation
    from .engine import engine

    logger.info("Starting recommendation recalculation...")

    # Get all movies
    movies = list(MovieFeature.objects.all().values(
        'movie_id', 'title', 'genres', 'tags', 'director', 'year', 'rating',
        'view_count', 'trending_score'
    ))

    # Parse JSON fields
    for m in movies:
        m['genres'] = json.loads(m['genres']) if m['genres'] else []
        m['tags'] = json.loads(m['tags']) if m['tags'] else []

    # Get all interactions
    interactions = list(UserInteraction.objects.all().values(
        'user_id', 'movie_id', 'score'
    ))

    # Get unique users
    user_ids = set(i['user_id'] for i in interactions)

    # Calculate trending for all
    trending = engine.get_trending(movies)
    trending_ids = json.dumps([t['movie_id'] for t in trending])
    trending_scores = json.dumps([t['score'] for t in trending])

    # Cache trending globally (user_id=0)
    CachedRecommendation.objects.update_or_create(
        user_id=0,
        recommendation_type='trending',
        defaults={'movie_ids': trending_ids, 'scores': trending_scores}
    )

    # Per-user recommendations
    for user_id in user_ids:
        try:
            user_interactions = [i for i in interactions if i['user_id'] == user_id]
            user_movie_ids = [i['movie_id'] for i in user_interactions]

            # Get user's genre preferences from their watched movies
            user_genres = []
            for mid in user_movie_ids:
                mf = next((m for m in movies if m['movie_id'] == mid), None)
                if mf:
                    user_genres.extend(mf['genres'])

            # Personalized recommendations
            personalized = engine.get_personalized(user_id, user_genres, movies, interactions)
            CachedRecommendation.objects.update_or_create(
                user_id=user_id,
                recommendation_type='personalized',
                defaults={
                    'movie_ids': json.dumps([r['movie_id'] for r in personalized]),
                    'scores': json.dumps([r['score'] for r in personalized]),
                }
            )

            # Collaborative recommendations
            collab = engine.get_collaborative_recommendations(user_id, interactions)
            CachedRecommendation.objects.update_or_create(
                user_id=user_id,
                recommendation_type='collaborative',
                defaults={
                    'movie_ids': json.dumps([r['movie_id'] for r in collab]),
                    'scores': json.dumps([r['score'] for r in collab]),
                }
            )

        except Exception as e:
            logger.error(f"Error calculating recs for user {user_id}: {e}")

    # Cache in Redis for fast retrieval
    try:
        import redis
        r = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
        r.set('flick:trending', trending_ids, ex=21600)  # 6 hour TTL
    except Exception as e:
        logger.error(f"Redis cache error: {e}")

    logger.info(f"Recommendation recalculation complete for {len(user_ids)} users")


@shared_task
def record_interaction(user_id, movie_id, interaction_type, score=1.0):
    """Record a user-movie interaction."""
    from .models import UserInteraction

    UserInteraction.objects.create(
        user_id=user_id,
        movie_id=movie_id,
        interaction_type=interaction_type,
        score=score,
    )
