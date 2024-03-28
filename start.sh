#!/bin/bash

ps aux | grep gunicorn

echo "kill gunicorn now..."

pkill gunicorn

gunicorn -w 4 -b 127.0.0.1:5001 -D run:app

ps aux | grep gunicorn
