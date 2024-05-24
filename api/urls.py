from django.urls import path, include

from .views import user, movies, books, ai

urlpatterns = [
    path('user/', include('dj_rest_auth.urls')),
    path('user/registration/', include('dj_rest_auth.registration.urls')),
    path('user/data/', user.get_user_data),
    path('user/ratings/', user.get_ratings_by_media_type),
    path('user/ratings/set/', user.change_media_rating),
    path('user/genres/update/', user.update_preferred_genres),
    path('user/review/', user.update_media_review),

    path('user/recommendations', ai.get_user_recommendations),
    
    path('movies/details/', movies.get_movie_details),
    path('movies/details/bulk/', movies.get_movie_details_bulk),
    path('movies/search/', movies.search_movies),
    path('movies/upcoming/', movies.get_upcoming_movies),
    path('movies/popular/', movies.get_popular_movies),
    path('movies/create/', movies.create_movie),

    path('books/details/', books.get_book_details),
    path('books/search/', books.search_books),
    path('books/upcoming/', books.get_popular_books),
    path('books/popular/', books.get_popular_books),
    path('books/create/', books.create_book),
    path('books/summarize', ai.summarize_book_description)
]
