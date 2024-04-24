import requests

class OpenLibraryService:
    BASE_URL = "https://openlibrary.org"

    @staticmethod
    def get_book_languages(isbn):
        url = f"{OpenLibraryService.BASE_URL}/search.json"
        params = {
            "q": isbn,
            "fields": "language"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get("docs"):
            languages = data["docs"][0].get("language")
            if languages:
                return languages

        return ["missing"]