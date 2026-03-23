import os
import glob
import re

dockerfiles = glob.glob("*/Dockerfile")
for df in dockerfiles:
    with open(df, "r") as f:
        content = f.read()
    
    # Replace standard sync workers with uvicorn async workers for immense concurrency gains
    if 'gthread' in content:
        content = content.replace(
            '--worker-class", "gthread"', 
            '--worker-class", "uvicorn.workers.UvicornWorker"'
        )
        content = content.replace(
            'wsgi:application',
            'asgi:application'
        )
    
    with open(df, "w") as f:
        f.write(content)
    print(f"Patched {df}")
