import glob
import re

dockerfiles = glob.glob('*/Dockerfile')

for path in dockerfiles:
    with open(path, 'r') as f:
        content = f.read()
    
    # We need to construct a proper shell command string
    # E.g. CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 --workers 2 ... application"]
    
    # Find the port and application from the previous incorrect CMD
    # It might look like: CMD ["sh", "-c", "python manage.py migrate && gunicorn "--bind", "0.0.0.0:8000", ..., "gateway_project.asgi:application""]
    match = re.search(r'0\.0\.0\.0:(\d+)', content)
    port = match.group(1) if match else "8000"
    
    match2 = re.search(r'([a-z_]+_project\.asgi:application)', content)
    app = match2.group(1) if match2 else ""
    
    if not app:
        # Fallback if we didn't find the asgi
        match3 = re.search(r'([a-z_]+_project\.wsgi:application)', content)
        app = match3.group(1) if match3 else ""
        
    cmd_str = f'CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:{port} --workers 2 --threads 4 --worker-class uvicorn.workers.UvicornWorker --timeout 120 --keep-alive 5 {app}"]\n'
    
    # Replace the bad CMD line
    content = re.sub(r'CMD \["sh".*', cmd_str, content)
    
    with open(path, 'w') as f:
        f.write(content)
    print(f"Fixed {path}")
