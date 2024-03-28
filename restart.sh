#!/bin/bash

ps aux | grep gunicorn

echo "reload now..."
pkill -HUP -f gunicorn

ps aux | grep gunicorn