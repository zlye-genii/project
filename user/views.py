from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from web.models import Movie
from api.views.ai import get_user_recommendations

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
    return render(request, 'favorites.html')

@login_required
def recommendations(request):
    recommendations = get_user_recommendations(request)
    return render(request, 'recom.html', {'recommendations': recommendations})