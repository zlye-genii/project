# ai stuff file
import os
from dotenv import load_dotenv
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .user import _get_user_favorites
import requests
import json
load_dotenv('../..')
AI_BASE_URL = os.getenv('AI_BASE_URL')
AI_TOKEN = os.getenv('AI_TOKEN')

# if this doesnt work properly try the <AIROLE> from AP-3
PROMPT = '''You are a {{CONTENT_TYPE}} expert and your task is to recommend {{CONTENT_TYPE_PLURAL}} based on the User's past {{CONTENT_TYPE_PLURAL_ACTION}} and favorites.
You will be given the User's preferences in the <UserPreferences> tag. You must provide a list of FIVE {{CONTENT_TYPE_PLURAL}}, outputting ONLY COMMA-SEPERATED NAMES, after the "Recommendations" line.
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
    if media_type == 'movie':
        favorites_list = _get_user_favorites(profile, media_type)
        # TODO: implement last watched lol
        # last_watched = profile.last_watched_movies.all().order_by('-watch_date')[:5]
        # last_watched_list = [movie.title for movie in last_watched]
    elif media_type == 'book':
        favorites_list = _get_user_favorites(profile, media_type)
        # e
    
    else:
        return Response({"error": "Invalid media type"}, status=status.HTTP_400_BAD_REQUEST)

    prompt_filled = PROMPT.replace("{{FAVORITES}}", FAVORITES_BASE + " " + ", ".join(x['title'] for x in favorites_list))
    # prompt_filled = prompt_filled.replace("{{LASTWATCHED}}", LASTWATCHED_BASE + " " + ", ".join(last_watched_list))
    prompt_filled = prompt_filled.replace("{{CONTENT_TYPE}}", media_type) \
        .replace("{{CONTENT_TYPE_PLURAL}}", content_type_plural[media_type]) \
        .replace("{{CONTENT_TYPE_PLURAL_ACTION}}", content_type_plural_action[media_type])

    # https://platform.openai.com/docs/guides/text-generation
    # https://platform.openai.com/docs/api-reference/chat
    messages = [
        {"role": "system", "content": prompt_filled},
        {"role": "user", "content": "Recommendations:"}
    ]

    print(messages)

    response = requests.post(
        AI_BASE_URL + '/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {AI_TOKEN}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3' # me when cloudflare moment
        },
        json={
            'model': 'gpt-4', # TODO: change to gigachat later
            'messages': messages,
            "temperature": 0.5,
            "top_p": 0.5,
            "max_tokens": 256
        }
    )

    if response.ok:
        recommendations = response.json()['choices'][0]['message']['content'].split(', ')
        return Response({"recommendations": recommendations}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "AI service unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)