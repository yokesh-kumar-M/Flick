import re

for svc, seed_cmd in [('auth_service', 'seed_users'), ('catalog_service', 'seed_catalog')]:
    path = f"{svc}/Dockerfile"
    with open(path, 'r') as f:
        content = f.read()
    
    # Remove RUN seed_...
    content = re.sub(f'RUN python manage\.py {seed_cmd}\n', '', content)
    
    # modify CMD to include seed
    # currently it looks like: CMD ["sh", "-c", "python manage.py migrate && gunicorn ..."]
    content = re.sub(
        r'CMD \["sh", "-c", "python manage\.py migrate && gunicorn',
        f'CMD ["sh", "-c", "python manage.py migrate && python manage.py {seed_cmd} && gunicorn',
        content
    )
    with open(path, 'w') as f:
        f.write(content)
    print(f"Fixed {path}")
