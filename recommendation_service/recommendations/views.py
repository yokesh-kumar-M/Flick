from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import MovieFeature, UserInteraction, CachedRecommendation
from .engine import engine
import json, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.jwt_utils import decode_token


def get_user_payload(request):
    token = request.COOKIES.get('access_token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
    return decode_token(token) if token else None


@api_view(['GET'])
@permission_classes([AllowAny])
def get_recommendations(request):
    """Get personalized recommendations for the current user."""
    payload = get_user_payload(request)
    rec_type = request.GET.get('type', 'personalized')

    if payload:
        user_id = payload['user_id']
        cached = CachedRecommendation.objects.filter(
            user_id=user_id, recommendation_type=rec_type
        ).first()

        if cached:
            return Response({
                'type': rec_type,
                'movie_ids': cached.get_movie_ids(),
                'scores': cached.get_scores(),
            })

    # Fall back to trending
    cached = CachedRecommendation.objects.filter(
        user_id=0, recommendation_type='trending'
    ).first()

    if cached:
        return Response({
            'type': 'trending',
            'movie_ids': cached.get_movie_ids(),
            'scores': cached.get_scores(),
        })

    # If no cached data, return top movies by feature data
    top_movies = MovieFeature.objects.all().order_by('-trending_score', '-view_count')[:15]
    return Response({
        'type': 'trending',
        'movie_ids': [m.movie_id for m in top_movies],
        'scores': [m.trending_score for m in top_movies],
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_similar(request, movie_id):
    """Get movies similar to the specified movie."""
    movies = list(MovieFeature.objects.all().values(
        'movie_id', 'title', 'genres', 'tags', 'director', 'year', 'rating'
    ))
    for m in movies:
        m['genres'] = json.loads(m['genres']) if m['genres'] else []
        m['tags'] = json.loads(m['tags']) if m['tags'] else []

    similar = engine.get_similar_movies(movie_id, movies, top_n=10)
    return Response({
        'movie_id': movie_id,
        'similar': similar,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_trending(request):
    """Get trending movies."""
    movies = list(MovieFeature.objects.all().values(
        'movie_id', 'title', 'trending_score', 'view_count', 'rating'
    ))
    trending = engine.get_trending(movies)
    return Response({'trending': trending})


@api_view(['POST'])
def record_interaction(request):
    """Record a user interaction with a movie."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    movie_id = request.data.get('movie_id')
    interaction_type = request.data.get('type', 'view')
    score = request.data.get('score', 1.0)

    if not movie_id:
        return Response({'error': 'movie_id required'}, status=status.HTTP_400_BAD_REQUEST)

    UserInteraction.objects.create(
        user_id=payload['user_id'],
        movie_id=movie_id,
        interaction_type=interaction_type,
        score=score,
    )

    return Response({'message': 'Interaction recorded'})


@api_view(['POST'])
def sync_movies(request):
    """Sync movie features from catalog service (admin/internal)."""
    payload = get_user_payload(request)
    if not payload or not payload.get('is_admin'):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    movies = request.data.get('movies', [])
    synced = 0

    for movie_data in movies:
        MovieFeature.objects.update_or_create(
            movie_id=movie_data['id'],
            defaults={
                'title': movie_data.get('title', ''),
                'genres': json.dumps(movie_data.get('genres', [])),
                'tags': json.dumps(movie_data.get('tags', [])),
                'director': movie_data.get('director', ''),
                'year': movie_data.get('release_year', 2024),
                'rating': movie_data.get('rating', 0),
                'view_count': movie_data.get('view_count', 0),
                'trending_score': movie_data.get('trending_score', 0),
                'feature_vector': ' '.join([
                    movie_data.get('title', ''),
                    ' '.join(movie_data.get('genres', [])),
                    ' '.join(movie_data.get('tags', [])),
                    movie_data.get('director', ''),
                ]),
            }
        )
        synced += 1

    return Response({'message': f'Synced {synced} movies'})


@api_view(['POST'])
def trigger_recalculation(request):
    """Admin: Trigger recommendation recalculation."""
    payload = get_user_payload(request)
    if not payload or not payload.get('is_admin'):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    from .tasks import recalculate_all_recommendations
    recalculate_all_recommendations.delay()

    return Response({'message': 'Recalculation triggered'})
