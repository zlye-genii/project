from django.contrib.auth.models import User
from rest_framework import serializers
from user.models import Profile
from web.models import Movie, Genre, Person, Book, Rating

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}
    
class RatingSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField()

    class Meta:
        model = Rating
        fields = ['stars', 'review', 'profile', 'media', 'favorited', 'completed']

    def get_media(self, obj):
        if isinstance(obj.media, Movie):
            return MovieSerializer(obj.media).data
        elif isinstance(obj.media, Book):
            return BookSerializer(obj.media).data
        else:
            return None

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    ratings = RatingSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ('user', 'ratings')

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['name']

class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    directors = PersonSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'release_date', 'genres', 'thumbnail', 'directors', 'runtime', 'imdb_rating', 'content_rating']

class BookSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    authors = PersonSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'description', 'release_date', 'genres', 'thumbnail', 'authors', 'pages']