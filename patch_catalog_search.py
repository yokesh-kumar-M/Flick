import re

with open('catalog_service/catalog/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

import_statement = "from .search_engine import search_movies_es, sync_movie_to_es\n"
if "search_movies_es" not in content:
    content = content.replace("from shared.jwt_utils import decode_token", "from shared.jwt_utils import decode_token\n" + import_statement)

search_patch = """@api_view(['GET'])
@permission_classes([AllowAny])
def search(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return Response({'results': [], 'query': query})

    # Try high-speed Elasticsearch first
    es_results = search_movies_es(query)
    
    if es_results is not None:
        return Response({
            'results': es_results, # Already formatted
            'query': query,
            'total': len(es_results),
            'source': 'elasticsearch'
        })
        
    # Fallback to slow database query if ES fails or is offline
    movies = Movie.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(director__icontains=query) |
        Q(cast__icontains=query) |
        Q(tags__icontains=query),
        is_active=True
    ).distinct()[:30]

    return Response({
        'results': MovieListSerializer(movies, many=True).data,
        'query': query,
        'total': movies.count() if hasattr(movies, 'count') else len(movies),
        'source': 'database'
    })
"""

content = re.sub(r"@api_view\(\['GET'\]\)\n@permission_classes\(\[AllowAny\]\)\ndef search\(request\):[\s\S]*?(?=\n# ══════════════════════════════════════\n# Trending)", search_patch, content)

# Let's also patch the movie_create to automatically sync to ES
movie_create_patch = """
    movie = serializer.save()
    
    # Sync to Elasticsearch in background
    import threading
    threading.Thread(target=sync_movie_to_es, args=(movie,)).start()
    
    return Response(MovieDetailSerializer(movie).data, status=status.HTTP_201_CREATED)
"""
content = content.replace("""    movie = serializer.save()
    return Response(MovieDetailSerializer(movie).data, status=status.HTTP_201_CREATED)""", movie_create_patch)

with open('catalog_service/catalog/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
