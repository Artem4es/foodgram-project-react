FROM python:3.9-slim

WORKDIR /app

COPY /requirements.txt .
RUN apt-get update
RUN apt-get install libcairo2-dev pkg-config python3-dev -y
RUN apt install gcc -y
RUN pip install pycairo
RUN pip install -r requirements.txt --no-cache-dir

COPY /food .
# gunicorn в requirements
RUN apt install gunicorn -y

# RUN echo python3 -m django --version
CMD ["gunicorn", "food.wsgi:application", "--bind", "0:8000" ]