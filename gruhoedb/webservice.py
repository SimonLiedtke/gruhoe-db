import os

from flask import Flask, abort

from gruhoedb import get_cells

BAD_REQUEST = 400
NOT_FOUND = 404

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')


@app.route('/')
def index():
    abort(NOT_FOUND)


@app.route('/count')
def count_all():
    # subtract 1 to not count the header row
    return str(len(get_cells(os.getenv('GOOGLEAPIKEY'), os.getenv('SPREADSHEET'))) - 1)
