from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from utils.movie import _create_movie, _get_movie_details
from rest_framework.decorators import api_view, permission_classes
from web.models import Movie, Genre, Person
from api.serializers import MovieSerializer
from PyMovieDb import IMDB
import json
import datetime

imdb = IMDB()
    
@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def get_movie_details(request):
    id = request.query_params.get('id')
    if id:
        movie_info = _get_movie_details(id=id)
        if not isinstance(movie_info, Response):
            return Response(movie_info, status=status.HTTP_200_OK)
        else:
            return movie_info
    else:
        return Response({'error': 'Bad Request: Please provide an id'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def get_movie_details_bulk(request):
    ids = request.query_params.get('ids')
    if ids:
        ids = ids.split(',')
        movie_infos = []
        for id in ids:
            movie_info = _get_movie_details(id=id)
            if not isinstance(movie_info, Response):
                movie_infos.append(movie_info)
        return Response(movie_infos, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Bad Request: Please provide ids'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def search_movies(request):
    query = request.query_params.get('query')
    year = request.query_params.get('year')
    res = imdb.search(query, year=year)
    return Response(json.loads(res)['results'])

def _search_movies(query):
    res = imdb.search(query)
    return json.loads(res)['results']

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def get_upcoming_movies(request):
    region = request.query_params.get('region')
    res = imdb.upcoming(region=region)
    return Response(json.loads(res))

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def get_popular_movies(request):
    genre = request.query_params.get('genre')
    page = request.query_params.get('page', 0)
    start_id = int(page) * 50 + 1
    sort_by = request.query_params.get('sort_by')
    res = imdb.popular_movies(genre=genre, start_id=start_id, sort_by=sort_by)
    res = json.loads(res)
    res['results'] = [movie for movie in res['results'] if movie['poster'] != "image_not_found"]
    res['result_count'] = len(res['results'])
    return Response(res)

@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def create_movie(request):
    movie_id = request.data.get("id")
    if not movie_id:
        return Response({"error": "Movie ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    result, status_code = _create_movie(movie_id)
    return Response(result, status=status_code)