with open('access_service/access/urls.py', 'r') as f:
    content = f.read()

new_urls = """    
    # Hash/Unlock endpoints
    path('unlock/', views.unlock_movie, name='unlock_movie'),
    path('generate_hash/', views.generate_hash_manual, name='generate_hash_manual'),
"""

content = content.replace("    # User endpoints", new_urls + "\n    # User endpoints")

with open('access_service/access/urls.py', 'w') as f:
    f.write(content)
