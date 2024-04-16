from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.response import Response
from api.views.movies import _create_movie
from api.views.book import create_book

def get_media(request):
    media_id = request.data.get("media_id")
    media_type = request.data.get("media_type")  # 'movie' or 'book'

    if not media_id or not media_type:
        return Response({"error": "Media ID and type are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        model = ContentType.objects.get(model=media_type).model_class()
        media = model.objects.get(id=media_id)
        return media
    except model.DoesNotExist:
        if media_type == 'movie':
            result, status_code = _create_movie(media_id)
            if status_code == status.HTTP_201_CREATED:
                return model.objects.get(id=media_id)
        elif media_type == 'book':
            result, status_code = create_book(request)
            if status_code == status.HTTP_201_CREATED:
                return model.objects.get(id=media_id)
        return Response({"error": "Media not found"}, status=status.HTTP_404_NOT_FOUND)