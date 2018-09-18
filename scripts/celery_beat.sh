#!/bin/bash

cd /app/src
celery -A simple_api beat -l info