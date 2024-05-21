# ai stuff file
import os
from dotenv import load_dotenv
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .user import _get_user_favorites, _get_user_completed
from api.serializers import BookSerializer, MovieSerializer
import requests
from utils.movie import _create_movie
from utils.book import _create_book
from web.models import Movie, Book
from api.views.movies import _search_movies
from api.views.books import _search_books
load_dotenv('../..')
AI_BASE_URL = os.getenv('AI_BASE_URL')
AI_TOKEN = os.getenv('AI_TOKEN')

# if this doesnt work properly try the <AIROLE> from AP-3
PROMPT = '''You are a {{CONTENT_TYPE}} expert and your task is to recommend {{CONTENT_TYPE_PLURAL}} based on the User's past {{CONTENT_TYPE_PLURAL_ACTION}} and favorites.
You will be given the User's preferences in the <UserPreferences> tag. You must provide a list of FIVE {{CONTENT_TYPE_PLURAL}}, outputting ONLY COMMA-SEPERATED NAMES, after the "Recommendations" line.
Your response MUST BE IN ENGLISH. Write all media titles IN ENGLISH.
<UserPreferences>
{{FAVORITES}}
</UserPreferences>
'''
FAVORITES_BASE = "User has added the following {{CONTENT_TYPE_PLURAL}} to their favorites:"
LASTWATCHED_BASE = "User has watched these {{CONTENT_TYPE_PLURAL}} last:"

content_type_plural = {
    "movie": "movies",
    "book": "books"
}

content_type_plural_action = {
    "movie": "watched movies",
    "book": "read books"
}

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_recommendations(request):
    profile = request.user.profile
    media_type = request.query_params.get('media_type')
    favorites_list = _get_user_favorites(profile, media_type)
    completed_list = _get_user_completed(profile, media_type)

    if not favorites_list or not completed_list:
        return Response({"error": "Invalid media type or no data available"}, status=status.HTTP_400_BAD_REQUEST)

    prompt_filled = PROMPT.replace("{{FAVORITES}}", FAVORITES_BASE + " " + ", ".join(x['media']['title'] for x in favorites_list))
    prompt_filled = prompt_filled.replace("{{LASTWATCHED}}", LASTWATCHED_BASE + " " + ", ".join(x['media']['title'] for x in completed_list))
    prompt_filled = prompt_filled.replace("{{CONTENT_TYPE}}", media_type) \
        .replace("{{CONTENT_TYPE_PLURAL}}", content_type_plural[media_type]) \
        .replace("{{CONTENT_TYPE_PLURAL_ACTION}}", content_type_plural_action[media_type])

    messages = [
        {"role": "system", "content": prompt_filled},
        {"role": "user", "content": "Recommendations:"}
    ]

    response = requests.post(
        AI_BASE_URL + '/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {AI_TOKEN}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        },
        json={
            'model': 'gpt-4',
            'messages': messages,
            "temperature": 0.5,
            "top_p": 0.5,
            "max_tokens": 256
        }
    )

    if response.ok:
        recommendations = response.json()['choices'][0]['message']['content'].split(', ')
        media_objects = []
        for rec in recommendations:
            if media_type == 'movie':
                # Search for the movie by title
                search_results = _search_movies(rec)
                if search_results:
                    # Get the ID of the first result
                    movie_id = search_results[0]['id']
                    # Attempt to create the movie
                    results, status_code = _create_movie(movie_id)
                    if status_code == status.HTTP_201_CREATED or status_code == status.HTTP_400_BAD_REQUEST:
                        # The movie was created successfully or already exists
                        movie = Movie.objects.get(id=movie_id)
                        media_objects.append(movie)
                    else:
                        # Handle other errors appropriately
                        return Response(results, status=status_code)
            elif media_type == 'book':
                # Similar logic for books
                search_results = _search_books(rec)
                if search_results:
                    book_id = search_results[0]['id']
                    results, status_code = _create_book(book_id)
                    if status_code == status.HTTP_201_CREATED or status_code == status.HTTP_400_BAD_REQUEST:
                        book = Book.objects.get(id=book_id)
                        media_objects.append(book)
                    else:
                        return Response(results, status=status_code)
                
        serialized_media = MovieSerializer(media_objects, many=True) if media_type == 'movie' else BookSerializer(media_objects, many=True)
        return Response({"recommendations": serialized_media.data}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "AI service unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)