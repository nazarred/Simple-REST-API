FROM python:3.5


ENV PYTHONUNBUFFERED 1
ENV DOCKER_CONTAINER 1
RUN mkdir -p /opt/services/api
WORKDIR /opt/services/api

COPY ./requirements.txt /opt/services/api/requirements.txt
RUN pip install -r requirements.txt

COPY . /opt/services/api

EXPOSE 8000
