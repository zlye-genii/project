# ai stuff file
import os
from dotenv import load_dotenv
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from user.models import Profile
import requests
import json
load_dotenv('../..')
AI_BASE_URL = os.getenv('AI_BASE_URL')
AI_TOKEN = os.getenv('AI_TOKEN')

# if this doesnt work properly try the <AIROLE> from AP-3
PROMPT = '''You are a movie expert and your task is to recommend movies based on the User's past watched movies and favorites.
You will be given the User's preferences in the <UserPreferences> tag. You must provide a list of FIVE movies, outputting ONLY COMMA-SEPERATED NAMES, after the "Recommendations" line.
<UserPreferences>
{{FAVORITES}}
{{LASTWATCHED}}
</UserPreferences>
'''
FAVORITES_BASE = "User has added the following movies to their favorites:"
LASTWATCHED_BASE = "User has watched these movies last:"


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_recommendations(request):
    profile = request.user.profile
    favorites = profile.favorite_movies.all().order_by('-id')[:5]
    favorites_list = [movie.title for movie in favorites]
    last_watched = profile.last_watched_movies.all().order_by('-watch_date')[:5]
    last_watched_list = [movie.title for movie in last_watched]

    prompt_filled = PROMPT.replace("{{FAVORITES}}", FAVORITES_BASE + " " + ", ".join(favorites_list))
    prompt_filled = prompt_filled.replace("{{LASTWATCHED}}", LASTWATCHED_BASE + " " + ", ".join(last_watched_list))

    # https://platform.openai.com/docs/guides/text-generation
    # https://platform.openai.com/docs/api-reference/chat
    messages = [
        {"role": "system", "content": prompt_filled},
        {"role": "user", "content": "Recommendations:"}
    ]

    response = requests.post(
        AI_BASE_URL,
        headers={
            'Authorization': f'Bearer {AI_TOKEN}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3' # me when cloudflare moment
        },
        json={
            'model': 'gpt-4', # TODO: change to gigachat later
            'messages': messages,
            "temperature": 0.5,
            "top_p": 0.5
        }
    )

    if response.status_code == 200:
        recommendations = response.json()['choices'][0]['message']['content'].split(',')
        return Response({"recommendations": recommendations}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "AI service unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


def get_book_by_id(book_id):
    GOOGLE_BOOKS_API_URL = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    response = requests.get(GOOGLE_BOOKS_API_URL)

    if response.status_code == 200:
        return response.json()
    else:
        return None

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_book(request):
    book_id = request.data.get('book_id')

    if book_id:
        book = get_book_by_id(book_id)
        if book:
            return Response({"book": book}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"error": "No book_id provided"}, status=status.HTTP_400_BAD_REQUEST)
