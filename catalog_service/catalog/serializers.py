from rest_framework import serializers
from .models import Category, Genre, Movie, Review, Playlist


class CategorySerializer(serializers.ModelSerializer):
    movie_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'order', 'movie_count']

    def get_movie_count(self, obj):
        return obj.movies.filter(is_active=True).count()


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'slug']


class MovieImageMixin:
    """Shared image URL resolution for movie serializers."""
    def get_poster_display(self, obj):
        return obj.get_poster_display()

    def get_thumbnail_display(self, obj):
        return obj.get_thumbnail_display()

    def get_backdrop_display(self, obj):
        return obj.get_backdrop_display()


class MovieListSerializer(MovieImageMixin, serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    poster_display = serializers.SerializerMethodField()
    thumbnail_display = serializers.SerializerMethodField()
    backdrop_display = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ['id', 'title', 'slug', 'description', 'content_type', 'release_year',
                  'duration', 'director', 'rating', 'maturity_rating', 'poster_display',
                  'thumbnail_display', 'backdrop_display', 'trailer_url', 'genres', 'view_count', 'like_count',
                  'trending_score', 'is_featured', 'requires_access', 'created_at']


class MovieDetailSerializer(MovieImageMixin, serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    poster_display = serializers.SerializerMethodField()
    thumbnail_display = serializers.SerializerMethodField()
    backdrop_display = serializers.SerializerMethodField()
    cast_list = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ['id', 'title', 'slug', 'description', 'content_type', 'release_year',
                  'duration', 'director', 'cast', 'cast_list', 'rating', 'maturity_rating',
                  'poster_display', 'thumbnail_display', 'backdrop_display', 'poster_url', 'thumbnail_url', 'trailer_url',
                  'category', 'genres', 'tags', 'tags_list', 'view_count', 'like_count',
                  'trending_score', 'is_featured', 'requires_access', 'created_at', 'updated_at']

    def get_cast_list(self, obj):
        return obj.get_cast_list()

    def get_tags_list(self, obj):
        return obj.get_tags_list()


class MovieCreateSerializer(serializers.ModelSerializer):
    genre_ids = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)

    class Meta:
        model = Movie
        fields = ['title', 'slug', 'description', 'content_type', 'release_year',
                  'duration', 'director', 'cast', 'rating', 'maturity_rating',
                  'poster', 'poster_url', 'thumbnail', 'thumbnail_url',
                  'backdrop', 'backdrop_url', 'trailer_url',
                  'video_file', 'category', 'genre_ids', 'tags', 'is_featured',
                  'requires_access']

    def create(self, validated_data):
        genre_ids = validated_data.pop('genre_ids', [])
        movie = Movie.objects.create(**validated_data)
        if genre_ids:
            movie.genres.set(genre_ids)
        return movie

    def update(self, instance, validated_data):
        genre_ids = validated_data.pop('genre_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if genre_ids is not None:
            instance.genres.set(genre_ids)
        return instance


class PlaylistSerializer(serializers.ModelSerializer):
    movies = MovieListSerializer(many=True, read_only=True)
    movie_count = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'slug', 'description', 'poster_url', 'movies',
                  'movie_count', 'is_featured', 'order', 'created_at']

    def get_movie_count(self, obj):
        return obj.movies.count()


class PlaylistListSerializer(serializers.ModelSerializer):
    movie_count = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'slug', 'description', 'poster_url',
                  'movie_count', 'is_featured', 'order']

    def get_movie_count(self, obj):
        return obj.movies.count()


class ReviewSerializer(serializers.ModelSerializer):
    movie_title = serializers.SerializerMethodField()
    movie_slug = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'movie', 'movie_title', 'movie_slug', 'user_id', 'username', 'user_avatar', 'rating',
                  'title', 'content', 'contains_spoilers', 'likes', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'user_id', 'username', 'user_avatar', 'likes', 'created_at', 'updated_at']

    def get_movie_title(self, obj):
        return obj.movie.title if obj.movie else ''

    def get_movie_slug(self, obj):
        return obj.movie.slug if obj.movie else ''


class ReviewCreateSerializer(serializers.Serializer):
    movie_id = serializers.IntegerField()
    rating = serializers.FloatField(min_value=1, max_value=10)
    title = serializers.CharField(max_length=255, required=False, default='')
    content = serializers.CharField(required=False, default='')
    contains_spoilers = serializers.BooleanField(required=False, default=False)
