with open('nginx/nginx.conf', 'r') as f:
    content = f.read()

cdn_rules = """
        # Cloudflare CDN Video Edge Caching Rules
        location ~* \.m3u8$ {
            proxy_pass http://gateway_backend;
            proxy_set_header Host $host;
            
            # Do not cache playlists, they might update (especially for live streams)
            add_header Cache-Control "no-cache, no-store, must-revalidate";
            add_header Pragma "no-cache";
            add_header Expires 0;
            
            # Ensure CORS is allowed so players can fetch it
            add_header Access-Control-Allow-Origin "*";
        }

        location ~* \.ts$ {
            proxy_pass http://gateway_backend;
            proxy_set_header Host $host;
            
            # Tell Cloudflare to cache these chunks for a year!
            expires 1y;
            add_header Cache-Control "public, max-age=31536000, immutable";
            add_header Access-Control-Allow-Origin "*";
        }

        location / {"""

if "Cloudflare CDN Video Edge Caching Rules" not in content:
    content = content.replace("        location / {", cdn_rules)

with open('nginx/nginx.conf', 'w') as f:
    f.write(content)
