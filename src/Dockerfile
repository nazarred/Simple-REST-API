FROM python:3.5


ENV PYTHONUNBUFFERED 1
ENV DOCKER_CONTAINER 1
RUN mkdir -p /opt/services/api/src
WORKDIR /opt/services/api/src

COPY ./requirements.txt /opt/services/api/src/requirements.txt
RUN pip install -r requirements.txt

COPY . /opt/services/api/src

#RUN python manage.py collectstatic

EXPOSE 8000

#CMD ["gunicorn", "--chdir", "simple_api", "--bind", ":8000", "simple_api.wsgi:application"]
