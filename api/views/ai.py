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
AI_MODEL = os.getenv("AI_MODEL")

# if this doesnt work properly try the <AIROLE> from AP-3
PROMPT = '''You are a {{CONTENT_TYPE}} expert and your task is to recommend {{CONTENT_TYPE_PLURAL}} based on the User's past {{CONTENT_TYPE_PLURAL_ACTION}}, favorites, and specific preferences.
You will be given the User's preferences in the <UserPreferences> tag. You must provide a list of FIVE {{CONTENT_TYPE_PLURAL}}, outputting ONLY COMMA-SEPARATED NAMES, after the "Recommendations" line.
Your response MUST BE IN ENGLISH. Write all media titles IN ENGLISH.
<UserPreferences>
{{FAVORITES}}
{{LASTWATCHED}}
Keyword: {{KEYWORD}}
Genre: {{GENRE}}
Country: {{COUNTRY}}
Creator: {{CREATOR}}
Year: {{YEAR}}
Age Rating: {{AGE_RATING}}
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
    keyword = request.query_params.get('keyword', 'not specified')
    genre = request.query_params.get('genre')
    if genre == 'none':
        print('using preferred_genres')
        genre = ', '.join([g.translated_name for g in profile.preferred_genres.all()])
    country = request.query_params.get('country', 'not specified')
    creator = request.query_params.get('creator', 'not specified')
    year = request.query_params.get('year', 'not specified')
    age_rating = request.query_params.get('age', 'not specified')
    # ¯\_(ツ)_/¯
    keyword = 'not specified' if keyword == '' else keyword
    country = 'not specified' if country == '' else country
    creator = 'not specified' if creator == '' else creator
    year = 'not specified' if year == '' else year
    age_rating = 'not specified' if age_rating == '' else age_rating


    if media_type not in ['movie', 'book']:
        return Response({"error": "Invalid media type"}, status=status.HTTP_400_BAD_REQUEST)

    if request.query_params.get('consider_favorites'):
        completed_list = _get_user_completed(profile, media_type)
        favorites_list = _get_user_favorites(profile, media_type)
    else:
        completed_list = []
        favorites_list = []
        print('toggle disable consider fav')

    if len(favorites_list) != 0:
        prompt_filled = PROMPT.replace("{{FAVORITES}}", FAVORITES_BASE + " " + ", ".join(x['media']['title'] for x in favorites_list))
    else:
        prompt_filled = PROMPT.replace("{{FAVORITES}}\n", '')
    if len(completed_list) != 0:
        prompt_filled = prompt_filled.replace("{{LASTWATCHED}}", LASTWATCHED_BASE + " " + ", ".join(x['media']['title'] for x in completed_list))
    else:
        prompt_filled = prompt_filled.replace("{{LASTWATCHED}}\n", '')
    prompt_filled = prompt_filled.replace("{{CONTENT_TYPE}}", media_type) \
        .replace("{{CONTENT_TYPE_PLURAL}}", content_type_plural[media_type]) \
        .replace("{{CONTENT_TYPE_PLURAL_ACTION}}", content_type_plural_action[media_type]) \
        .replace("{{KEYWORD}}", keyword) \
        .replace("{{GENRE}}", genre) \
        .replace("{{COUNTRY}}", country) \
        .replace("{{CREATOR}}", creator) \
        .replace("{{YEAR}}", year) \
        .replace("{{AGE_RATING}}", age_rating)
    print(prompt_filled)

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
            'model': AI_MODEL,
            'messages': messages,
            "temperature": 0.5,
            "top_p": 0.5,
            "max_tokens": 256
        }
    )

    if response.ok:
        recommendations = response.json()['choices'][0]['message']['content'].split(', ')
        print(recommendations)
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
        # :/ filter?
        print(response.json())
        return Response({"error": "AI service unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def summarize_book_description(request):
    book_id = request.data.get('book_id')
    if not book_id:
        return Response({"error": "Book ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

    prompt = f'''You are an AI trained to summarize texts. Please provide a concise summary of the following book description in RUSSIAN.
<BookDescription>
{book.description}
</BookDescription>
Your output must be IN RUSSIAN ONLY.
'''

    response = requests.post(
        AI_BASE_URL + '/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {AI_TOKEN}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        },
        json={
            'model': AI_MODEL,
            'messages': [
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Summary:"}
            ],
            "temperature": 0.5,
            "top_p": 0.5,
            "max_tokens": 512
        }
    )

    if response.ok:
        summary = response.json()['choices'][0]['message']['content']
        return Response({"summary": summary}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "AI service unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)