from resources.books import BooksResource
import urllib.parse

class RatingsResource:
    ratings = []  # List to store ratings data

    @staticmethod
    def get_ratings(query_string):
        if not query_string:
            return RatingsResource.ratings
        query_string = urllib.parse.unquote_plus(query_string)
        filtered_ratings = RatingsResource.ratings.copy()
        if '=' in query_string:
            field, value = query_string.split('=', 1)
            if field == 'id':
                filtered_ratings = [rating for rating in filtered_ratings if rating['id'] == value]
            else:
                return {'error': 'Invalid query parameter'}, 422
        return filtered_ratings

    @staticmethod
    def get_rating(book_id):
        rating = next((rating for rating in RatingsResource.ratings if rating['id'] == book_id), None)
        if rating:
            return rating
        else:
            return {'error': 'Book not found'}, 404

    @staticmethod
    def add_new_rating(book_id, book_title):
        new_rating = {
            'values': [],
            'average': 0,
            'title': book_title,
            'id': book_id
        }
        RatingsResource.ratings.append(new_rating)

    @staticmethod
    def add_rating(book_id, rating_data):
        try:
            value = rating_data['value']
            if value < 1 or value > 5:
                return {'error': 'Rating value must be between 1 and 5'}, 422
        except KeyError:
            return {'error': 'Missing rating value'}, 422

        # Find the book in the books resource
        book = next((book for book in BooksResource.books if book['id'] == book_id), None)
        if not book:
            return {'error': 'Book not found'}, 404

        # Check if the book already exists in the ratings resource
        rating = next((rating for rating in RatingsResource.ratings if rating['id'] == book_id), None)

        if rating:
            # Book already exists, update the values and average
            rating['values'].append(value)
            rating['average'] = sum(rating['values']) / len(rating['values'])
        else:
            # Book doesn't exist, create a new entry
            new_rating = {
                'values': [value],
                'average': value,
                'title': book['title'],
                'id': book_id
            }
            RatingsResource.ratings.append(new_rating)

        return {'average': rating['average'] if rating else new_rating['average']}

    @staticmethod
    def update_rating(book_id, new_title):
        rating = next((rating for rating in RatingsResource.ratings if rating['id'] == book_id), None)
        if rating:
            rating['title'] = new_title
    
    @staticmethod
    def delete_rating(book_id):
        rating = next((rating for rating in RatingsResource.ratings if rating['id'] == book_id), None)
        if rating:
            RatingsResource.ratings.remove(rating)

    def get_top_books():
        valid_ratings = [rating for rating in RatingsResource.ratings if len(rating['values']) >= 3]
        sorted_ratings = sorted(valid_ratings, key=lambda rating: rating['average'], reverse=True)

        top_books = []
        for rating in sorted_ratings:
            top_book = {
                'id': rating['id'],
                'title': rating['title'],
                'average': rating['average']
            }
            top_books.append(top_book)

        return top_books[:3]