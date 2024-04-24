import google.generativeai as genai
import os

class GenAIService:
    @staticmethod
    def get_book_summary(book_name, author_name):
        # Set up the API key
        genai.configure(api_key=os.environ['API_KEY'])
        # Create the prompt
        prompt = f'Summarize the book "{book_name}" by {author_name} in 5 sentences or less.'
        # Set up the model parameters
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.candidates[0].content.parts[0].text
