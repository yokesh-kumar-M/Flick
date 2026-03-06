from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer, CreateNotificationSerializer
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.jwt_utils import decode_token


def get_user_payload(request):
    token = request.COOKIES.get('access_token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
    return decode_token(token) if token else None


@api_view(['GET'])
def get_notifications(request):
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    notifications = Notification.objects.filter(user_id=payload['user_id'])[:50]
    return Response(NotificationSerializer(notifications, many=True).data)


@api_view(['GET'])
def unread_count(request):
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    count = Notification.objects.filter(user_id=payload['user_id'], is_read=False).count()
    return Response({'unread_count': count})


@api_view(['POST'])
def mark_read(request, pk):
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        notification = Notification.objects.get(pk=pk, user_id=payload['user_id'])
        notification.is_read = True
        notification.save()
        return Response({'message': 'Marked as read'})
    except Notification.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def mark_all_read(request):
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    Notification.objects.filter(user_id=payload['user_id'], is_read=False).update(is_read=True)
    return Response({'message': 'All marked as read'})


@api_view(['POST'])
@permission_classes([AllowAny])
def create_notification(request):
    """Internal: Create a notification (called by other services)."""
    serializer = CreateNotificationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    notification = Notification.objects.create(**serializer.validated_data)
    return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)
