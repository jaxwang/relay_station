#!/bin/bash

pkill gunicorn
gunicorn -w 5 -b 127.0.0.1:5001 -D run:app
