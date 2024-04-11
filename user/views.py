from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.

def login(request):
    return render(request, 'login.html')

@login_required
def account(request):
    return render(request, 'account.html', {'user': request.user})

@login_required
def favorites(request):
    return render(request, 'favorites.html')