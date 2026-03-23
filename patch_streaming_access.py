with open('streaming_service/streaming/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

import_statement = "import requests\n"

access_check_code = """
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

"""

# Insert import if missing
if "import requests" not in content:
    content = content.replace("import uuid, os, sys", "import uuid, os, sys\nimport requests")

# Inject access check before creating stream session
if "is_admin = payload.get('is_admin', False)" not in content:
    content = content.replace(
        "# Create stream session",
        access_check_code + "\n    # Create stream session"
    )

with open('streaming_service/streaming/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
