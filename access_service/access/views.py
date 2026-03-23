from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from .models import AccessRequest, AccessGrant, MovieHash
from .serializers import (
    AccessRequestSerializer, AccessRequestCreateSerializer,
    AccessGrantSerializer, VerifyCodeSerializer
)
import sys, os, requests, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.jwt_utils import decode_token, generate_access_code

logger = logging.getLogger(__name__)


# Auth service URL for user lookups
AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:8001/api/auth')


def get_raw_token(request):
    """Extract raw JWT token string from request."""
    return request.COOKIES.get('access_token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')


def get_user_payload(request):
    token = get_raw_token(request)
    return decode_token(token) if token else None


def check_user_privileges(user_id, token):
    """Query auth service to check if user is admin or has super access."""
    try:
        resp = requests.get(
            f'{AUTH_SERVICE_URL}/profile/',
            headers={'Authorization': f'Bearer {token}'},
            timeout=3
        )
        if resp.status_code == 200:
            user_data = resp.json()
            return {
                'is_admin': user_data.get('is_admin', False),
                'has_super_access': user_data.get('has_super_access', False),
                'email': user_data.get('email', ''),
            }
    except Exception:
        pass
    return {'is_admin': False, 'has_super_access': False, 'email': ''}


@api_view(['GET'])
def check_access(request, movie_id):
    """Check if user can access a movie (admin/super users get immediate access)."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'has_access': False, 'reason': 'not_authenticated'})

    user_id = payload['user_id']
    
    # Check if admin directly from JWT token (no HTTP call needed)
    is_admin = payload.get('is_admin', False)
    if is_admin:
        return Response({
            'has_access': True,
            'reason': 'admin',
            'requires_payment': False,
            'access_type': 'unlimited'
        })
    
    # For super_access, we need to check the auth service since it can change after login
    token = get_raw_token(request)
    privileges = check_user_privileges(user_id, token)
    
    if privileges['has_super_access']:
        return Response({
            'has_access': True,
            'reason': 'super_access',
            'requires_payment': False,
            'access_type': 'unlimited'
        })

    # Check for existing grant
    grant = AccessGrant.objects.filter(user_id=user_id, movie_id=movie_id, is_active=True).first()
    if grant:
        return Response({
            'has_access': True,
            'reason': 'granted',
            'access_code': grant.access_code,
            'requires_payment': False,
        })

    # Check for pending request
    access_req = AccessRequest.objects.filter(user_id=user_id, movie_id=movie_id).first()
    if access_req:
        if access_req.status == 'approved':
            return Response({
                'has_access': True,
                'reason': 'approved',
                'access_code': access_req.access_code,
                'requires_payment': False,
            })
        elif access_req.status == 'pending':
            return Response({
                'has_access': False,
                'reason': 'pending_approval',
                'requires_payment': access_req.payment_status == 'pending',
                'payment_status': access_req.payment_status,
                'request_id': access_req.id,
            })

    # No access
    return Response({
        'has_access': False,
        'reason': 'no_request',
        'requires_payment': True,  # Regular users need to pay
    })


@api_view(['POST'])
def request_access(request):
    """User requests access to a movie."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = AccessRequestCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    movie_id = serializer.validated_data['movie_id']
    user_id = payload['user_id']
    
    # Check if admin directly from JWT token
    is_admin = payload.get('is_admin', False)
    
    # For super_access, check auth service
    has_super_access = False
    user_email = ''
    if not is_admin:
        token = get_raw_token(request)
        privileges = check_user_privileges(user_id, token)
        has_super_access = privileges['has_super_access']
        user_email = privileges['email']

    # Admin/super users don't need to request — create auto-approved grant
    if is_admin or has_super_access:
        code, timestamp = generate_access_code(user_id, movie_id)
        grant, created = AccessGrant.objects.get_or_create(
            user_id=user_id,
            movie_id=movie_id,
            defaults={'access_code': code}
        )
        return Response({
            'message': 'Unlimited access granted',
            'access_code': grant.access_code,
            'access_type': 'admin' if is_admin else 'super_access',
        })

    # Check if already has active grant
    if AccessGrant.objects.filter(user_id=user_id, movie_id=movie_id, is_active=True).exists():
        grant = AccessGrant.objects.get(user_id=user_id, movie_id=movie_id)
        return Response({
            'message': 'You already have access to this movie',
            'access_code': grant.access_code,
            'status': 'approved'
        })

    # Check if pending request exists
    existing = AccessRequest.objects.filter(user_id=user_id, movie_id=movie_id).first()
    if existing:
        if existing.status == 'pending':
            return Response({
                'message': 'Access request already pending',
                'request': AccessRequestSerializer(existing).data
            })
        elif existing.status == 'approved':
            return Response({
                'message': 'Access already approved',
                'access_code': existing.access_code,
                'request': AccessRequestSerializer(existing).data
            })
        elif existing.status == 'denied':
            # Allow re-request
            existing.status = 'pending'
            existing.reason = serializer.validated_data.get('reason', '')
            existing.save()
            return Response({
                'message': 'Access re-requested',
                'request': AccessRequestSerializer(existing).data
            })

    # Regular user — create request requiring payment
    access_req = AccessRequest.objects.create(
        user_id=user_id,
        username=payload.get('username', ''),
        user_email=user_email,
        movie_id=movie_id,
        movie_title=serializer.validated_data.get('movie_title', ''),
        reason=serializer.validated_data.get('reason', ''),
        payment_status='pending',  # Requires payment
    )

    return Response({
        'message': 'Access requested — payment required',
        'request': AccessRequestSerializer(access_req).data,
        'requires_payment': True,
        'request_id': access_req.id,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def approve_access(request, pk):
    """Admin approves an access request."""
    payload = get_user_payload(request)
    if not payload or not payload.get('is_admin'):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        access_req = AccessRequest.objects.get(pk=pk)
    except AccessRequest.DoesNotExist:
        return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)

    if access_req.status != 'pending':
        return Response({'error': f'Request is already {access_req.status}'}, status=status.HTTP_400_BAD_REQUEST)

    # Generate access code
    code, timestamp = generate_access_code(access_req.user_id, access_req.movie_id)

    access_req.status = 'approved'
    access_req.access_code = code
    access_req.code_timestamp = timestamp
    access_req.admin_note = request.data.get('admin_note', '')
    access_req.expires_at = timezone.now() + timedelta(days=30)
    access_req.save()

    # Generate the Hash for the user to unlock
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
            f'''Your payment for "{access_req.movie_title}" was successful.

Your Unlock Hash: {code}

Please enter this Hash on the movie page to unlock it forever.','''
            'access_approved',
            f'/movie/{access_req.movie_id}/',
        )
    except Exception: pass

    return Response({
        'message': 'Access approved',
        'access_code': code,
        'request': AccessRequestSerializer(access_req).data
    })


