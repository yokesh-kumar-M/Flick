import re
with open('auth_service/authentication/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "access_token = create_access_token(user.id, user.username, user.is_admin)",
    "access_token = create_access_token(user.id, user.username, user.is_admin, user.has_super_access)"
)

with open('auth_service/authentication/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
