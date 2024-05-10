from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("movies/", views.movielist),
    path("books/", views.booklist)
]