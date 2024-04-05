from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from web.models import Movie

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from web.models import Movie
from PyMovieDb import IMDB
import json

imdb = IMDB()

@api_view(['GET'])
@permission_classes([AllowAny])
def get_movie_details(request):
    name = request.query_params.get('name')
    id = request.query_params.get('id')
    if name:
        results = imdb.get_by_name(name)
        return Response(json.loads(results))
    elif id:
        movie_info = imdb.get_by_id(id)
        return Response(json.loads(movie_info))
    else:
        return Response({'error': 'Bad Request: Please provide either a name or an id'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def search_movies(request):
    query = request.query_params.get('query')
    year = request.query_params.get('year')  # recommended
    res = imdb.search(query, year=year)
    return Response(json.loads(res))

@api_view(['GET'])
@permission_classes([AllowAny])
def get_upcoming_movies(request):
    region = request.query_params.get('region')
    res = imdb.upcoming(region=region)
    return Response(json.loads(res))

@api_view(['GET'])
@permission_classes([AllowAny])
def get_popular_movies(request):
    genre = request.query_params.get('genre')
    page = request.query_params.get('page', 0)
    start_id = int(page) * 50 + 1
    sort_by = request.query_params.get('sort_by')
    res = imdb.popular_movies(genre=genre, start_id=start_id, sort_by=sort_by)
    res = json.loads(res)
    res['results'] = [movie for movie in res['results'] if movie['poster'] != "image_not_found"]  # filter out glitched garbage
    res['result_count'] = len(res['results'])
    return Response(res)
