import os
from elasticsearch import Elasticsearch
from django.conf import settings

# Initialize Elasticsearch client
es_url = os.environ.get('ELASTICSEARCH_URL', 'http://elasticsearch:9200')
if 'localhost' in es_url and not os.path.exists('/.dockerenv'):
    pass # use localhost
elif 'localhost' in es_url:
    es_url = es_url.replace('localhost', 'elasticsearch')

es_client = Elasticsearch(es_url)
INDEX_NAME = 'movies'

def sync_movie_to_es(movie):
    """Sync a Django Movie model to Elasticsearch."""
    try:
        doc = {
            'id': movie.id,
            'title': movie.title,
            'description': movie.description,
            'director': movie.director,
            'cast': movie.cast,
            'tags': movie.tags,
            'release_year': movie.release_year,
            'rating': movie.rating,
            'slug': movie.slug,
            'poster_url': movie.poster_url,
            'genres': [g.name for g in movie.genres.all()]
        }
        es_client.index(index=INDEX_NAME, id=movie.id, document=doc)
    except Exception as e:
        print(f"Failed to sync movie to ES: {e}")

def search_movies_es(query, size=30):
    """Perform fuzzy search using Elasticsearch."""
    try:
        if not es_client.indices.exists(index=INDEX_NAME):
            return None
            
        res = es_client.search(
            index=INDEX_NAME,
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "description", "director^2", "cast^2", "tags", "genres"],
                        "fuzziness": "AUTO"
                    }
                },
                "size": size
            }
        )
        # Return list of movie IDs that matched
        return [hit['_source'] for hit in res['hits']['hits']]
    except Exception as e:
        print(f"ES search failed: {e}")
        return None
