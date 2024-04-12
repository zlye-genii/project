from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from ..serializers import ProfileSerializer
from django.contrib.contenttypes.models import ContentType
from web.models import Movie, Rating
from .movies import _create_movie

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    profile = request.user.profile
    serializer = ProfileSerializer(profile)
    return Response(serializer.data, status=status.HTTP_200_OK)

# TODO: might have to convert this to a universal favorites thing (movie/book)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_movie_to_favorites(request):
    movie_id = request.data.get("movie_id")
    if not movie_id:
        return Response({"error": "Movie ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        try:
            _create_movie(movie_id)
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)

    profile = request.user.profile
    rating = profile.ratings.filter(media=movie).exists()
    if not rating:
        rating, created = Rating.objects.get_or_create(favorited=True, media=movie, profile=profile)
        profile.ratings.add(rating)
        profile.save()
        return Response({"message": "Movie added to favorites"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Movie already in favorites"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_movie_from_favorites(request):
    movie_id = request.data.get("movie_id")
    if not movie_id:
        return Response({"error": "Movie ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        try:
            _create_movie(movie_id)
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)

    profile = request.user.profile
    rating = profile.ratings.filter(media=movie).first()
    if not rating:
        rating.favorited = False
        rating.save()
        return Response({"message": "Movie removed from favorites"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Movie not in favorites"}, status=status.HTTP_400_BAD_REQUEST)
