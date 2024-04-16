from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
import requests

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

def _get_book_details(id=None):
    if id:
        response = requests.get(f"{GOOGLE_BOOKS_API_URL}/{id}")
        if response.status_code == 200:
            return response.json()
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
    response = requests.get(GOOGLE_BOOKS_API_URL, params={"orderBy": "relevance"})
    if response.status_code == 200:
        return Response(response.json().get('items', []))
    else:
        return Response({'error': 'Failed to retrieve popular books'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    book.authors = book_details.get("volumeInfo").get("authors")
    book.published_date = book_details.get("volumeInfo").get("publishedDate")
    book.description = book_details.get("volumeInfo").get("description")
    book.page_count = book_details.get("volumeInfo").get("pageCount")
    book.thumbnail_url = book_details.get("volumeInfo").get("imageLinks").get("thumbnail")
    
    book.save()
    
    return Response({"message": "Book created successfully", "book_id": book.id}, status=status.HTTP_201_CREATED)