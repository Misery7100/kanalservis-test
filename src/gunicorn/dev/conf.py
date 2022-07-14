"""Gunicorn *development* config file"""

import os

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "backend.wsgi:application"
# The granularity of Error log outputs
loglevel = "debug"
# The number of worker processes for handling requests
workers = 4
# The socket to bind
bind = "0.0.0.0:8000"
# Restart workers when code changes (development only!)
reload = True
# Write access and error info to log file
#accesslog = errorlog = os.path.join(BASE_DIR, "dev.log")
# Redirect stdout/stderr to log file
capture_output = True
# PID file so you can easily fetch process ID (???)
#pidfile = "/var/run/gunicorn/dev.pid"

# Daemonize the Gunicorn process (detach & enter background)
# daemon = False