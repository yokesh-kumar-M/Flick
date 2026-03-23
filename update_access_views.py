import re

with open('access_service/access/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add MovieHash to imports
content = content.replace("from .models import AccessRequest, AccessGrant", "from .models import AccessRequest, AccessGrant, MovieHash")

# Update approve_access
approve_access_orig = """    # Create access grant
    AccessGrant.objects.update_or_create(
        user_id=access_req.user_id,
        movie_id=access_req.movie_id,
        defaults={
            'access_code': code,
            'is_active': True,
            'expires_at': access_req.expires_at,
        }
    )

    # Send notification (fire-and-forget)
    try:
        from shared.service_client import send_notification
        send_notification(
            access_req.user_id,
            '🎬 Access Granted!',
            f'Your access to "{access_req.movie_title}" has been approved. Enjoy watching!',
            'access_approved',
            f'/movie/movie-{access_req.movie_id}/',
        )
    except Exception: pass"""

approve_access_new = """    # Generate the Hash for the user to unlock
    movie_hash = MovieHash.objects.create(
        hash_code=code,
        movie_id=access_req.movie_id,
        movie_title=access_req.movie_title,
        user_id=access_req.user_id
    )

    # Send Hash to User's Inbox
    try:
        from shared.service_client import send_notification
        send_notification(
            access_req.user_id,
            '🎬 Movie Access Key Generated!',
            f'Your payment for "{access_req.movie_title}" was successful.\n\nYour Unlock Hash: {code}\n\nPlease enter this Hash on the movie page to unlock it forever.',
            'access_approved',
            f'/movie/{access_req.movie_id}/',
        )
    except Exception: pass"""

content = content.replace(approve_access_orig, approve_access_new)

# Add new endpoints: unlock_movie and generate_hash_manual
new_endpoints = """

@api_view(['POST'])
def unlock_movie(request):
    \"\"\"User submits a Hash to permanently unlock a movie.\"\"\"
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    user_id = payload['user_id']
    hash_code = request.data.get('hash_code', '').strip()

    if not hash_code:
        return Response({'error': 'Hash code is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        movie_hash = MovieHash.objects.get(hash_code=hash_code)
    except MovieHash.DoesNotExist:
        return Response({'error': 'Invalid Hash Code'}, status=status.HTTP_404_NOT_FOUND)

    if movie_hash.is_used:
        return Response({'error': 'This Hash has already been used'}, status=status.HTTP_400_BAD_REQUEST)
        
    if movie_hash.user_id != user_id:
        return Response({'error': 'This Hash belongs to another user'}, status=status.HTTP_403_FORBIDDEN)

    # Unlock the movie
    movie_hash.is_used = True
    movie_hash.used_at = timezone.now()
    movie_hash.save()

    AccessGrant.objects.update_or_create(
        user_id=user_id,
        movie_id=movie_hash.movie_id,
        defaults={
            'access_code': hash_code,
            'is_active': True,
        }
    )

    return Response({
        'message': 'Movie unlocked successfully forever!',
        'movie_id': movie_hash.movie_id
    })


@api_view(['POST'])
def generate_hash_manual(request):
    \"\"\"Admin manually generates a Hash for a user without a prior request.\"\"\"
    payload = get_user_payload(request)
    if not payload or not payload.get('is_admin'):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    user_id = request.data.get('user_id')
    movie_id = request.data.get('movie_id')
    movie_title = request.data.get('movie_title', f'Movie {movie_id}')

    if not user_id or not movie_id:
        return Response({'error': 'user_id and movie_id are required'}, status=status.HTTP_400_BAD_REQUEST)

    code, timestamp = generate_access_code(user_id, movie_id)
    
    movie_hash = MovieHash.objects.create(
        hash_code=code,
        movie_id=movie_id,
        movie_title=movie_title,
        user_id=user_id
    )

    # Send directly to Inbox
    try:
        from shared.service_client import send_notification
        send_notification(
            user_id,
            '🎁 Special Access Key Gifted!',
            f'An admin has gifted you access to "{movie_title}".\n\nYour Unlock Hash: {code}\n\nEnter this on the movie page to unlock it!',
            'info',
            f'/movie/{movie_id}/',
        )
    except Exception: pass

    return Response({
        'message': 'Hash generated and sent to user inbox',
        'hash_code': code
    })
"""

if "def unlock_movie(request):" not in content:
    content += new_endpoints

with open('access_service/access/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
