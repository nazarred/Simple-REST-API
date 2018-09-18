FROM nginx:latest


ENV PYTHONUNBUFFERED 1

WORKDIR /etc/nginx/
RUN rm ./conf.d/default.conf
COPY ./conf.d ./conf.d
