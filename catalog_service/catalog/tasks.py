from celery import shared_task
import logging
from .models import Movie
from .search_engine import sync_movie_to_es

logger = logging.getLogger(__name__)

@shared_task
def sync_movie_to_es_task(movie_id):
    """Celery task to sync a movie to Elasticsearch."""
    try:
        movie = Movie.objects.get(pk=movie_id)
        sync_movie_to_es(movie)
        logger.info(f"Successfully synced movie {movie_id} to ES")
    except Movie.DoesNotExist:
        logger.error(f"Movie {movie_id} not found for ES sync")
    except Exception as e:
        logger.error(f"Error syncing movie {movie_id} to ES: {e}")
