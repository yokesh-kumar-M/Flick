from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import FlickUser, WatchHistory, UserWatchlist, GenreStats
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    UserProfileUpdateSerializer, WatchHistorySerializer,
    GenreStatsSerializer, ChangePasswordSerializer, WatchlistSerializer
)
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.jwt_utils import create_access_token, create_refresh_token, decode_token, blacklist_token


def get_user_payload(request):
    """Extract and decode JWT from cookies or Authorization header."""
    token = request.COOKIES.get('access_token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
    return decode_token(token) if token else None


def get_authenticated_user(request):
    """Get the FlickUser for the current request, or None."""
    payload = get_user_payload(request)
    if not payload:
        return None, None
    try:
        return FlickUser.objects.get(id=payload['user_id']), payload
    except FlickUser.DoesNotExist:
        return None, payload


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user."""
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = FlickUser(
        username=serializer.validated_data['username'],
        email=serializer.validated_data['email'],
        display_name=serializer.validated_data.get('display_name', serializer.validated_data['username']),
    )
    user.set_password(serializer.validated_data['password'])
    user.save()

    access_token = create_access_token(user.id, user.username, user.is_admin, user.has_super_access)
    refresh_token = create_refresh_token(user.id)

    response_data = {
        'message': 'Registration successful',
        'user': UserSerializer(user).data,
        'access_token': access_token,
        'refresh_token': refresh_token,
    }

    response = Response(response_data, status=status.HTTP_201_CREATED)
    response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', path='/', max_age=1800)
    response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', path='/', max_age=86400)

    # Welcome notification
    try:
        from shared.service_client import send_notification
        send_notification(
            user.id,
            '🎬 Welcome to Flick!',
            f'Hey {user.display_name or user.username}, welcome aboard! Start exploring movies and build your watchlist.',
            'welcome',
            '/browse/',
        )
    except Exception: pass

    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Authenticate user and return JWT tokens."""
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = FlickUser.objects.get(username=serializer.validated_data['username'])
    except FlickUser.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(serializer.validated_data['password']):
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_active:
        return Response({'error': 'Account is deactivated'}, status=status.HTTP_403_FORBIDDEN)

    access_token = create_access_token(user.id, user.username, user.is_admin, user.has_super_access)
    refresh_token = create_refresh_token(user.id)

    response_data = {
        'message': 'Login successful',
        'user': UserSerializer(user).data,
        'access_token': access_token,
        'refresh_token': refresh_token,
    }

    response = Response(response_data, status=status.HTTP_200_OK)
    response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', path='/', max_age=1800)
    response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', path='/', max_age=86400)
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """Refresh access token using refresh token."""
    token = request.data.get('refresh_token') or request.COOKIES.get('refresh_token')
    if not token:
        return Response({'error': 'Refresh token required'}, status=status.HTTP_400_BAD_REQUEST)

    payload = decode_token(token)
    if not payload or payload.get('type') != 'refresh':
        return Response({'error': 'Invalid or expired refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        user = FlickUser.objects.get(id=payload['user_id'])
    except FlickUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    access_token = create_access_token(user.id, user.username, user.is_admin, user.has_super_access)
    new_refresh_token = create_refresh_token(user.id)

    response = Response({
        'access_token': access_token,
        'refresh_token': new_refresh_token,
    })
    response.set_cookie('access_token', access_token, httponly=True, samesite='Lax', path='/', max_age=1800)
    response.set_cookie('refresh_token', new_refresh_token, httponly=True, samesite='Lax', path='/', max_age=86400)
    return response


@api_view(['POST'])
def logout(request):
    """Clear authentication cookies and blacklist current tokens."""
    # Blacklist access token
    access_token = request.COOKIES.get('access_token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
    if access_token:
        blacklist_token(access_token)

    # Blacklist refresh token
    refresh = request.COOKIES.get('refresh_token') or request.data.get('refresh_token')
    if refresh:
        blacklist_token(refresh)

    response = Response({'message': 'Logged out successfully'})
    response.delete_cookie('access_token', path='/', samesite='Lax')
    response.delete_cookie('refresh_token', path='/', samesite='Lax')
    return response


@api_view(['GET'])
def get_profile(request):
    """Get current user's profile."""
    user, payload = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(UserSerializer(user).data)


@api_view(['PUT', 'PATCH'])
def update_profile(request):
    """Update current user's profile."""
    user, payload = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = UserProfileUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Validate email uniqueness (excluding current user)
    new_email = serializer.validated_data.get('email')
    if new_email and new_email != user.email:
        if FlickUser.objects.filter(email=new_email).exclude(id=user.id).exists():
            return Response({'email': ['Email already in use.']}, status=status.HTTP_400_BAD_REQUEST)

    for key, value in serializer.validated_data.items():
        setattr(user, key, value)
    user.save()

    return Response(UserSerializer(user).data)


@api_view(['POST'])
def change_password(request):
    """Change user's password."""
    user, payload = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = ChangePasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(serializer.validated_data['old_password']):
        return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(serializer.validated_data['new_password'])
    user.save()

    return Response({'message': 'Password changed successfully'})


@api_view(['GET'])
def watch_history(request):
    """Get user's watch history."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    history = WatchHistory.objects.filter(user_id=payload['user_id'])[:50]
    return Response(WatchHistorySerializer(history, many=True).data)


@api_view(['POST'])
def update_watch_progress(request):
    """Update watch progress for a movie."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    movie_id = request.data.get('movie_id')
    progress = request.data.get('progress', 0)
    last_position = request.data.get('last_position', 0)
    duration = request.data.get('duration', 0)
    movie_title = request.data.get('movie_title', '')
    movie_poster = request.data.get('movie_poster', '')

    if not movie_id:
        return Response({'error': 'movie_id required'}, status=status.HTTP_400_BAD_REQUEST)

    history, created = WatchHistory.objects.update_or_create(
        user_id=payload['user_id'],
        movie_id=movie_id,
        defaults={
            'progress': progress,
            'last_position': last_position,
            'duration': duration,
            'movie_title': movie_title,
            'movie_poster': movie_poster,
        }
    )

    return Response(WatchHistorySerializer(history).data)


@api_view(['GET'])
def continue_watching(request):
    """Get movies the user hasn't finished watching."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    history = WatchHistory.objects.filter(
        user_id=payload['user_id'],
        progress__gt=0,
        progress__lt=95
    ).order_by('-watched_at')[:20]
    return Response(WatchHistorySerializer(history, many=True).data)


@api_view(['GET'])
def genre_stats(request):
    """Get user's genre statistics."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    stats = GenreStats.objects.filter(user_id=payload['user_id'])
    return Response(GenreStatsSerializer(stats, many=True).data)


@api_view(['GET'])
def user_stats(request):
    """Get user's overall watch statistics."""
    user, payload = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    total_watched = WatchHistory.objects.filter(user_id=user.id).count()
    completed = WatchHistory.objects.filter(user_id=user.id, progress__gte=95).count()
    genre_breakdown = list(GenreStats.objects.filter(user_id=user.id).values('genre', 'watch_count', 'total_minutes'))

    return Response({
        'user': UserSerializer(user).data,
        'total_watched': total_watched,
        'completed': completed,
        'total_watch_time_hours': round(user.total_watch_time / 60, 1),
        'genre_breakdown': genre_breakdown,
    })


@api_view(['GET'])
def validate_token(request):
    """Validate a JWT token (used by other services)."""
    token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
    if not token:
        token = request.GET.get('token', '')

    payload = decode_token(token)
    if not payload:
        return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({
        'valid': True,
        'user_id': payload.get('user_id'),
        'username': payload.get('username'),
        'is_admin': payload.get('is_admin', False),
    })


@api_view(['GET'])
def list_users(request):
    """Admin: List all users."""
    payload = get_user_payload(request)
    if not payload or not payload.get('is_admin'):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    return Response(UserSerializer(FlickUser.objects.all(), many=True).data)


@api_view(['POST'])
def toggle_admin(request, user_id):
    """Admin: Toggle admin status for a user."""
    payload = get_user_payload(request)
    if not payload or not payload.get('is_admin'):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = FlickUser.objects.get(id=user_id)
    except FlickUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    user.is_admin = not user.is_admin
    user.save()
    return Response({'message': f'User {user.username} admin status: {user.is_admin}', 'user': UserSerializer(user).data})


@api_view(['POST'])
def ban_user(request, user_id):
    """Admin: Ban/unban a user."""
    payload = get_user_payload(request)
    if not payload or not payload.get('is_admin'):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = FlickUser.objects.get(id=user_id)
    except FlickUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    user.is_active = not user.is_active
    user.save()
    action = 'unbanned' if user.is_active else 'banned'
    return Response({'message': f'User {user.username} {action}', 'user': UserSerializer(user).data})


@api_view(['POST'])
def toggle_super_access(request, user_id):
    """Admin: Grant/revoke super access for a user."""
    payload = get_user_payload(request)
    if not payload or not payload.get('is_admin'):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = FlickUser.objects.get(id=user_id)
    except FlickUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    user.has_super_access = not user.has_super_access
    user.save()
    status_msg = 'granted' if user.has_super_access else 'revoked'
    return Response({
        'message': f'Super access {status_msg} for {user.username}',
        'user': UserSerializer(user).data
    })


@api_view(['GET'])
def admin_stats(request):
    """Admin: Get platform statistics."""
    payload = get_user_payload(request)
    if not payload or not payload.get('is_admin'):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    total_users = FlickUser.objects.count()
    active_users = FlickUser.objects.filter(is_active=True).count()
    admin_users = FlickUser.objects.filter(is_admin=True).count()
    total_watch_history = WatchHistory.objects.count()

    return Response({
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'total_watch_history': total_watch_history,
    })


# ══════════════════════════════════════
# Avatar Upload
# ══════════════════════════════════════

@api_view(['POST'])
def upload_avatar(request):
    """Upload a profile picture for the current user."""
    user, payload = get_authenticated_user(request)
    if not user:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    if 'avatar' not in request.FILES:
        return Response({'error': 'No file provided. Send the image as avatar field.'}, status=status.HTTP_400_BAD_REQUEST)

    avatar_file = request.FILES['avatar']

    # Validate MIME type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if avatar_file.content_type not in allowed_types:
        return Response({'error': 'Only JPEG, PNG, GIF, and WebP images are allowed.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate file size (max 5 MB)
    if avatar_file.size > 5 * 1024 * 1024:
        return Response({'error': 'Image must be smaller than 5 MB.'}, status=status.HTTP_400_BAD_REQUEST)

    # Delete old avatar file from disk
    if user.avatar:
        try:
            user.avatar.delete(save=False)
        except Exception:
            pass

    user.avatar = avatar_file
    user.save()

    return Response({
        'message': 'Avatar updated successfully',
        'avatar_display': user.get_avatar_display(),
        'user': UserSerializer(user).data,
    })


# ══════════════════════════════════════
# Server-Side Watchlist
# ══════════════════════════════════════

@api_view(['GET'])
def get_watchlist(request):
    """Get user's watchlist."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    items = UserWatchlist.objects.filter(user_id=payload['user_id'])
    return Response(WatchlistSerializer(items, many=True).data)


@api_view(['POST'])
def add_to_watchlist(request):
    """Add a movie to the watchlist."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    movie_id = request.data.get('movie_id')
    if not movie_id:
        return Response({'error': 'movie_id required'}, status=status.HTTP_400_BAD_REQUEST)

    item, created = UserWatchlist.objects.get_or_create(
        user_id=payload['user_id'],
        movie_id=movie_id,
        defaults={
            'movie_title': request.data.get('movie_title', ''),
            'movie_slug': request.data.get('movie_slug', ''),
            'movie_poster': request.data.get('movie_poster', ''),
        }
    )

    if not created:
        return Response({'message': 'Already in watchlist', 'item': WatchlistSerializer(item).data})

    return Response({
        'message': 'Added to watchlist',
        'item': WatchlistSerializer(item).data,
    }, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def remove_from_watchlist(request, movie_id):
    """Remove a movie from the watchlist."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    deleted, _ = UserWatchlist.objects.filter(
        user_id=payload['user_id'], movie_id=movie_id
    ).delete()

    if deleted:
        return Response({'message': 'Removed from watchlist'})
    return Response({'message': 'Not in watchlist'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def check_watchlist(request, movie_id):
    """Check if a movie is in the user's watchlist."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'in_watchlist': False})

    exists = UserWatchlist.objects.filter(
        user_id=payload['user_id'], movie_id=movie_id
    ).exists()
    return Response({'in_watchlist': exists})

