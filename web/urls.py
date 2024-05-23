from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    re_path(r'^favicon\.ico$', serve, {'path': 'favicon.ico', 'document_root': settings.BASE_DIR / 'static/logo'}),
    path("movies/", views.movielist),
    path("books/", views.booklist),
    path('movie/details/<movie_id>/', views.moviedetails),
    path('book/details/<book_id>/', views.bookdetails),
    path('search/', views.search),
    path('search/result/', views.search_results, name='search_results'),
    path('support/', views.support)
]