@api_view(['POST'])
def deny_access(request, pk):
    """Admin denies an access request."""
    payload = get_user_payload(request)
    if not payload or not payload.get('is_admin'):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        access_req = AccessRequest.objects.get(pk=pk)
    except AccessRequest.DoesNotExist:
        return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)

    access_req.status = 'denied'
    access_req.admin_note = request.data.get('admin_note', '')
    access_req.save()

    # Send notification
    try:
        from shared.service_client import send_notification
        send_notification(
            access_req.user_id,
            'Access Denied',
            f'Your access request for "{access_req.movie_title}" was denied.{" Reason: " + access_req.admin_note if access_req.admin_note else ""}',
            'access_denied',
        )
    except Exception: pass

    return Response({
        'message': 'Access denied',
        'request': AccessRequestSerializer(access_req).data
    })


@api_view(['POST'])
def verify_code(request):
    """Verify an access code for a movie."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = VerifyCodeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    movie_id = serializer.validated_data['movie_id']
    code = serializer.validated_data['access_code'].upper()
    user_id = payload['user_id']

    # Check grant
    grant = AccessGrant.objects.filter(
        user_id=user_id, movie_id=movie_id, is_active=True
    ).first()

    if not grant:
        return Response({'valid': False, 'error': 'No access grant found'}, status=status.HTTP_403_FORBIDDEN)

    if grant.access_code != code:
        return Response({'valid': False, 'error': 'Invalid access code'}, status=status.HTTP_403_FORBIDDEN)

    if grant.expires_at and grant.expires_at < timezone.now():
        grant.is_active = False
        grant.save()
        return Response({'valid': False, 'error': 'Access expired'}, status=status.HTTP_403_FORBIDDEN)

    return Response({'valid': True, 'message': 'Access verified'})


@api_view(['GET'])
def my_requests(request):
    """Get current user's access requests."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    requests_list = AccessRequest.objects.filter(user_id=payload['user_id'])
    return Response(AccessRequestSerializer(requests_list, many=True).data)


@api_view(['GET'])
def my_grants(request):
    """Get current user's active access grants."""
    payload = get_user_payload(request)
    if not payload:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    grants = AccessGrant.objects.filter(user_id=payload['user_id'], is_active=True)
    return Response(AccessGrantSerializer(grants, many=True).data)


@api_view(['GET'])
def pending_requests(request):
    """Admin: Get all pending access requests."""
    payload = get_user_payload(request)
    if not payload or not payload.get('is_admin'):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    requests_list = AccessRequest.objects.filter(status='pending')
    return Response(AccessRequestSerializer(requests_list, many=True).data)


