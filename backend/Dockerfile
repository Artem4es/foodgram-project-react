FROM python:3.9-slim
WORKDIR /app
COPY /backend/requirements.txt .
RUN apt-get update
RUN apt-get install libcairo2-dev pkg-config python3.9-dev gcc -y
RUN pip install -r requirements.txt --no-cache-dir
COPY /backend/food .
CMD ["gunicorn", "food.wsgi:application", "--bind", "0:8000" ]