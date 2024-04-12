from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from web.models import Movie

# Create your views here.

def login(request):
    if request.user.is_authenticated:
        return redirect('account')
    return render(request, 'login.html')

@login_required
def account(request):
    return render(request, 'account.html', {'user': request.user})

@login_required
def favorites(request):
    movies = Movie.objects.all().prefetch_related('genres', 'directors') # temp for testing
    favorites = request.user.profile.ratings.filter(favorited=True)
    return render(request, 'favorites.html', {'movies': movies, 'favorites': favorites})