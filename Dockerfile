FROM python:3.5


ENV PYTHONUNBUFFERED 1
ENV DOCKER_CONTAINER 1
#ENV DJANGO_CONFIGURATION='Dev' \
#    DJANGO_SETTINGS_MODULE='simple_api.settings' \
#    DJANGO_EMAIL_HOST='smtp.sendgrid.net' \
#    DJANGO_EMAIL_PORT='587' \
#    DJANGO_EMAIL_HOST_USER='apikey' \
#    DJANGO_EMAIL_HOST_PASSWORD='xxxxx' \
#    DJANGO_CLEARBIT_KEY='xxxx' \
#    DJANGO_HUNTER_API_KEY='xxxx'

WORKDIR /app

COPY . /app
RUN pip install -r requirements.txt
