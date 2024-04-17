from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from utils.movie import _create_movie, _get_movie_details
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
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
    name = request.query_params.get('name')
    id = request.query_params.get('id')
    if name or id:
        movie_info = _get_movie_details(name=name, id=id)
        return Response(movie_info)
    else:
        return Response({'error': 'Bad Request: Please provide either a name or an id'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def search_movies(request):
    query = request.query_params.get('query')
    year = request.query_params.get('year')  # recommended
    res = imdb.search(query, year=year)
    return Response(json.loads(res))

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
def get_popular_movies(request): # TODO fix: returns movie results in spanish (????????)
    genre = request.query_params.get('genre')
    page = request.query_params.get('page', 0)
    start_id = int(page) * 50 + 1
    sort_by = request.query_params.get('sort_by')
    res = imdb.popular_movies(genre=genre, start_id=start_id, sort_by=sort_by)
    res = json.loads(res)
    res['results'] = [movie for movie in res['results'] if movie['poster'] != "image_not_found"]  # filter out glitched garbage
    res['result_count'] = len(res['results'])
    return Response(res)

# this is mainly for speed reasons because scraper is sloooooooow
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def create_movie(request):
    movie_id = request.data.get("id")
    if not movie_id:
        return Response({"error": "Movie ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    result, status_code = _create_movie(movie_id)
    return Response(result, status=status_code)