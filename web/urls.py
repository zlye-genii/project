from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("movies/", views.movielist),
    path("books/", views.booklist),
    path('movie/details/<movie_id>/', views.moviedetails),
    path('book/details/<book_id>/', views.bookdetails),
    path('search/', views.search),
    path('search_results/', views.search_results, name='search_results')
]