from django.core.management.base import BaseCommand
from catalog.models import Movie
from catalog.search_engine import sync_movie_to_es

class Command(BaseCommand):
    help = 'Sync all movies to Elasticsearch'

    def handle(self, *args, **options):
        movies = Movie.objects.filter(is_active=True)
        self.stdout.write(f"Syncing {movies.count()} movies to Elasticsearch...")
        count = 0
        for movie in movies:
            sync_movie_to_es(movie)
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Successfully synced {count} movies."))
