from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from ..serializers import ProfileSerializer, RatingSerializer
from django.contrib.contenttypes.models import ContentType
from web.models import Rating, Movie, Book, Genre
from utils.media import get_media

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    profile = request.user.profile
    serializer = ProfileSerializer(profile)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_media_rating(request):
    media = get_media(request)
    if isinstance(media, Response):
        return media
    profile = request.user.profile
    rating = profile.ratings.filter(media=media).first()

    star_rating = request.data.get('rating')  # 1 - 10
    if star_rating:
        star_rating = int(star_rating)
        if not 1 <= star_rating <= 10:
            return Response({"error": "Invalid Star Rating"}, status=status.HTTP_400_BAD_REQUEST)
        if not rating:
            rating, created = Rating.objects.get_or_create(stars=star_rating, media=media, profile=profile)
            profile.ratings.add(rating)
            profile.save()
        else:
            rating.stars = star_rating
            rating.save()
        return Response({"message": "Movie rating set successfully"}, status=status.HTTP_200_OK)

    favorited = request.data.get('favorited')  # true or false
    completed = request.data.get('completed')  # true or false

    if favorited is not None:
        if not rating:
            rating, created = Rating.objects.get_or_create(favorited=favorited, media=media, profile=profile)
            profile.ratings.add(rating)
            profile.save()
        elif rating:
            rating.favorited = favorited
            rating.save()
        else:
            return Response({"error": "Media not marked as favorited"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Media favorited status changed"}, status=status.HTTP_200_OK)

    if completed is not None:
        if not rating:
            rating, created = Rating.objects.get_or_create(completed=completed, media=media, profile=profile)
            profile.ratings.add(rating)
            profile.save()
        elif rating:
            rating.completed = completed
            rating.save()
        else:
            return Response({"error": "Media not marked as completed"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Media completed status changed"}, status=status.HTTP_200_OK)

def _get_user_favorites(profile, media_type):
    favorites = [rating for rating in profile.ratings.all() if isinstance(rating.media, (Movie if media_type == 'movie' else Book)) and rating.favorited]
    serializer = RatingSerializer(favorites, many=True)
    return serializer.data

def _get_user_completed(profile, media_type):
    watched = [rating for rating in profile.ratings.all() if isinstance(rating.media, (Movie if media_type == 'movie' else Book)) and rating.completed]
    serializer = RatingSerializer(watched, many=True)
    return serializer.data

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_preferred_genres(request):
    profile = request.user.profile
    genre_ids = request.data.get('genres', [])

    if not genre_ids:
        return Response({"error": "No genres provided"}, status=status.HTTP_400_BAD_REQUEST)

    genres = Genre.objects.filter(id__in=genre_ids)
    profile.preferred_genres.set(genres)
    profile.save()

    return Response({"message": "Preferred genres updated successfully"}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_ratings_by_media_type(request):
    media_type = request.query_params.get("media_type")  # 'movie' or 'book'

    if not media_type:
        return Response({"error": "Media type is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        model = ContentType.objects.get(model=media_type).model_class()
    except model.DoesNotExist:
        return Response({"error": "Invalid media type"}, status=status.HTTP_400_BAD_REQUEST)
    
    profile = request.user.profile
    ratings = [rating for rating in profile.ratings.all() if isinstance(rating.media, (Movie if media_type == 'movie' else Book))]

    ratings_list = [{"id": rating.media.id, "title": rating.media.title, "stars": rating.stars, "favorited": rating.favorited} for rating in ratings]

    return Response({"ratings": ratings_list}, status=status.HTTP_200_OK)