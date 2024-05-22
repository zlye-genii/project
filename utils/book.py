from rest_framework import status
from web.models import Book, Genre, Person
from rest_framework.response import Response
from api.serializers import BookSerializer
from PIL import Image
import os
import requests
from io import BytesIO
import json
from datetime import datetime
from utils.translate import translate

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

def compress_book_cover(book_id, cover_url, regen=False):
    img_path = os.path.join('static', 'bookcovers', os.path.basename(book_id) + '.png')
    if not regen and img_path:
        return img_path
    response = requests.get(cover_url)
    img = Image.open(BytesIO(response.content))
    img = img.resize((100, 250), Image.ANTIALIAS)

    img.save(img_path)

    return img_path.replace('\\', '/')

def _get_book_details(id, db_only=True):
    book = Book.objects.filter(id=id).first()
    if not book:
        if db_only:
            results, stat = _create_book(id)
            if stat != status.HTTP_201_CREATED:
                return Response(results, status=stat)
            book = Book.objects.filter(id=id).first()
        else:
            response = requests.get(f"{GOOGLE_BOOKS_API_URL}/{id}")
            results = response.json() if response.status_code == 200 else None
        
    return results if not book else BookSerializer(book).data

def _format_published_date(date_str):
    if not date_str:
        return None
    date_str = date_str.replace("“", '').replace('”', '')
    # Try to parse the date with the complete format
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        # If the day is missing (format YYYY-MM)
        try:
            return datetime.strptime(date_str, "%Y-%m").date().replace(day=1)
        except ValueError:
            # If only the year is present (format YYYY)
            try:
                return datetime.strptime(date_str, "%Y").date().replace(month=1, day=1)
            except ValueError:
                # If the date is not in a valid format, return None or a default date
                return None

def _create_book(book_id):
    if Book.objects.filter(id=book_id).exists():
        return {"error": "Book with this ID already exists"}, status.HTTP_400_BAD_REQUEST
    
    book = Book(id=book_id)

    book_details = _get_book_details(id=book_id, db_only=False)
    if not book_details:
        return {"error": "Failed to retrieve book details"}, status.HTTP_500_INTERNAL_SERVER_ERROR
    if 'status' in book_details:
        if book_details['status'] == 404:
            return {"error": "Book not found"}, status.HTTP_404_NOT_FOUND
    authors = book_details.get("volumeInfo").get("authors")
    categories = book_details.get("volumeInfo").get("categories")
    translated = translate([book_details.get("volumeInfo").get("title"), book_details.get("volumeInfo").get("description")])
    book.title = translated[0]
    book.release_date = _format_published_date(book_details.get("volumeInfo").get("publishedDate"))
    book.description = translated[1]
    book.pages = book_details.get("volumeInfo").get("pageCount")
    if book_details.get("volumeInfo").get("imageLinks"):
        book.thumbnail = book_details.get("volumeInfo").get("imageLinks").get("thumbnail")
    
    book.save()

    if authors:
        for author_name in authors:
            author, created = Person.objects.get_or_create(name=author_name)
            book.authors.add(author)
    if categories:
        for category_name in categories:
            category, created = Genre.objects.get_or_create(name=category_name)
            book.genres.add(category)
    
    return {"message": "Book created successfully", "book_id": book.id}, status.HTTP_201_CREATED