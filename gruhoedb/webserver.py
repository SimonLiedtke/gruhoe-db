import os

from flask import Flask, abort, jsonify, render_template, request

from gruhoedb import get_cells
from gruhoedb.models import Pick

BAD_REQUEST = 400
NOT_FOUND = 404

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    artist_query = request.args.get('artist', '')
    album_query = request.args.get('album', '')

    cells = [
        pick._asdict() for pick in get_all_cells() if matches_search(pick, artist_query, album_query)
    ]

    return jsonify(cells[:int(os.getenv('MAX_SEARCH_RESULTS'))])


@app.route('/count')
def count_all():
    return str(len(get_all_cells()))


def matches_search(pick, artist_query, album_query):
    if artist_query and not album_query:
        return artist_query.lower() in pick.artist.lower()
    if not artist_query and album_query:
        return album_query.lower() in pick.album.lower()
    return album_query.lower() in pick.album.lower() or artist_query.lower() in pick.artist.lower()


def get_all_cells():
    return [Pick(*row) for row in get_cells(os.getenv('GOOGLEAPIKEY'), os.getenv('SPREADSHEET'))][1:]
