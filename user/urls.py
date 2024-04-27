from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path('account/', views.account, name='account'),
    path('favorites/', views.favorites, name='favorites'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('watched/', views.watched)
]