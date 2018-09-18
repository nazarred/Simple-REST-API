FROM python:3.5


ENV PYTHONUNBUFFERED 1
ENV DOCKER_CONTAINER 1

WORKDIR /app

COPY . /app
RUN pip install -r requirements.txt
