from celery import shared_task
import json
import logging
import os
import pandas as pd

logger = logging.getLogger(__name__)


@shared_task
def recalculate_all_recommendations():
    """Periodic task: Recalculate recommendations for all users."""
    from .models import MovieFeature, UserInteraction, CachedRecommendation
    from .engine import engine

    logger.info("Starting recommendation recalculation...")

    # 1. Load movies efficiently
    movie_qs = MovieFeature.objects.all().values(
        'movie_id', 'title', 'genres', 'tags', 'director', 'year', 'rating',
        'view_count', 'trending_score'
    )
    
    movies = []
    movie_map = {} # For faster lookup
    for m in movie_qs.iterator(chunk_size=1000):
        m['genres'] = json.loads(m['genres']) if m['genres'] else []
        m['tags'] = json.loads(m['tags']) if m['tags'] else []
        movies.append(m)
        movie_map[m['movie_id']] = m

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

    # 2. Load interactions and build user-item matrix ONCE
    # Using values_list for memory efficiency
    interactions_qs = UserInteraction.objects.all().values_list('user_id', 'movie_id', 'score')
    
    # Build list of dicts for pandas (could be optimized further but better than before)
    all_interactions = []
    interactions_by_user = {}
    
    for uid, mid, score in interactions_qs.iterator(chunk_size=5000):
        item = {'user_id': uid, 'movie_id': mid, 'score': score}
        all_interactions.append(item)
        if uid not in interactions_by_user:
            interactions_by_user[uid] = []
        interactions_by_user[uid].append(mid) # Just need movie IDs for genre preferences

    if not all_interactions:
        logger.info("No interactions found. Recalculation complete.")
        return

    # Create the user-item matrix once for all collaborative filtering
    df = pd.DataFrame(all_interactions)
    user_item_matrix = df.pivot_table(
        index='user_id', columns='movie_id', values='score', fill_value=0
    )
    
    # 3. Process users in batches
    user_ids = list(interactions_by_user.keys())
    logger.info(f"Processing recommendations for {len(user_ids)} users in batches...")
    
    batch_size = 100
    for i in range(0, len(user_ids), batch_size):
        batch_users = user_ids[i:i+batch_size]
        for user_id in batch_users:
            try:
                # Get user's watched movie IDs from our pre-grouped dict
                user_movie_ids = interactions_by_user.get(user_id, [])

                # Get user's genre preferences
                user_genres = []
                for mid in user_movie_ids:
                    mf = movie_map.get(mid)
                    if mf:
                        user_genres.extend(mf['genres'])

                # Personalized recommendations (using pre-built matrix)
                personalized = engine.get_personalized(
                    user_id, user_genres, movies, user_item=user_item_matrix
                )
                CachedRecommendation.objects.update_or_create(
                    user_id=user_id,
                    recommendation_type='personalized',
                    defaults={
                        'movie_ids': json.dumps([r['movie_id'] for r in personalized]),
                        'scores': json.dumps([r['score'] for r in personalized]),
                    }
                )

                # Collaborative recommendations (using pre-built matrix)
                collab = engine.get_collaborative_recommendations(
                    user_id, user_item=user_item_matrix
                )
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
