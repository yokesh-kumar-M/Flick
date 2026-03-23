import glob
import re

dockerfiles = glob.glob('*/Dockerfile')

for path in dockerfiles:
    with open(path, 'r') as f:
        content = f.read()
    
    # Remove RUN python manage.py migrate
    content = re.sub(r'RUN python manage\.py migrate\n', '', content)
    
    # Modify CMD to include migrate
    content = re.sub(
        r'CMD \["gunicorn", (.*?)\]',
        r'CMD ["sh", "-c", "python manage.py migrate && gunicorn \1"]',
        content
    )
    
    with open(path, 'w') as f:
        f.write(content)
    print(f"Fixed {path}")
