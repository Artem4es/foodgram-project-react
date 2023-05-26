FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN apt-get update
RUN apt-get install libcairo2-dev pkg-config python3.9-dev gcc -y
RUN pip install -r requirements.txt --no-cache-dir
RUN ls
RUN pwd
COPY /food .
CMD ["gunicorn", "food.wsgi:application", "--bind", "0:8000" ]