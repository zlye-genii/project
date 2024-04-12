from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Movie

# Create your views here.

from django.http import HttpResponse

def index(request):
    return render(request, 'main.html')

def movielist(request):
    movies = Movie.objects.all().prefetch_related('genres', 'directors')
    return render(request, 'movielist.html', {'movies': movies})