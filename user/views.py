from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from web.models import Media, Movie, Book
from api.views.user import _get_user_completed
from web.models import Genre


# Create your views here.

def login(request):
    if request.user.is_authenticated:
        return redirect('account')
    return render(request, 'login2.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('account')
    return render(request, 'register.html')

@login_required
def favmovies(request):
    fav_movies = request.user.profile.ratings.filter(favorited=True, media__movie__isnull=False).select_related('media').prefetch_related('media__movie__directors')
    return render(request, 'favmovies.html', {'fav_movies': fav_movies})

@login_required
def favbooks(request):
    fav_books = request.user.profile.ratings.filter(favorited=True, media__book__isnull=False).select_related('media').prefetch_related('media__book__authors')
    return render(request, 'favbooks.html', {'fav_books': fav_books})

@login_required
def favorites(request):
    return render(request, 'favorites.html')

@login_required
def recommendations(request):
    return render(request, 'personalselection.html')

@login_required
def watched(request):
    watched_movies = _get_user_completed(request.user.profile, 'movie')
    return render(request, 'watched.html', {'watched_movies': watched_movies})

@login_required
def read(request):
    read_books = _get_user_completed(request.user.profile, 'book')
    return render(request, 'read.html', {'read_books': read_books})

@login_required
def selgenerated(request):
    media_ids = request.GET.get('ids').split(',')
    generation_results = Media.objects.filter(id__in=media_ids)
    return render(request, 'selgenerated.html', {'generation_results': generation_results})

def genres_selection(request):
    genres = Genre.objects.all()
    return render(request, 'genrepref.html', {'genres': genres})