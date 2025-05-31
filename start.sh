#!/bin/sh
cd /home/pi/TeXnique
/home/pi/.local/bin/gunicorn -w 1 --threads 100 -b 0.0.0.0:12345 "server:create_app()"
