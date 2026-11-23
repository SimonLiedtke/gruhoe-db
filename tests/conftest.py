import os

# webserver.py reads the secret key at import time, so it must be set before any test imports it.
os.environ.setdefault('FLASK_SECRET_KEY', 'test-secret-key')