@api_view(['GET'])
def all_requests(request):
    """Admin: Get all access requests."""
    payload = get_user_payload(request)
    if not payload or not payload.get('is_admin'):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    status_filter = request.GET.get('status')
    requests_list = AccessRequest.objects.all()
    if status_filter:
        requests_list = requests_list.filter(status=status_filter)

    return Response(AccessRequestSerializer(requests_list, many=True).data)


# ══════════════════════════════════════
# Payment Processing
# ══════════════════════════════════════

@api_view(['POST'])
@permission_classes([AllowAny])  # Webhook from payment provider
def payment_webhook(request):
    """Webhook endpoint for payment confirmations (Stripe/PayPal/etc)."""
    # In production, verify webhook signature here
    payment_id = request.data.get('payment_id')
    request_id = request.data.get('request_id')
    status_received = request.data.get('status', 'completed')

    if not payment_id or not request_id:
        return Response({'error': 'Missing payment_id or request_id'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        access_req = AccessRequest.objects.get(id=request_id)
    except AccessRequest.DoesNotExist:
        return Response({'error': 'Access request not found'}, status=status.HTTP_404_NOT_FOUND)

    if status_received == 'completed':
        access_req.payment_status = 'completed'
        access_req.payment_id = payment_id
        access_req.status = 'approved'  # Auto-approve after payment

        # Generate access code
        code, timestamp = generate_access_code(access_req.user_id, access_req.movie_id)
        access_req.access_code = code
        access_req.code_timestamp = timestamp
        access_req.save()

        # Create access grant
        AccessGrant.objects.get_or_create(
            user_id=access_req.user_id,
            movie_id=access_req.movie_id,
            defaults={'access_code': code}
        )

        # Send email with access code
        send_access_code_email(access_req)

        return Response({
            'message': 'Payment processed and access granted',
            'access_code': code,
        })
    else:
        access_req.payment_status = 'failed'
        access_req.payment_id = payment_id
        access_req.save()
        return Response({'message': 'Payment failed', 'status': 'failed'})


@api_view(['POST'])
def confirm_payment_manual(request, request_id):
    """Admin manually confirms payment and grants access."""
    payload = get_user_payload(request)
    if not payload or not payload.get('is_admin'):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        access_req = AccessRequest.objects.get(id=request_id)
    except AccessRequest.DoesNotExist:
        return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)

    access_req.payment_status = 'completed'
    access_req.status = 'approved'
    access_req.payment_id = f"MANUAL_{timezone.now().strftime('%Y%m%d%H%M%S')}"

    # Generate access code
    code, timestamp = generate_access_code(access_req.user_id, access_req.movie_id)
    access_req.access_code = code
    access_req.code_timestamp = timestamp
    access_req.save()

    # Create access grant
    AccessGrant.objects.get_or_create(
        user_id=access_req.user_id,
        movie_id=access_req.movie_id,
        defaults={'access_code': code}
    )

    # Send email
    send_access_code_email(access_req)

    return Response({
        'message': 'Payment confirmed and access granted',
        'access_code': code,
        'request': AccessRequestSerializer(access_req).data,
    })


# ══════════════════════════════════════
# Email Functionality
# ══════════════════════════════════════


def send_access_code_email(access_req):
    """Send access code to user via email."""
    if not access_req.user_email:
        logger.warning(f"No email for user {access_req.user_id}, skipping email")
        return False

    subject = f"🎬 Your Access Code for {access_req.movie_title}"
    message = f"""
Hello {access_req.username},

Your payment has been processed successfully! You now have access to:

📽️ Movie: {access_req.movie_title}
🔑 Access Code: {access_req.access_code}

You can now watch this movie anytime. Enjoy!

— The Flick Team
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[access_req.user_email],
            fail_silently=False,
        )
        access_req.email_sent = True
        access_req.save()
        logger.info(f"Email sent to {access_req.user_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {access_req.user_email}: {e}")
        return False


@api_view(['POST'])
def resend_access_code(request, request_id):
    """Admin can resend access code email."""
    payload = get_user_payload(request)
    if not payload or not payload.get('is_admin'):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        access_req = AccessRequest.objects.get(id=request_id)
    except AccessRequest.DoesNotExist:
        return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)

    if access_req.status != 'approved' or not access_req.access_code:
        return Response({'error': 'Request must be approved with access code'}, status=status.HTTP_400_BAD_REQUEST)

    success = send_access_code_email(access_req)
    if success:
        return Response({'message': f'Access code resent to {access_req.user_email}'})
    else:
        return Response({'error': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def unlock_movie(request):
    """User submits a Hash to permanently unlock a movie."""
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
    """Admin manually generates a Hash for a user without a prior request."""
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
            f'''An admin has gifted you access to "{movie_title}".

Your Unlock Hash: {code}

Enter this on the movie page to unlock it!''',
            'info',
            f'/movie/{movie_id}/',
        )
    except Exception: pass

    return Response({
        'message': 'Hash generated and sent to user inbox',
        'hash_code': code
    })
