import os
import glob
import re

directories = ['auth_service', 'catalog_service', 'access_service', 'streaming_service', 'recommendation_service', 'notification_service', 'gateway']

for d in directories:
    dockerfile_path = os.path.join(d, 'Dockerfile')
    if not os.path.exists(dockerfile_path):
        continue
        
    with open(dockerfile_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Replace requirements.txt copy
    content = content.replace('COPY requirements.txt .', f'COPY {d}/requirements.txt .')
    
    # Add WORKDIR before EXPOSE or CMD
    if 'WORKDIR /app/' not in content:
        # Find the line with COPY . .
        lines = content.split('\n')
        new_lines = []
        app_copied = False
        for line in lines:
            if 'COPY . .' in line:
                new_lines.append(line)
                new_lines.append(f'WORKDIR /app/{d}')
                app_copied = True
            elif 'WORKDIR /app/auth_service' in line and d == 'auth_service':
                # Skip duplicate if already added
                pass
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)
        
    with open(dockerfile_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Updated Dockerfiles")
