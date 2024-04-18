from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
import requests
from web.models import Book, Person, Genre
import json

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

def _get_book_details(id=None):
    if id:
        response = requests.get(f"{GOOGLE_BOOKS_API_URL}/{id}")
        if response.status_code == 200:
            return response.json()
    return None

def get_book_by_id(book_id):
    GOOGLE_BOOKS_API_URL = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    response = requests.get(GOOGLE_BOOKS_API_URL)

    if response.status_code == 200:
        return response.json()
    else:
        return None

@api_view(['GET'])
@permission_classes([AllowAny])
def get_book_details(request):
    id = request.query_params.get('id')
    if id:
        book_info = _get_book_details(id=id)
        if book_info:
            return Response(book_info)
        else:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'Bad Request: Please provide an id'}, status=status.HTTP_400_BAD_REQUEST)

def _search_books(query=None):
    if query:
        response = requests.get(GOOGLE_BOOKS_API_URL, params={"q": query})
        if response.status_code == 200:
            return response.json().get('items', [])
    return []

@api_view(['GET'])
@permission_classes([AllowAny])
def search_books(request):
    query = request.query_params.get('query')
    if query:
        books = _search_books(query=query)
        return Response(books)
    else:
        return Response({'error': 'Bad Request: Please provide a query'}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([AllowAny])
def get_new_books(request):
    response = requests.get(GOOGLE_BOOKS_API_URL, params={"orderBy": "newest"})
    if response.status_code == 200:
        return Response(response.json().get('items', []))
    else:
        return Response({'error': 'Failed to retrieve new books'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_popular_books(request):
    try:
        genre = request.query_params.get('genre', 'book')  # получаем параметр жанра, по умолчанию 'book'
        sort_by = request.query_params.get('sort_by', 'relevance')  # получаем параметр сортировки, по умолчанию 'relevance'
        
        # Делаем первый запрос на 40 книг
        response1 = requests.get(GOOGLE_BOOKS_API_URL, params={"q": genre, "orderBy": sort_by, "maxResults": 40})
        if response1.status_code != 200:
            return Response({'error': 'Не удалось получить популярные книги', 'response': response1.json()}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Делаем второй запрос на оставшиеся 10 книг
        response2 = requests.get(GOOGLE_BOOKS_API_URL, params={"q": genre, "orderBy": sort_by, "maxResults": 10, "startIndex": 40})
        if response2.status_code != 200:
            return Response({'error': 'Не удалось получить популярные книги', 'response': response2.json()}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Объединяем результаты двух запросов
        res = response1.json().get('items', []) + response2.json().get('items', [])
        res = [book for book in res if 'imageLinks' in book['volumeInfo']]  # фильтруем книги без изображений

        updated_res = []
        for book in res:
            volume_info = book['volumeInfo']
            # Создаем новый словарь только с нужными полями
            new_book = {
                'id': book['id'],
                'title': volume_info.get('title'),
                'authors': volume_info.get('authors'),
                'publisher': volume_info.get('publisher'),
                'publishedDate': volume_info.get('publishedDate'),
                'previewLink': volume_info.get('previewLink'),
                'infoLink': volume_info.get('infoLink'),
                'canonicalVolumeLink': volume_info.get('canonicalVolumeLink')
            }
            # Добавляем новый словарь в список
            updated_res.append(new_book)

        return Response({"results": updated_res, "result_count": len(updated_res)})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# https://developers.google.com/books/docs/v1/using?hl=ru#RetrievingVolume
@api_view(["POST"])
@permission_classes([AllowAny])
def create_book(request):
    # Extract book id from the request
    book_id = request.data.get("id")
    if not book_id:
        return Response({"error": "Book ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if book already exists to avoid duplicates
    if Book.objects.filter(id=book_id).exists():
        return Response({"error": "Book with this ID already exists"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create a new Book instance with the provided ID
    book = Book(id=book_id)

    # Extract additional book details from the get_book_details API
    book_details = _get_book_details(id=book_id)
    if not book_details:
        return Response({"error": "Failed to retrieve book details"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Set the book details
    book.title = book_details.get("volumeInfo").get("title")
    book.release_date = book_details.get("volumeInfo").get("publishedDate")
    book.description = book_details.get("volumeInfo").get("description")
    book.pages = book_details.get("volumeInfo").get("pageCount")
    book.thumbnail = book_details.get("volumeInfo").get("imageLinks").get("thumbnail")
    
    book.save()

    for author in book_details.get("volumeInfo").get("authors"):
        author_obj, created = Person.objects.get_or_create(name=author) # google does not provide a url
        book.authors.add(author_obj)
        
    # well books have category not genre but who cares
    if book_details.get("mainCategory"):
        genre, created = Genre.objects.get_or_create(name=book_details.get("mainCategory"))
        book.genres.add(genre)
    
    return Response({"message": "Book created successfully", "book_id": book.id}, status=status.HTTP_201_CREATED)