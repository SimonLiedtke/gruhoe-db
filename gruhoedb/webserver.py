from datetime import date
from enum import StrEnum, auto
import os

from babel.dates import format_date
from flask import Flask, abort, jsonify, redirect, render_template, request

from gruhoedb.repos import PickRepository

BAD_REQUEST = 400
NOT_FOUND = 404

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')


class OutputFormat(StrEnum):
    HTML = auto()
    JSON = auto()


def date_format(date, locale):
    return format_date(date, locale=locale, format='short')


@app.route('/favicon.ico')
def favicon():
    return redirect('/static/favicon.ico')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    query = request.args.get('query', '')
    from_ = get_date_from_input(request.args.get('from')) or date(1, 1, 1)
    to = get_date_from_input(request.args.get('to')) or date.today()

    results = list(PickRepository(os.getenv('DB_CONNECTION')).search(query, from_, to))

    outputformat = request.args.get('outputformat')

    locale = (request.accept_languages.best or 'en')[:2]

    if outputformat == OutputFormat.HTML:
        return render_template(
            'index.html',
            query=query,
            search_results=results,
            date_format=date_format,
            locale=locale)
    elif outputformat == OutputFormat.JSON:
        return jsonify(results)
    else:
        return abort(BAD_REQUEST)


@app.route('/count')
def count_all():
    return str(PickRepository(os.getenv('DB_CONNECTION')).count())


def matches_search(pick, artist_query, album_query):
    if artist_query and not album_query:
        return artist_query.lower() in pick.artist.lower()
    if not artist_query and album_query:
        return album_query.lower() in pick.album.lower()
    return album_query.lower() in pick.album.lower() or artist_query.lower() in pick.artist.lower()


def get_date_from_input(input_):
    try:
        return date.fromisoformat(input_)
    except ValueError:
        return None


def get_all_cells():
    return PickRepository(os.getenv('DB_CONNECTION')).get_all()
