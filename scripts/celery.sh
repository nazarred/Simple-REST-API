#!/bin/bash

cd /app/src
celery -A simple_api worker -l info