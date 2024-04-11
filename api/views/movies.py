from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from web.models import Movie

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from web.models import Movie, Genre, Director
from PyMovieDb import IMDB
import json
import datetime

imdb = IMDB()

def _get_movie_details(name=None, id=None):
    if name:
        results = imdb.get_by_name(name)
    elif id:
        results = imdb.get_by_id(id)
    return json.loads(results)

def _create_movie(movie_id):
    # Check if movie already exists to avoid duplicates
    if Movie.objects.filter(id=movie_id).exists():
        return {"error": "Movie with this ID already exists"}, status.HTTP_400_BAD_REQUEST
    
    # Create a new Movie instance with the provided ID
    movie = Movie(id=movie_id)

    # Extract additional movie details from the get_movie_details API
    movie_details = _get_movie_details(id=movie_id)
    if not movie_details:
        return {"error": "Failed to retrieve movie details"}, status.HTTP_500_INTERNAL_SERVER_ERROR
    if movie_details['status'] == 404:
        # how? ¯\_(ツ)_/¯
        return {"error": "Movie not found"}, status.HTTP_404_NOT_FOUND

    genres = movie_details.get("genre", [])
    # duration has a weird format (e.g. PT1H55M) :p
    duration = movie_details.get("duration")
    if 'M' not in duration:
        duration += '0M'
    time_obj = datetime.datetime.strptime(duration.replace("PT", ''), "%HH%MM")
    runtime = time_obj.hour * 60 + time_obj.minute
    short_description = movie_details.get("short_description")

    # Set the movie details
    movie.title = movie_details.get("name")
    movie.release_date = movie_details.get("datePublished")
    movie.director = movie_details.get("director")
    movie.runtime = runtime
    movie.imdb_rating = movie_details.get("rating").get("ratingValue")
    movie.description = movie_details.get("description")
    movie.content_rating = movie_details.get("contentRating")
    movie.poster_url = movie_details.get("poster") # amazon link
    
    movie.save()

    # Link the genres to the movie
    for genre_name in genres:
        genre, created = Genre.objects.get_or_create(name=genre_name)
        movie.genres.add(genre)

    for director in movie_details.get("director"):
        director_obj, created = Director.objects.get_or_create(name=director['name'], url=director['url'])
        movie.directors.add(director_obj)
    
    return {"message": "Movie created successfully", "movie_id": movie.id}, status.HTTP_201_CREATED

@api_view(['GET'])
@permission_classes([AllowAny])
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
def create_movie(request):
    movie_id = request.data.get("id")
    if not movie_id:
        return Response({"error": "Movie ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    result, status_code = _create_movie(movie_id)
    return Response(result, status=status_code)