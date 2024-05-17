from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from web.models import Movie
from api.views.ai import get_user_recommendations
from api.views.user import _get_user_watched
from rest_framework.renderers import JSONRenderer
from api.serializers import RatingSerializer

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
    ratings = request.user.profile.ratings.all()
    ratings_data = RatingSerializer(ratings, many=True).data
    ratings_json = JSONRenderer().render(ratings_data)
    ratings_json_str = ratings_json.decode('utf-8')
    return render(request, 'account.html', {'ratings': ratings_json_str})

@login_required
def favmovies(request):
    fav_movies = request.user.profile.ratings.filter(favorited=True, media__movie__isnull=False).select_related('media').prefetch_related('media__movie__directors')
    return render(request, 'favmovies.html', {'fav_movies': fav_movies})

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
