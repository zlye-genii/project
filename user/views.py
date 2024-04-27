from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from web.models import Movie
from api.views.ai import get_user_recommendations
from api.views.user import _get_user_watched

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
def account(request):
    return render(request, 'account.html', {'user': request.user})

@login_required
def favorites(request):
    return render(request, 'favorites.html')

@login_required
def recommendations(request):
    recommendations = get_user_recommendations(request) # convert this to internal call?
    return render(request, 'recom.html', {'recommendations': recommendations})

@login_required
def watched(request):
    watched_movies = _get_user_watched(request.user.profile, 'movie')
    print(watched_movies)
    return render(request, 'prochit.html', {'watched_movies': watched_movies})
