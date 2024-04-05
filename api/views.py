from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer, ProfileSerializer
from web.models import Movie

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    profile = request.user.profile
    serializer = ProfileSerializer(profile)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_movie_to_favorites(request):
    movie_id = request.data.get("movie_id")
    if not movie_id:
        return Response({"error": "Movie ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)

    profile = request.user.profile
    if movie not in profile.favorite_movies.all():
        profile.favorite_movies.add(movie)
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
        return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)

    profile = request.user.profile
    if movie in profile.favorite_movies.all():
        profile.favorite_movies.remove(movie)
        profile.save()
        return Response({"message": "Movie removed from favorites"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Movie not in favorites"}, status=status.HTTP_400_BAD_REQUEST)
