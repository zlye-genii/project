from django.urls import path, include

from .views import user, movies, book, ai

urlpatterns = [
    path('user/', include('dj_rest_auth.urls')),
    path('user/registration/', include('dj_rest_auth.registration.urls')),
    path('user/data/', user.get_user_data),
    path('user/ratings/', user.get_ratings_by_media_type),
    path('user/ratings/set/', user.change_media_rating),

    path('user/recommendations', ai.get_user_recommendations),
    
    path('movies/details/', movies.get_movie_details),
    path('movies/search/', movies.search_movies),
    path('movies/upcoming/', movies.get_upcoming_movies),
    path('movies/popular/', movies.get_popular_movies),
    path('movies/create/', movies.create_movie),

    path('books/details', book.get_book_details),
    path('books/search', book.search_books),
    path('books/upcoming', book.get_new_books),
    path('books/popular', book.get_popular_books),
    path('books/create', book.create_book)
]
