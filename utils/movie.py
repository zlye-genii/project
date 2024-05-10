from rest_framework import status
from web.models import Movie, Genre, Person
from rest_framework.response import Response
from api.serializers import MovieSerializer
from PIL import Image
import os
import requests
from io import BytesIO
from PyMovieDb import IMDB
from django.core.cache import cache
import json
import datetime
from utils.translate import translate

imdb = IMDB()
    
# compress poster urls received from amazon because my chrome is crying loading 50 of these
# books are fine (common google W)
def compress_movie_media(movie_id, poster_url, regen=False):
    img_path = os.path.join('static', 'movieposters', os.path.basename(movie_id) + '.png')
    if not regen and img_path:
        return img_path
    response = requests.get(poster_url)
    img = Image.open(BytesIO(response.content))
    img = img.resize((150, 250), Image.ANTIALIAS) # adjust this

    img.save(img_path)

    return img_path.replace('\\', '/') # windows <3

def poster_exists(path):
    # checks if poster exists
    # alternatively create a 404 default img but blehhhh :3
    return os.path.isfile(path)

def _get_movie_details(id, db_only=True):
    movie = cache.get(f'movie_{id}')
    if not movie:
        movie = Movie.objects.filter(id=id).first()
        if not movie:
            if db_only:
                results, stat = _create_movie(id)
                if stat != status.HTTP_201_CREATED: # uh well um oops good luck
                    return Response(results, status=stat)
                movie = Movie.objects.filter(id=id).first()
            else:
                results = json.loads(imdb.get_by_id(id))
        if movie:
            cache.set(f'movie_{id}', movie) # cache
        
    return results if not movie else MovieSerializer(movie).data

def _create_movie(movie_id):
    # Check if movie already exists to avoid duplicates
    if Movie.objects.filter(id=movie_id).exists():
        return {"error": "Movie with this ID already exists"}, status.HTTP_400_BAD_REQUEST
    
    # Create a new Movie instance with the provided ID
    movie = Movie(id=movie_id)

    # Extract additional movie details from the get_movie_details API
    movie_details = _get_movie_details(id=movie_id, db_only=False)
    if not movie_details:
        return {"error": "Failed to retrieve movie details"}, status.HTTP_500_INTERNAL_SERVER_ERROR
    if 'status' in movie_details:
        if movie_details['status'] == 404:
            # how? ¯\_(ツ)_/¯
            return {"error": "Movie not found"}, status.HTTP_404_NOT_FOUND

    genres = movie_details.get("genre", [])
    directors = movie_details.get("director")
    # duration has a weird format (e.g. PT1H55M) :p
    duration = movie_details.get("duration")
    if not duration:
        duration = '0H0M'
    if 'M' not in duration:
        duration += '0M'
    time_obj = datetime.datetime.strptime(duration.replace("PT", ''), "%HH%MM")
    runtime = time_obj.hour * 60 + time_obj.minute

    # Set the movie details
    translated = translate([movie_details.get("name"), movie_details.get("description")] + [genre for genre in genres])
    movie.title = translated[0]
    movie.release_date = movie_details.get("datePublished")
    movie.runtime = runtime
    movie.imdb_rating = movie_details.get("rating").get("ratingValue")
    movie.description = translated[1]
    movie.content_rating = movie_details.get("contentRating")
    if movie_details.get("poster"):
        movie.thumbnail = compress_movie_media(movie_id, movie_details.get("poster"))
    
    movie.save()

    # Link the genres to the movie
    if genres:
        for i, genre_name in enumerate(genres):
            genre, created = Genre.objects.get_or_create(name=genre_name)
            if created:
                genre.translated_name = translated[i+2]
                genre.save()
            movie.genres.add(genre)
    if directors:
        for director in directors:
            director_obj, created = Person.objects.get_or_create(name=director['name'], url=director['url'])
            movie.directors.add(director_obj)
    
    return {"message": "Movie created successfully", "movie_id": movie.id}, status.HTTP_201_CREATED
