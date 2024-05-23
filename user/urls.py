from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path('favorites/movies', views.favmovies, name='favmovies'),
    path('favorites/books', views.favbooks, name='favbooks'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('recommendations/result/', views.selgenerated),
    path('watched/', views.watched),
    path('read/', views.read)
]