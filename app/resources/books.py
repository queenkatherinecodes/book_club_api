from flask import jsonify
from services.google_books import GoogleBooksService

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

        book = {
            'title': title,
            'authors': google_books_data['authors'],
            'ISBN': isbn,
            'genre': genre,
            'publisher': google_books_data['publisher'],
            'publishedDate': google_books_data['publishedDate'],
            'id': str(len(BooksResource.books) + 1)
        }

        BooksResource.books.append(book)

        return jsonify({"id": book['id']}), 201

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