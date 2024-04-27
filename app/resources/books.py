import urllib.parse
from flask import jsonify
from services.google_books import GoogleBooksService
from services.gemini import GenAIService
from services.open_library import OpenLibraryService

VALID_GENRES = ['Fiction', 'Children', 'Biography', 'Science', 'Science Fiction', 'Fantasy', 'Other']

class BooksResource:
    books = []  # Placeholder for storing books in memory

    @staticmethod
    def get_books(query_string):
        if not query_string:
            return jsonify(BooksResource.books), 200

        query_string = urllib.parse.unquote_plus(query_string)
        query_params = query_string.split('&')
        filtered_books = BooksResource.books.copy()

        for param in query_params:
            if param.startswith("language contains"):
                param_parts = param.split()
                if len(param_parts) != 3:
                    return jsonify({"error": "Invalid query format for querying by language"}), 422

                _, _, language = param_parts
                if language not in ["heb", "eng", "spa", "chi"]:
                    return jsonify({"error": "Invalid language code"}), 422

                filtered_books = [
                    book for book in filtered_books
                    if language in book.get('languages', [])
                ]
            else:
                if '=' not in param:
                    continue  # Skip parameters without '='
                field, value = param.split('=', 1)
                if field not in ["summary", "language"]:
                    filtered_books = [
                        book for book in filtered_books
                        if book.get(field) == value
                    ]
        return jsonify(filtered_books), 200
    
    @staticmethod
    def create_book(book_data):
        title = book_data.get('title')
        isbn = book_data.get('ISBN')
        genre = book_data.get('genre')

        if not title or not isbn or not genre:
            return jsonify({"error": "Missing required fields"}), 400
        existing_book = next((book for book in BooksResource.books if book['ISBN'] == isbn), None)
        if existing_book:
            return jsonify({"error": "Book with the provided ISBN already exists"}), 422
        if not BooksResource.is_valid_genre(genre):
            return jsonify({"error": "Invalid Genre"}), 422
        
        google_books_data = GoogleBooksService.get_book_details(isbn)
        if not google_books_data:
            return jsonify({"error": "Book not found in Google Books API"}), 404

        authors = BooksResource.replace_unknown(google_books_data['authors'])
        first_author = authors.split(',')[0] if ',' in authors else authors

        book = {
            'title': title,
            'authors': authors,
            'ISBN': isbn,
            'genre': genre,
            'publisher': BooksResource.replace_unknown(google_books_data['publisher']),
            'publishedDate': BooksResource.replace_unknown(google_books_data['publishedDate']),
            'id': str(len(BooksResource.books) + 1),
            'summary': GenAIService.get_book_summary(title, first_author),
            'languages': OpenLibraryService.get_book_languages(isbn)
        }

        BooksResource.books.append(book)
        return jsonify(book), 201

    @staticmethod
    def get_book(book_id):
        book = next((book for book in BooksResource.books if book['id'] == book_id), None)
        if not book:
            return jsonify({"error": "Book not found"}), 404
        return jsonify(book), 200

    @staticmethod
    def update_book(book_id, book_data):
        book = next((book for book in BooksResource.books if book['id'] == book_id), None)
        if not book:
            return jsonify({"error": "Book not found"}), 404

        required_fields = ['title', 'authors', 'ISBN', 'genre', 'publisher', 'publishedDate', 'languages']
        missing_fields = [field for field in required_fields if field not in book_data]

        if missing_fields:
            return jsonify({"error": "Missing required fields"}), 422

        if 'genre' in book_data and not BooksResource.is_valid_genre(book_data['genre']):
            return jsonify({"error": "Invalid genre"}), 422
        
        book.update(book_data)
        return jsonify({"id": book_id}), 200

    @staticmethod
    def delete_book(book_id):
        book = next((book for book in BooksResource.books if book['id'] == book_id), None)
        if not book:
            return jsonify({"error": "Book not found"}), 404

        BooksResource.books.remove(book)
        return jsonify({"id": book_id}), 200
    
    @staticmethod
    def is_valid_genre(genre):
        return genre in VALID_GENRES
    
    @staticmethod
    def replace_unknown(value):
        return "missing" if value == "unknown" else value