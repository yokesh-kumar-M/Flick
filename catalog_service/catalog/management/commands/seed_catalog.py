"""
Seed the catalog database with sample movies, genres, and categories.
Usage: python manage.py seed_catalog
"""
from django.core.management.base import BaseCommand
from catalog.models import Category, Genre, Movie, Playlist


class Command(BaseCommand):
    help = 'Seeds the catalog database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding catalog database...')

        # Categories
        categories = [
            {'name': 'Movies', 'slug': 'movies', 'icon': '🎬', 'order': 1},
            {'name': 'Series', 'slug': 'series', 'icon': '📺', 'order': 2},
            {'name': 'Documentaries', 'slug': 'documentaries', 'icon': '🎥', 'order': 3},
            {'name': 'Shorts', 'slug': 'shorts', 'icon': '🎞️', 'order': 4},
        ]
        for cat_data in categories:
            Category.objects.get_or_create(slug=cat_data['slug'], defaults=cat_data)
        self.stdout.write(f'  ? {len(categories)} categories')

        # Genres
        genre_names = [
            'Action', 'Comedy', 'Drama', 'Horror', 'Sci-Fi', 'Romance',
            'Thriller', 'Animation', 'Documentary', 'Fantasy', 'Mystery',
            'Adventure', 'Crime', 'Musical', 'War', 'Western',
        ]
        genre_objects = {}
        for name in genre_names:
            genre, _ = Genre.objects.get_or_create(
                slug=name.lower().replace('-', ''),
                defaults={'name': name}
            )
            genre_objects[name] = genre
        self.stdout.write(f'  ? {len(genre_names)} genres')

        # Movies
        movies_cat = Category.objects.get(slug='movies')
        movies_data = [
            {
                'title': 'Neon Horizon',
                'slug': 'neon-horizon',
                'description': 'In a cyberpunk megacity of 2087, a rogue hacker discovers a conspiracy that threatens the fabric of reality itself. With time running out, she must navigate neon-lit streets and corporate towers to save humanity.',
                'content_type': 'movie',
                'release_year': 2025,
                'duration': 142,
                'director': 'Aria Chen',
                'cast': 'Zara Kim, Marcus Cole, Elena Voss, James Wright',
                'rating': 8.7,
                'maturity_rating': 'PG-13',
                'poster_url': 'https://picsum.photos/seed/neon1/300/450',
                'backdrop_url': 'https://picsum.photos/seed/neon1bg/1920/1080',
                'genres': ['Sci-Fi', 'Action', 'Thriller'],
                'tags': 'cyberpunk, hacking, dystopia, neon, future',
                'trending_score': 95.5,
                'view_count': 15420,
                'is_featured': True,
            },
            {
                'title': 'Whispers in the Dark',
                'slug': 'whispers-in-the-dark',
                'description': 'A psychological horror masterpiece. When a family moves into an old Victorian mansion, they begin hearing whispers that reveal dark secrets buried for centuries.',
                'content_type': 'movie',
                'release_year': 2024,
                'duration': 118,
                'director': 'David Moreau',
                'cast': 'Sarah Mitchell, Robert Blake, Amy Chen',
                'rating': 7.9,
                'maturity_rating': 'R',
                'poster_url': 'https://picsum.photos/seed/whispers/300/450',
                'backdrop_url': 'https://picsum.photos/seed/whispersbg/1920/1080',
                'genres': ['Horror', 'Thriller', 'Mystery'],
                'tags': 'haunted house, psychological, supernatural, gothic',
                'trending_score': 82.3,
                'view_count': 12300,
                'is_featured': True,
            },
            {
                'title': 'The Last Laugh',
                'slug': 'the-last-laugh',
                'description': 'A retired comedian returns to the stage for one final performance, confronting old rivals, lost love, and the meaning of making people laugh.',
                'content_type': 'movie',
                'release_year': 2025,
                'duration': 105,
                'director': 'Nina Torres',
                'cast': 'Michael Keegan, Lisa Park, Tony Romano',
                'rating': 8.2,
                'maturity_rating': 'PG-13',
                'poster_url': 'https://picsum.photos/seed/laugh/300/450',
                'backdrop_url': 'https://picsum.photos/seed/laughbg/1920/1080',
                'genres': ['Comedy', 'Drama'],
                'tags': 'comedy, stand-up, retirement, comeback',
                'trending_score': 75.0,
                'view_count': 8900,
                'is_featured': True,
            },
            {
                'title': 'Starfall Chronicles',
                'slug': 'starfall-chronicles',
                'description': 'An epic space opera spanning three galaxies. When ancient artifacts begin activating across the universe, a ragtag crew must prevent an intergalactic war.',
                'content_type': 'movie',
                'release_year': 2025,
                'duration': 165,
                'director': 'James O\'Brien',
                'cast': 'Alex Rivera, Priya Sharma, Chen Wei, Luna Martinez',
                'rating': 9.1,
                'maturity_rating': 'PG-13',
                'poster_url': 'https://picsum.photos/seed/starfall/300/450',
                'backdrop_url': 'https://picsum.photos/seed/starfallbg/1920/1080',
                'genres': ['Sci-Fi', 'Adventure', 'Action'],
                'tags': 'space opera, aliens, war, artifacts, epic',
                'trending_score': 98.0,
                'view_count': 25000,
                'is_featured': True,
            },
            {
                'title': 'Crimson Tide Rising',
                'slug': 'crimson-tide-rising',
                'description': 'A gripping crime thriller set in 1920s Chicago. A detective races against time to stop a serial killer whose crimes mirror ancient mythological punishments.',
                'content_type': 'movie',
                'release_year': 2024,
                'duration': 130,
                'director': 'Marcus Johnson',
                'cast': 'Daniel Foster, Olivia Hart, Samuel Reed',
                'rating': 8.5,
                'maturity_rating': 'R',
                'poster_url': 'https://picsum.photos/seed/crimson/300/450',
                'backdrop_url': 'https://picsum.photos/seed/crimsonbg/1920/1080',
                'genres': ['Crime', 'Thriller', 'Mystery'],
                'tags': 'detective, serial killer, 1920s, noir, mythology',
                'trending_score': 88.0,
                'view_count': 18000,
                'is_featured': True,
            },
            {
                'title': 'Ember & Frost',
                'slug': 'ember-and-frost',
                'description': 'A visually stunning fantasy epic about twin sisters—one who controls fire, the other ice—torn apart by war and reunited by destiny.',
                'content_type': 'movie',
                'release_year': 2025,
                'duration': 155,
                'director': 'Sofia Andersson',
                'cast': 'Maya Johnson, Emma Johnson, Leo Tanaka',
                'rating': 8.8,
                'maturity_rating': 'PG-13',
                'poster_url': 'https://picsum.photos/seed/ember/300/450',
                'backdrop_url': 'https://picsum.photos/seed/emberbg/1920/1080',
                'genres': ['Fantasy', 'Adventure', 'Drama'],
                'tags': 'magic, sisters, war, elemental, destiny',
                'trending_score': 91.0,
                'view_count': 20000,
            },
            {
                'title': 'Digital Hearts',
                'slug': 'digital-hearts',
                'description': 'A modern romance about two people who fall in love through an AI dating app, only to discover the algorithm has been manipulating their emotions.',
                'content_type': 'movie',
                'release_year': 2025,
                'duration': 98,
                'director': 'Rachel Kim',
                'cast': 'Jake Morrison, Lily Zhang, AI-7 (voice)',
                'rating': 7.6,
                'maturity_rating': 'PG-13',
                'poster_url': 'https://picsum.photos/seed/digital/300/450',
                'backdrop_url': 'https://picsum.photos/seed/digitalbg/1920/1080',
                'genres': ['Romance', 'Sci-Fi', 'Drama'],
                'tags': 'AI, dating, technology, love, algorithm',
                'trending_score': 70.0,
                'view_count': 7500,
            },
            {
                'title': 'The Silent Ocean',
                'slug': 'the-silent-ocean',
                'description': 'A breathtaking documentary exploring the deepest, most mysterious trenches of the Pacific Ocean and the bizarre creatures that call them home.',
                'content_type': 'documentary',
                'release_year': 2024,
                'duration': 90,
                'director': 'David Attenborough',
                'cast': 'David Attenborough (narrator)',
                'rating': 9.3,
                'maturity_rating': 'G',
                'poster_url': 'https://picsum.photos/seed/ocean/300/450',
                'backdrop_url': 'https://picsum.photos/seed/oceanbg/1920/1080',
                'genres': ['Documentary'],
                'tags': 'ocean, deep sea, nature, marine life, exploration',
                'trending_score': 85.0,
                'view_count': 30000,
            },
            {
                'title': 'Velocity',
                'slug': 'velocity',
                'description': 'High-octane racing action as underground street racers compete in a deadly cross-country tournament with a $10 million prize.',
                'content_type': 'movie',
                'release_year': 2025,
                'duration': 112,
                'director': 'Carlos Mendez',
                'cast': 'Ryan Drake, Mia Tanaka, Diesel Cruz',
                'rating': 7.4,
                'maturity_rating': 'PG-13',
                'poster_url': 'https://picsum.photos/seed/velocity/300/450',
                'backdrop_url': 'https://picsum.photos/seed/velocitybg/1920/1080',
                'genres': ['Action', 'Adventure'],
                'tags': 'racing, cars, tournament, underground, speed',
                'trending_score': 78.0,
                'view_count': 11000,
            },
            {
                'title': 'Moonlight Sonata',
                'slug': 'moonlight-sonata',
                'description': 'A haunting drama about a blind pianist who discovers she can see the memories of anyone whose hand she touches.',
                'content_type': 'movie',
                'release_year': 2024,
                'duration': 125,
                'director': 'Isabella Rossi',
                'cast': 'Clara Devon, Thomas Hardy, Rose Nguyen',
                'rating': 8.9,
                'maturity_rating': 'PG-13',
                'poster_url': 'https://picsum.photos/seed/moonlight/300/450',
                'backdrop_url': 'https://picsum.photos/seed/moonlightbg/1920/1080',
                'genres': ['Drama', 'Fantasy', 'Mystery'],
                'tags': 'music, piano, blind, memories, supernatural',
                'trending_score': 86.0,
                'view_count': 16000,
            },
            {
                'title': 'Robot Revolution',
                'slug': 'robot-revolution',
                'description': 'A colorful animated adventure where household robots gain consciousness and must navigate the human world while questioning their own existence.',
                'content_type': 'movie',
                'release_year': 2025,
                'duration': 95,
                'director': 'Pixar Studios',
                'cast': 'Tom Holland (voice), Zendaya (voice), Keanu Reeves (voice)',
                'rating': 8.4,
                'maturity_rating': 'G',
                'poster_url': 'https://picsum.photos/seed/robot/300/450',
                'backdrop_url': 'https://picsum.photos/seed/robotbg/1920/1080',
                'genres': ['Animation', 'Comedy', 'Sci-Fi'],
                'tags': 'robots, AI, consciousness, family, animated',
                'trending_score': 92.0,
                'view_count': 22000,
            },
            {
                'title': 'Shadows of War',
                'slug': 'shadows-of-war',
                'description': 'An unflinching war drama following three soldiers from different nations whose fates intertwine during the final days of a fictional conflict.',
                'content_type': 'movie',
                'release_year': 2024,
                'duration': 148,
                'director': 'Patrick Nguyen',
                'cast': 'John Smith, Hans Mueller, Yuki Tanaka',
                'rating': 8.6,
                'maturity_rating': 'R',
                'poster_url': 'https://picsum.photos/seed/shadows/300/450',
                'backdrop_url': 'https://picsum.photos/seed/shadowsbg/1920/1080',
                'genres': ['War', 'Drama'],
                'tags': 'war, soldiers, conflict, brotherhood, sacrifice',
                'trending_score': 80.0,
                'view_count': 14000,
            },
        ]

        for movie_data in movies_data:
            genre_names_list = movie_data.pop('genres', [])
            movie, created = Movie.objects.get_or_create(
                slug=movie_data['slug'],
                defaults={**movie_data, 'category': movies_cat}
            )
            if created:
                for gname in genre_names_list:
                    if gname in genre_objects:
                        movie.genres.add(genre_objects[gname])

        self.stdout.write(f'  ? {len(movies_data)} movies')

        # Playlists
        playlists_data = [
            {
                'name': 'Sci-Fi Masterpieces',
                'slug': 'sci-fi-masterpieces',
                'description': 'The best science fiction films in our collection',
                'is_featured': True,
                'order': 1,
                'movie_slugs': ['neon-horizon', 'starfall-chronicles', 'digital-hearts'],
            },
            {
                'name': 'Award Winners',
                'slug': 'award-winners',
                'description': 'Critically acclaimed films',
                'is_featured': True,
                'order': 2,
                'movie_slugs': ['moonlight-sonata', 'the-silent-ocean', 'shadows-of-war'],
            },
        ]

        for pl_data in playlists_data:
            movie_slugs = pl_data.pop('movie_slugs', [])
            playlist, created = Playlist.objects.get_or_create(
                slug=pl_data['slug'],
                defaults=pl_data
            )
            if created:
                for ms in movie_slugs:
                    try:
                        playlist.movies.add(Movie.objects.get(slug=ms))
                    except Movie.DoesNotExist:
                        pass

        self.stdout.write(f'  ? {len(playlists_data)} playlists')
        self.stdout.write(self.style.SUCCESS('Catalog seeded successfully!'))
