with open('shared/jwt_utils.py', 'r') as f:
    content = f.read()

content = content.replace(
    "def create_access_token(user_id, username, is_admin=False):",
    "def create_access_token(user_id, username, is_admin=False, has_super_access=False):"
)
content = content.replace(
    "'is_admin': is_admin,",
    "'is_admin': is_admin,\n        'has_super_access': has_super_access,"
)

with open('shared/jwt_utils.py', 'w') as f:
    f.write(content)
