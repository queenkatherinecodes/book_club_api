from flask import Flask, jsonify, request
from loans import get_loans, create_loan, get_loan, delete_loan

app = Flask(__name__)

@app.route('/loans', methods=['GET', 'POST'])
def handle_loans():
    if request.method == 'GET':
        query_string = request.query_string.decode('utf-8')
        return get_loans(query_string)
    elif request.method == 'POST':
        if not request.is_json:
            return jsonify("Unsupported Media Type"), 415
        loan_data = request.json
        new_loan, status = create_loan(loan_data)
        return new_loan, status

@app.route('/loans/<string:loan_id>', methods=['GET', 'DELETE'])
def handle_loan(loan_id):
    if request.method == 'GET':
        return get_loan(loan_id)
    elif request.method == 'DELETE':
        return delete_loan(loan_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)