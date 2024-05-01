from flask import Flask, jsonify, request
from resources.books import BooksResource
from resources.ratings import RatingsResource

app = Flask(__name__)

@app.route('/books', methods=['GET', 'POST'])
def handle_books():
    if request.method == 'GET':
        query_string = request.query_string.decode('utf-8')
        return BooksResource.get_books(query_string)
    elif request.method == 'POST':
        if not request.is_json:
            return jsonify("Unsupported Media Type"), 415
        book_data = request.json
        new_book, status = BooksResource.create_book(book_data)
        if status == 201:
            book_id = new_book.json['id']
            book_title = book_data['title']
            RatingsResource.add_new_rating(book_id, book_title)
        return new_book, status

@app.route('/books/<string:book_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_book(book_id):
    if request.method == 'GET':
        return BooksResource.get_book(book_id)
    elif request.method == 'PUT':
        if not request.is_json:
            return jsonify("Unsupported Media Type"), 415
        book_data = request.json
        updated_book, status = BooksResource.update_book(book_id, book_data)
        book_title = book_data['title']
        RatingsResource.update_rating(book_id, book_title)
        return updated_book, status
    elif request.method == 'DELETE':
        RatingsResource.delete_rating(book_id)
        return BooksResource.delete_book(book_id)

@app.route('/ratings', methods=['GET'])
def get_ratings():
    query_string = request.query_string.decode('utf-8')
    ratings_list = RatingsResource.get_ratings(query_string)
    return jsonify(ratings_list)

@app.route('/ratings/<book_id>', methods=['GET'])
def get_rating(book_id):
    rating_data = RatingsResource.get_rating(book_id)
    if 'error' in rating_data:
        return jsonify(rating_data), rating_data['error']
    return jsonify(rating_data)

@app.route('/ratings/<book_id>/values', methods=['POST'])
def add_rating(book_id):
    rating_data = request.get_json()
    result = RatingsResource.add_rating(book_id, rating_data)
    if 'error' in result:
        return jsonify(result), result['error']
    return jsonify(result)
    
@app.route('/top', methods=['GET'])
def get_top_books():
    top_books = RatingsResource.get_top_books()
    return jsonify(top_books)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)