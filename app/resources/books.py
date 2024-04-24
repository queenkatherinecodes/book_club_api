from flask import jsonify
from services.google_books import GoogleBooksService
from services.gemini import GenAIService
from services.open_library import OpenLibraryService

class BooksResource:
    books = []  # Placeholder for storing books in memory

    @staticmethod
    def get_books():
        return jsonify(BooksResource.books), 200

    @staticmethod
    def create_book(book_data):
        title = book_data.get('title')
        isbn = book_data.get('ISBN')
        genre = book_data.get('genre')

        if not title or not isbn or not genre:
            return jsonify({"error": "Missing required fields"}), 400

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
    def replace_unknown(value):
        return "missing" if value == "unknown" else value