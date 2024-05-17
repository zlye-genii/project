from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Movie, Book, Genre
from utils.movie import poster_exists
from api.views.user import _get_user_favorites
import json

# Create your views here.

def index(request):
    one_month_ago = timezone.now() - timedelta(days=30)
    today = timezone.now()
    movies = Movie.objects.filter(release_date__gte=one_month_ago, release_date__lte=today).order_by('-imdb_rating')
    # Filter movies with existing poster files
    movies_with_posters = [movie for movie in movies if poster_exists(movie.thumbnail)]
    # Limit to the top 10 movies by IMDb rating
    top_movies = movies_with_posters[:10]
    books = Book.objects.filter()#release_date__gte=one_month_ago) # todo get some proper books from google api -_-
    # Limit to the top 10 books by IMDb rating
    top_books = books[:10]
    upcoming_movies = [movie for movie in Movie.objects.filter(release_date__gt=timezone.now()).order_by('release_date') if poster_exists(movie.thumbnail)][:10]
    if request.user.is_authenticated:
        favorites = _get_user_favorites(request.user.profile, "movie")
    else:
        favorites = None
    return render(request, 'novinki.html', {"movies": top_movies, "books": top_books, 'upcoming': upcoming_movies, 'favorites': json.dumps(favorites)})

def movielist(request):
    one_year_ago = timezone.now() - timedelta(days=365)
    today = timezone.now()
    genres = Genre.objects.all()
    mmovies = Movie.objects.prefetch_related('genres')
    movies = Movie.objects.filter(release_date__gte=one_year_ago, release_date__lte=today).exclude(imdb_rating__isnull=True).order_by('-imdb_rating')
    # Filter movies with existing poster files
    movies_with_posters = [movie for movie in movies if poster_exists(movie.thumbnail)]
    mmovies_with_posters = [movie for movie in mmovies if poster_exists(movie.thumbnail)]
    # Limit to the top 10 movies by IMDb rating
    top_movies = movies_with_posters[:25]
    return render(request, 'movies.html', {'top_movies': top_movies, 'movies': mmovies_with_posters, 'genres': genres})

def booklist(request):
    books = Book.objects.all().prefetch_related('genres', 'authors')
    return render(request, 'booklist.html', {'books': books})

def infotest(request):
    return render(request, 'filmreply.html')