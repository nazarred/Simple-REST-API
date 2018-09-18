FROM nginx:latest


ENV PYTHONUNBUFFERED 1
ENV DOCKER_CONTAINER 1

WORKDIR /etc/nginx/
RUN rm /etc/nginx/conf.d/default.conf
COPY ./conf.d /etc/nginx/conf.d
