from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from ..serializers import ProfileSerializer
from django.contrib.contenttypes.models import ContentType
from web.models import Rating, Movie, Book
from utils.media import get_media

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    profile = request.user.profile
    serializer = ProfileSerializer(profile)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_media_to_favorites(request):
    media = get_media(request)
    if isinstance(media, Response):
        return media
    profile = request.user.profile
    rating = profile.ratings.filter(media=media).exists()
    if not rating:
        rating, created = Rating.objects.get_or_create(favorited=True, media=media, profile=profile)
        profile.ratings.add(rating)
        profile.save()
        return Response({"message": "Media added to favorites"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Media already in favorites"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_media_from_favorites(request):
    media = get_media(request)
    if isinstance(media, Response):
        return media

    profile = request.user.profile
    rating = profile.ratings.filter(media=media).first()
    if rating:
        rating.favorited = False
        rating.save()
        return Response({"message": "Media removed from favorites"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Media not in favorites"}, status=status.HTTP_400_BAD_REQUEST)

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

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def set_media_rating(request):
    star_rating = int(request.data.get('rating')) # 1 - 5

    media = get_media(request)
    if isinstance(media, Response):
        return media

    if not 1 <= star_rating <= 5:
        return Response({"error": "Invalid Star Rating"}, status=status.HTTP_400_BAD_REQUEST)

    profile = request.user.profile
    rating, created = Rating.objects.get_or_create(media=media, profile=profile)
    rating.stars = star_rating
    rating.save()

    return Response({"message": "Movie rating set successfully"}, status=status.HTTP_200_OK)