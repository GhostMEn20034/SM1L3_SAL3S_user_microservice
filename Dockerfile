# pull official base image
FROM python:3.10.12

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /app

# install psycopg2 dependencies
RUN apt-get update \
    && apt-get install libpq-dev gcc python3-dev musl-dev -y

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .