from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from api.views.ai import get_user_recommendations

# Create your views here.

def login(request):
    return render(request, 'login.html')

@login_required
def account(request):
    return render(request, 'account.html', {'user': request.user})

@login_required
def recom(request):
    recommendations = get_user_recommendations(request)
    return render(request, 'recom.html', {'recommendations': recommendations})