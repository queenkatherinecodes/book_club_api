import requests
import urllib.parse
import uuid
from flask import jsonify
from pymongo import MongoClient

client = MongoClient('mongodb://mongo:27017/')
db = client.library

def get_loans(query_string):
    if not query_string:
        loans = list(db.loans.find({}, {'_id': False}))
        return jsonify(loans), 200

    query_params = urllib.parse.parse_qs(query_string)
    query_filter = {}
    for field, value in query_params.items():
        query_filter[field] = value[0]

    loans = list(db.loans.find(query_filter, {'_id': False}))
    return jsonify(loans), 200

def create_loan(loan_data):
    member_name = loan_data.get('memberName')
    isbn = loan_data.get('ISBN')
    loan_date = loan_data.get('loanDate')

    if not member_name or not isbn or not loan_date:
        return jsonify({"error": "Missing required fields"}), 400

    # Retrieve book details from the books microservice
    book_response = requests.get(f"http://localhost:8000/books?ISBN={isbn}")
    if book_response.status_code == 200:
        books_data = book_response.json()
        if not books_data:
            return jsonify({"error": "Book not found"}), 404
        book_data = books_data[0]
        title = book_data.get('title')
        book_id = book_data.get('id')
    else:
        return jsonify({"error": "Failed to retrieve book details"}), 500

    # Check if the book is already on loan
    if db.loans.find_one({"bookID": book_id}):
        return jsonify({"error": "Book is already on loan"}), 422

    # Check if the member already has 2 or more books on loan
    member_loans = list(db.loans.find({"memberName": member_name}))
    if len(member_loans) >= 2:
        return jsonify({"error": "Member already has 2 or more books on loan"}), 422

    # Generate a unique loan ID
    loan_id = str(uuid.uuid4())

    loan = {
        "memberName": member_name,
        "ISBN": isbn,
        "title": title,
        "bookID": book_id,
        "loanDate": loan_date,
        "loanID": loan_id
    }

    db.loans.insert_one(loan)
    return jsonify({'loanID': loan_id}), 201

def get_loan(loan_id):
    loan = db.loans.find_one({"loanID": loan_id}, {'_id': False})
    if not loan:
        return jsonify({"error": "Loan not found"}), 404
    return jsonify(loan), 200

def delete_loan(loan_id):
    result = db.loans.delete_one({"loanID": loan_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Loan not found"}), 404
    return jsonify({"loanID": loan_id}), 200