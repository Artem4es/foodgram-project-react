FROM python:3.7-slim

WORKDIR /app

COPY /requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY /food .
RUN pwd
CMD ["gunicorn", "food.wsgi:application", "--bind", "0:8000" ]