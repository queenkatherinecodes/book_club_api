from flask import Flask, jsonify, request
from resources.books import BooksResource

app = Flask(__name__)

@app.route('/books', methods=['GET', 'POST'])
def handle_books():
    if request.method == 'GET':
        query_string = request.query_string.decode('utf-8')
        print(query_string)
        return BooksResource.get_books(query_string)
    elif request.method == 'POST':
        if not request.is_json:
            return jsonify("Unsupported Media Type"), 415
        return BooksResource.create_book(request.json)

@app.route('/books/<string:book_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_book(book_id):
    if request.method == 'GET':
        return BooksResource.get_book(book_id)
    elif request.method == 'PUT':
        if not request.is_json:
            return jsonify("Unsupported Media Type"), 415
        return BooksResource.update_book(book_id, request.json)
    elif request.method == 'DELETE':
        return BooksResource.delete_book(book_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)