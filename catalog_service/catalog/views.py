from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, F, Avg, Count
from .models import Category, Genre, Movie, Review, Playlist
from .serializers import (
    CategorySerializer, GenreSerializer, MovieListSerializer,
    MovieDetailSerializer, MovieCreateSerializer, PlaylistSerializer,
    PlaylistListSerializer, ReviewSerializer, ReviewCreateSerializer
)
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.jwt_utils import decode_token


def get_user_payload(request):
    token = request.COOKIES.get('access_token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
    return decode_token(token) if token else None


def require_admin(request):
    payload = get_user_payload(request)
    if not payload or not payload.get('is_admin'):
        return None
    return payload


# ══════════════════════════════════════
# Categories
# ══════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    categories = Category.objects.filter(is_active=True)
    return Response(CategorySerializer(categories, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def category_detail(request, slug):
    try:
        category = Category.objects.get(slug=slug, is_active=True)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    movies = Movie.objects.filter(category=category, is_active=True)
    return Response({
        'category': CategorySerializer(category).data,
        'movies': MovieListSerializer(movies, many=True).data
    })


@api_view(['POST'])
def category_create(request):
    if not require_admin(request):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    name = request.data.get('name', '').strip()
    slug = request.data.get('slug', '').strip()
    if not name:
        return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)
    if not slug:
        slug = name.lower().replace(' ', '-')
    icon = request.data.get('icon', '🎬')
    description = request.data.get('description', '')
    order = request.data.get('order', 0)
    cat = Category.objects.create(name=name, slug=slug, icon=icon, description=description, order=order)
    return Response(CategorySerializer(cat).data, status=status.HTTP_201_CREATED)


@api_view(['PATCH', 'PUT'])
def category_update(request, pk):
    if not require_admin(request):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    try:
        cat = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
    for field in ['name', 'slug', 'icon', 'description', 'order', 'is_active']:
        if field in request.data:
            setattr(cat, field, request.data[field])
    cat.save()
    return Response(CategorySerializer(cat).data)


@api_view(['DELETE'])
def category_delete(request, pk):
    if not require_admin(request):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    try:
        cat = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
    cat.is_active = False
    cat.save()
    return Response({'message': 'Category deleted'})


# ══════════════════════════════════════
# Genres
# ══════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def genre_list(request):
    genres = Genre.objects.all()
    return Response(GenreSerializer(genres, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def genre_movies(request, slug):
    try:
        genre = Genre.objects.get(slug=slug)
    except Genre.DoesNotExist:
        return Response({'error': 'Genre not found'}, status=status.HTTP_404_NOT_FOUND)
    movies = Movie.objects.filter(genres=genre, is_active=True)
    return Response({
        'genre': GenreSerializer(genre).data,
        'movies': MovieListSerializer(movies, many=True).data
    })


@api_view(['POST'])
def genre_create(request):
    if not require_admin(request):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    name = request.data.get('name', '').strip()
    slug = request.data.get('slug', '').strip()
    if not name:
        return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)
    if not slug:
        slug = name.lower().replace(' ', '-')
    if Genre.objects.filter(slug=slug).exists():
        return Response({'error': 'Genre with this slug already exists'}, status=status.HTTP_400_BAD_REQUEST)
    genre = Genre.objects.create(name=name, slug=slug)
    return Response(GenreSerializer(genre).data, status=status.HTTP_201_CREATED)


@api_view(['PATCH', 'PUT'])
def genre_update(request, pk):
    if not require_admin(request):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    try:
        genre = Genre.objects.get(pk=pk)
    except Genre.DoesNotExist:
        return Response({'error': 'Genre not found'}, status=status.HTTP_404_NOT_FOUND)
    if 'name' in request.data:
        genre.name = request.data['name']
    if 'slug' in request.data:
        genre.slug = request.data['slug']
    genre.save()
    return Response(GenreSerializer(genre).data)


@api_view(['DELETE'])
def genre_delete(request, pk):
    if not require_admin(request):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    try:
        genre = Genre.objects.get(pk=pk)
    except Genre.DoesNotExist:
        return Response({'error': 'Genre not found'}, status=status.HTTP_404_NOT_FOUND)
    genre.delete()
    return Response({'message': 'Genre deleted'})


# ══════════════════════════════════════
# Movies
# ══════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def movie_list(request):
    movies = Movie.objects.filter(is_active=True)

    genre = request.GET.get('genre')
    category = request.GET.get('category')
    content_type = request.GET.get('type')
    year = request.GET.get('year')
    featured = request.GET.get('featured')
    sort = request.GET.get('sort', '-created_at')

    if genre:
        movies = movies.filter(genres__slug=genre)
    if category:
        movies = movies.filter(category__slug=category)
    if content_type:
        movies = movies.filter(content_type=content_type)
    if year:
        movies = movies.filter(release_year=int(year))
    if featured:
        movies = movies.filter(is_featured=True)

    valid_sorts = ['-created_at', 'created_at', '-rating', 'rating',
                   '-view_count', '-trending_score', 'title', '-title', '-release_year']
    if sort in valid_sorts:
        movies = movies.order_by(sort)

    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    total = movies.count()

    return Response({
        'results': MovieListSerializer(movies[start:end], many=True).data,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def movie_detail(request, slug):
    try:
        movie = Movie.objects.get(slug=slug, is_active=True)
    except Movie.DoesNotExist:
        return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)

    Movie.objects.filter(id=movie.id).update(view_count=F('view_count') + 1)
    movie.refresh_from_db()

    genre_ids = movie.genres.values_list('id', flat=True)
    similar = Movie.objects.filter(
        genres__in=genre_ids, is_active=True
    ).exclude(id=movie.id).distinct()[:10]

    # Include review stats
    review_stats = Review.objects.filter(movie=movie, is_active=True).aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )

    return Response({
        'movie': MovieDetailSerializer(movie).data,
        'similar': MovieListSerializer(similar, many=True).data,
        'review_stats': {
            'average_rating': round(review_stats['avg_rating'] or 0, 1),
            'total_reviews': review_stats['total_reviews'] or 0,
        },
    })


@api_view(['POST'])
def movie_create(request):
    if not require_admin(request):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    serializer = MovieCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    movie = serializer.save()
    return Response(MovieDetailSerializer(movie).data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'PATCH'])
def movie_update(request, pk):
    if not require_admin(request):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        movie = Movie.objects.get(pk=pk)
    except Movie.DoesNotExist:
        return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = MovieCreateSerializer(movie, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    movie = serializer.save()
    return Response(MovieDetailSerializer(movie).data)


@api_view(['DELETE'])
def movie_delete(request, pk):
    if not require_admin(request):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        movie = Movie.objects.get(pk=pk)
    except Movie.DoesNotExist:
        return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)

    movie.is_active = False
    movie.save()
    return Response({'message': 'Movie deleted successfully'})


# ══════════════════════════════════════
# Playlists
# ══════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def playlist_list(request):
    playlists = Playlist.objects.all()
    return Response(PlaylistListSerializer(playlists, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def playlist_detail(request, slug):
    try:
        playlist = Playlist.objects.get(slug=slug)
    except Playlist.DoesNotExist:
        return Response({'error': 'Playlist not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(PlaylistSerializer(playlist).data)


@api_view(['POST'])
def playlist_create(request):
    if not require_admin(request):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    name = request.data.get('name', '').strip()
    slug = request.data.get('slug', '').strip()
    if not name:
        return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)
    if not slug:
        slug = name.lower().replace(' ', '-')
    description = request.data.get('description', '')
    is_featured = request.data.get('is_featured', False)
    order = request.data.get('order', 0)
    pl = Playlist.objects.create(name=name, slug=slug, description=description, is_featured=is_featured, order=order)
    return Response(PlaylistListSerializer(pl).data, status=status.HTTP_201_CREATED)


@api_view(['PATCH', 'PUT'])
def playlist_update(request, pk):
    if not require_admin(request):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    try:
        pl = Playlist.objects.get(pk=pk)
    except Playlist.DoesNotExist:
        return Response({'error': 'Playlist not found'}, status=status.HTTP_404_NOT_FOUND)
    for field in ['name', 'slug', 'description', 'is_featured', 'order', 'poster_url']:
        if field in request.data:
            setattr(pl, field, request.data[field])
    pl.save()
    return Response(PlaylistListSerializer(pl).data)


@api_view(['DELETE'])
def playlist_delete(request, pk):
    if not require_admin(request):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    try:
        pl = Playlist.objects.get(pk=pk)
    except Playlist.DoesNotExist:
        return Response({'error': 'Playlist not found'}, status=status.HTTP_404_NOT_FOUND)
    pl.delete()
    return Response({'message': 'Playlist deleted'})


# ══════════════════════════════════════
# Search
# ══════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def search(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return Response({'results': [], 'query': query})

    movies = Movie.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(director__icontains=query) |
        Q(cast__icontains=query) |
        Q(tags__icontains=query),
        is_active=True
    ).distinct()[:30]

    return Response({
        'results': MovieListSerializer(movies, many=True).data,
        'query': query,
        'total': movies.count() if hasattr(movies, 'count') else len(movies),
    })


# ══════════════════════════════════════
# Trending / Featured / New Releases
# ══════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def trending(request):
    movies = Movie.objects.filter(is_active=True).order_by('-trending_score', '-view_count')[:20]
    return Response(MovieListSerializer(movies, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def featured(request):
    movies = Movie.objects.filter(is_active=True, is_featured=True).order_by('-created_at')[:10]
    return Response(MovieListSerializer(movies, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def new_releases(request):
    movies = Movie.objects.filter(is_active=True).order_by('-release_year', '-created_at')[:20]
    return Response(MovieListSerializer(movies, many=True).data)


# ══════════════════════════════════════
# Homepage Data
# ══════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def homepage_data(request):
    """Return all data needed for the homepage."""
    featured_movies = Movie.objects.filter(is_active=True, is_featured=True)[:5]
    trending_movies = Movie.objects.filter(is_active=True).order_by('-trending_score')[:15]
    new_movies = Movie.objects.filter(is_active=True).order_by('-created_at')[:15]
    top_rated = Movie.objects.filter(is_active=True, rating__gt=0).order_by('-rating')[:15]
    categories = Category.objects.filter(is_active=True)
    playlists = Playlist.objects.filter(is_featured=True)

    genres_with_movies = []
    for genre in Genre.objects.all()[:8]:
        movies = Movie.objects.filter(genres=genre, is_active=True)[:15]
        if movies.exists():
            genres_with_movies.append({
                'genre': GenreSerializer(genre).data,
                'movies': MovieListSerializer(movies, many=True).data,
            })

    return Response({
        'featured': MovieListSerializer(featured_movies, many=True).data,
        'trending': MovieListSerializer(trending_movies, many=True).data,
        'new_releases': MovieListSerializer(new_movies, many=True).data,
        'top_rated': MovieListSerializer(top_rated, many=True).data,
        'categories': CategorySerializer(categories, many=True).data,
        'playlists': PlaylistListSerializer(playlists, many=True).data,
        'genres_with_movies': genres_with_movies,
    })


@api_view(['POST'])
def increment_like(request, pk):
    try:
        movie = Movie.objects.get(pk=pk, is_active=True)
    except Movie.DoesNotExist:
        return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)

    Movie.objects.filter(pk=pk).update(like_count=F('like_count') + 1)
    movie.refresh_from_db()
    return Response({'like_count': movie.like_count})


# ══════════════════════════════════════
# Reviews
# ══════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def movie_reviews(request, pk):
    """Get all reviews for a movie."""
    reviews = Review.objects.filter(movie_id=pk, is_active=True)
    sort = request.GET.get('sort', '-created_at')
    if sort == '-likes':
        reviews = reviews.order_by('-likes', '-created_at')
    elif sort == '-rating':
        reviews = reviews.order_by('-rating', '-created_at')
    elif sort == 'rating':
        reviews = reviews.order_by('rating', '-created_at')
    else:
        reviews = reviews.order_by('-created_at')

    # Calculate stats
    stats = Review.objects.filter(movie_id=pk, is_active=True).aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )

    # Rating distribution
    distribution = {}
    for i in range(1, 11):
        distribution[str(i)] = Review.objects.filter(
            movie_id=pk, is_active=True, rating__gte=i, rating__lt=i+1
        ).count()

    return Response({
        'reviews': ReviewSerializer(reviews, many=True).data,
        'stats': {
            'average_rating': round(stats['avg_rating'] or 0, 1),
            'total_reviews': stats['total_reviews'] or 0,
            'distribution': distribution,
        }
    })


@api_view(['POST'])
def create_review(request):
    """Create or update a review for a movie."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = ReviewCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        movie = Movie.objects.get(id=serializer.validated_data['movie_id'], is_active=True)
    except Movie.DoesNotExist:
        return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)

    review, created = Review.objects.update_or_create(
        movie=movie,
        user_id=payload['user_id'],
        defaults={
            'username': payload.get('username', ''),
            'rating': serializer.validated_data['rating'],
            'title': serializer.validated_data.get('title', ''),
            'content': serializer.validated_data.get('content', ''),
            'contains_spoilers': serializer.validated_data.get('contains_spoilers', False),
        }
    )

    # Recalculate movie average rating
    avg = Review.objects.filter(movie=movie, is_active=True).aggregate(avg=Avg('rating'))['avg']
    if avg:
        Movie.objects.filter(id=movie.id).update(rating=round(avg, 1))

    # Send notification for new review (fire-and-forget)
    if created:
        try:
            from shared.service_client import send_notification
            # Notify admins about new review (user_id=0 = broadcast/admin)
            send_notification(
                0,
                '📝 New Review',
                f'{payload.get("username", "Someone")} reviewed "{movie.title}" — {serializer.validated_data["rating"]}/10',
                'new_review',
                f'/movie/{movie.slug}/',
            )
        except Exception: pass

    return Response({
        'review': ReviewSerializer(review).data,
        'created': created,
        'message': 'Review submitted!' if created else 'Review updated!',
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_review(request, pk):
    """Delete a review (owner or admin)."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        review = Review.objects.get(pk=pk)
    except Review.DoesNotExist:
        return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

    if review.user_id != payload['user_id'] and not payload.get('is_admin'):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    movie = review.movie
    review.is_active = False
    review.save()

    # Recalculate movie average rating
    avg = Review.objects.filter(movie=movie, is_active=True).aggregate(avg=Avg('rating'))['avg']
    Movie.objects.filter(id=movie.id).update(rating=round(avg or 0, 1))

    return Response({'message': 'Review deleted'})


@api_view(['POST'])
def like_review(request, pk):
    """Like a review."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        review = Review.objects.get(pk=pk, is_active=True)
    except Review.DoesNotExist:
        return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

    Review.objects.filter(pk=pk).update(likes=F('likes') + 1)
    review.refresh_from_db()
    return Response({'likes': review.likes})


@api_view(['GET'])
def user_reviews(request):
    """Get current user's reviews."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    reviews = Review.objects.filter(user_id=payload['user_id'], is_active=True)
    return Response(ReviewSerializer(reviews, many=True).data)


# ══════════════════════════════════════
# Admin Stats
# ══════════════════════════════════════

@api_view(['GET'])
def admin_stats(request):
    if not require_admin(request):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    total_movies = Movie.objects.filter(is_active=True).count()
    total_genres = Genre.objects.count()
    total_categories = Category.objects.filter(is_active=True).count()
    total_playlists = Playlist.objects.count()
    featured_count = Movie.objects.filter(is_active=True, is_featured=True).count()

    return Response({
        'total_movies': total_movies,
        'total_genres': total_genres,
        'total_categories': total_categories,
        'total_playlists': total_playlists,
        'featured_count': featured_count,
    })
