import glob
import re

dockerfiles = glob.glob('*/Dockerfile')

for path in dockerfiles:
    with open(path, 'r') as f:
        content = f.read()
    
    # replace the long CMD with simple gunicorn wsgi
    # find the project name
    match = re.search(r'([a-z_]+_project)\.asgi', content)
    if not match:
        match = re.search(r'([a-z_]+_project)\.wsgi', content)
    
    if match:
        project = match.group(1)
        # We need to keep python manage.py migrate (and seed_users if present)
        # So let's extract everything before gunicorn
        pre_cmd = re.search(r'CMD \["sh", "-c", "(.*?gunicorn)', content)
        if pre_cmd:
            pre_str = pre_cmd.group(1).replace('gunicorn', '').strip()
            if pre_str.endswith('&&'):
                pre_str = pre_str[:-2].strip()
            
            new_cmd = f'CMD ["sh", "-c", "{pre_str} && gunicorn --bind 0.0.0.0:${{PORT:-8000}} {project}.wsgi:application"]\n'
            
            content = re.sub(r'CMD \["sh", "-c".*', new_cmd, content)
            
            with open(path, 'w') as f:
                f.write(content)
            print(f"Fixed {path} with {project}.wsgi")
        else:
            print(f"Skipped {path} no gunicorn found")
    else:
        print(f"Skipped {path} no project found")

