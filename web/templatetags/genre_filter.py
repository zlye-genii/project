from django import template
from web.models import Genre  # Make sure to import the Genre model

register = template.Library()

@register.filter(name='filter_genre')
def filter_genre(movies, genre):
    """Filter movies by a given genre."""
    return [movie for movie in movies if genre in movie.genres.all()]