from django.contrib import admin
from .models import Movie, Genre, Book, Rating

# Register your models here.
admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(Book)
admin.site.register(Rating)