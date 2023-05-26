FROM python:3.9-slim
# ENV PYTHONUNBUFFERED 1
WORKDIR /app

COPY /requirements.txt .
RUN apt-get update
RUN apt-get install libcairo2-dev pkg-config python3.9-dev gcc -y
# sudo apt install ttf-mscorefonts-installer
# RUN apt install gcc -y
# RUN pip install pycairo
RUN pip install -r requirements.txt --no-cache-dir
#  --no-cache-dir
# RUN pip install Django
COPY /food .
# gunicorn в requirements
# RUN apt-get update
# RUN pip install gunicorn

# RUN echo python3 -m django --version

CMD ["gunicorn", "food.wsgi:application", "--bind", "0:8000" ]