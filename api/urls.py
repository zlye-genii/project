from django.urls import path, include

from .views import user, movies, book

urlpatterns = [
    path('user/', include('dj_rest_auth.urls')),
    path('user/registration/', include('dj_rest_auth.registration.urls')),
    path('user/data/', user.get_user_data),
    path('user/favorites/add', user.add_movie_to_favorites),
    path('user/favorites/remove', user.remove_movie_from_favorites),
    path('movies/details', movies.get_movie_details),
    path('movies/search', movies.search_movies),
    path('movies/upcoming', movies.get_upcoming_movies),
    path('movies/popular', movies.get_popular_movies),
    path('movies/create', movies.create_movie) 
    path('books/details', book.get_book_details),
    path('books/search', book.search_books),
    path('books/upcoming', book.get_upcoming_books),
    path('books/popular', book.get_popular_books),
    path('books/create', book.create_book),
]
]