FROM python:3.12
WORKDIR /app/resources/loans
COPY . .
RUN pip install flask pymongo requests
EXPOSE 5000
CMD ["python", "main.py"]