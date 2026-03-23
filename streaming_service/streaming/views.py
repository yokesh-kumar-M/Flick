from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from django.utils import timezone
from datetime import timedelta
from .models import TranscodeJob, StreamSession
from .serializers import TranscodeJobSerializer, StreamSessionSerializer, StartStreamSerializer
import uuid, os, sys
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.jwt_utils import decode_token, generate_signed_url
from shared.events import event_bus



def get_user_payload(request):
    token = request.COOKIES.get('access_token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
    return decode_token(token) if token else None


def get_hls_content_type(filename):
    """Return the content type for HLS files."""
    if filename.endswith('.m3u8'):
        return 'application/vnd.apple.mpegurl'
    if filename.endswith('.ts'):
        return 'video/MP2T'
    return 'application/octet-stream'


@api_view(['POST'])
def start_stream(request):
    """Start a streaming session."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = StartStreamSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    movie_id = serializer.validated_data['movie_id']

    
    is_admin = payload.get('is_admin', False)
    has_super_access = payload.get('has_super_access', False)
    
    # Fast path for admins and super users
    if not (is_admin or has_super_access):
        # Query access service to verify the user has unlocked this movie
        try:
            # We need to forward the token
            token = request.COOKIES.get('access_token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
            headers = {'Authorization': f'Bearer {token}'} if token else {}
            access_url = os.environ.get('ACCESS_SERVICE_URL', 'http://access_service:8003')
            resp = requests.get(f'{access_url}/api/access/check/{movie_id}/', headers=headers, timeout=3)
            
            if resp.status_code == 200:
                data = resp.json()
                if not data.get('has_access', False):
                    return Response({'error': 'Access Denied. You need to unlock this movie with an Access Key.'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'Failed to verify access permissions.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': f'Access verification failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # Create stream session
    session_token = str(uuid.uuid4())
    session = StreamSession.objects.create(
        user_id=payload['user_id'],
        movie_id=movie_id,
        session_token=session_token,
        quality=serializer.validated_data.get('quality', 'auto'),
    )


    # Generate signed URL for the master playlist
    playlist_path = f"/api/streaming/hls/{movie_id}/master.m3u8"
    signed_url = generate_signed_url(playlist_path)

    # Publish video_played event
    try:
        event_bus.publish('video_events', 'video_started', {
            'user_id': payload['user_id'],
            'movie_id': movie_id,
            'session_token': session_token
        })
    except Exception:
        pass


    return Response({
        'session_token': session_token,
        'playlist_url': signed_url,
        'session': StreamSessionSerializer(session).data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def serve_hls(request, movie_id, filename):
    """Serve HLS playlist or segment files."""
    media_root = os.path.join(os.path.dirname(__file__), '..', 'media')
    file_path = os.path.join(media_root, 'hls', str(movie_id), filename)

    if not os.path.exists(file_path):
        return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

    return FileResponse(open(file_path, 'rb'), content_type=get_hls_content_type(filename))


@api_view(['GET'])
@permission_classes([AllowAny])
def serve_hls_quality(request, movie_id, quality, filename):
    """Serve HLS files from quality subdirectories."""
    media_root = os.path.join(os.path.dirname(__file__), '..', 'media')
    file_path = os.path.join(media_root, 'hls', str(movie_id), quality, filename)

    if not os.path.exists(file_path):
        return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

    return FileResponse(open(file_path, 'rb'), content_type=get_hls_content_type(filename))


@api_view(['POST'])
def heartbeat(request):
    """Update stream session heartbeat."""
    session_token = request.data.get('session_token')
    if not session_token:
        return Response({'error': 'Session token required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        session = StreamSession.objects.get(session_token=session_token, is_active=True)
        session.save()  # auto_now updates last_heartbeat
        return Response({'status': 'ok'})
    except StreamSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def end_stream(request):
    """End a streaming session."""
    session_token = request.data.get('session_token')
    if not session_token:
        return Response({'error': 'Session token required'}, status=status.HTTP_400_BAD_REQUEST)


    try:
        session = StreamSession.objects.get(session_token=session_token)
        session.is_active = False
        session.save()
        
        # Publish video_ended event
        try:
            event_bus.publish('video_events', 'video_ended', {
                'user_id': session.user_id,
                'movie_id': session.movie_id,
                'session_token': session_token
            })
        except Exception:
            pass

        return Response({'status': 'ended'})

    except StreamSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def transcode(request):
    """Admin: Start a transcode job."""
    payload = get_user_payload(request)
    if not payload or not payload.get('is_admin'):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    movie_id = request.data.get('movie_id')
    source_file = request.data.get('source_file')

    if not movie_id or not source_file:
        return Response({'error': 'movie_id and source_file required'}, status=status.HTTP_400_BAD_REQUEST)

    job = TranscodeJob.objects.create(
        movie_id=movie_id,
        source_file=source_file,
    )

    # Queue the transcode task
    from .tasks import transcode_video
    transcode_video.delay(job.id)

    return Response(TranscodeJobSerializer(job).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def transcode_status(request, job_id):
    """Get transcode job status."""
    try:
        job = TranscodeJob.objects.get(pk=job_id)
        return Response(TranscodeJobSerializer(job).data)
    except TranscodeJob.DoesNotExist:
        return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def active_streams(request):
    """Admin: Get count of active streaming sessions."""
    payload = get_user_payload(request)
    if not payload or not payload.get('is_admin'):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    cutoff = timezone.now() - timedelta(minutes=2)
    count = StreamSession.objects.filter(is_active=True, last_heartbeat__gte=cutoff).count()
    return Response({'active_streams': count})
