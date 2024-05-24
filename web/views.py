from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Movie, Book, Genre, Rating
from utils.movie import poster_exists
from api.views.user import _get_user_favorites
from django.shortcuts import render
from api.views.movies import _search_movies
from api.views.books import _search_books
from rest_framework.request import Request
from api.views.movies import _search_movies
from api.views.books import _search_books
from utils.movie import _create_movie
from utils.book import _create_book
from api.serializers import MovieSerializer, BookSerializer
from rest_framework import status
import json
from django.shortcuts import redirect
import os

# Create your views here.

def index(request):
    one_month_ago = timezone.now() - timedelta(days=30)
    today = timezone.now()
    movies = Movie.objects.filter(release_date__gte=one_month_ago, release_date__lte=today).order_by('-imdb_rating')
    movies_with_posters = [movie for movie in movies if poster_exists(movie.thumbnail)]
    top_movies = movies_with_posters[:10]
    books = Book.objects.filter()
    top_books = books[:10]
    upcoming_movies = [movie for movie in Movie.objects.filter(release_date__gt=timezone.now()).order_by('release_date') if poster_exists(movie.thumbnail)][:10]
    if request.user.is_authenticated:
        favorites = _get_user_favorites(request.user.profile, "movie")
    else:
        favorites = None
    return render(request, 'novinki.html', {"movies": top_movies, "books": top_books, 'upcoming': upcoming_movies, 'favorites': json.dumps(favorites)})

def search_results(request):
    query = request.GET.get('query')
    media_type = request.GET.get('media_type', 'movie')
    media_objects = []

    if media_type == 'movie':
        search_results = _search_movies(query)
        for movie_data in search_results:
            movie_id = movie_data['id']
            results, status_code = _create_movie(movie_id)
            if status_code == status.HTTP_201_CREATED or status_code == status.HTTP_400_BAD_REQUEST:
                movie = Movie.objects.get(id=movie_id)
                media_objects.append(movie)
            else:
                continue
    elif media_type == 'book':
        search_results = _search_books(query)
        for book_data in search_results:
            book_id = book_data['id']
            results, status_code = _create_book(book_id)
            if status_code == status.HTTP_201_CREATED or status_code == status.HTTP_400_BAD_REQUEST:
                book = Book.objects.get(id=book_id)
                media_objects.append(book)
            else:
                continue

    serialized_media = MovieSerializer(media_objects, many=True) if media_type == 'movie' else BookSerializer(media_objects, many=True)
    context = {'search_results': serialized_media.data}
    return render(request, 'search.html', context)

def movielist(request):
    one_year_ago = timezone.now() - timedelta(days=365)
    today = timezone.now()
    genres = Genre.objects.all()
    mmovies = Movie.objects.prefetch_related('genres')
    movies = Movie.objects.filter(release_date__gte=one_year_ago, release_date__lte=today).exclude(imdb_rating__isnull=True).order_by('-imdb_rating')
    movies_with_posters = [movie for movie in movies if poster_exists(movie.thumbnail)]
    mmovies_with_posters = [movie for movie in mmovies if poster_exists(movie.thumbnail)]
    top_movies = movies_with_posters[:25]
    return render(request, 'movies.html', {'top_movies': top_movies, 'movies': mmovies_with_posters, 'genres': genres})

def booklist(request):
    genres = Genre.objects.all()
    books = Book.objects.all().prefetch_related('genres')
    books_w = [book for book in books if book.thumbnail != '/static/banner404.png']
    return render(request, 'books.html', {'books': books_w, 'genres': genres})

def moviedetails(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    if request.user.is_authenticated:
        user_profile = request.user.profile
        user_rating = Rating.objects.filter(profile=user_profile, media=movie).first()
    else:
        user_rating = None
    return render(request, 'filmreply.html', {'movie': movie, 'user_rating': user_rating})

def search(request):
    return render(request, 'search.html')

def bookdetails(request, book_id):
    book = Book.objects.get(id=book_id)
    if request.user.is_authenticated:
        user_profile = request.user.profile
        user_rating = Rating.objects.filter(profile=user_profile, media=book).first()
    else:
        user_rating = None
    return render(request, 'bookdetails.html', {'book': book, 'user_rating': user_rating})

def support(request):
    return redirect(os.getenv("SUPPORT"))
