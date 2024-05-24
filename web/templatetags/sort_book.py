from django import template
from web.models import Genre

register = template.Library()

@register.filter
def sort_by_book_count(genres, books):
    genre_count = {}
    for genre in genres:
        genre_books = [book for book in books if genre in book.genres.all()]
        genre_count[genre] = len(genre_books)
    sorted_genres = sorted(genre_count, key=genre_count.get, reverse=True)
    return sorted_genres