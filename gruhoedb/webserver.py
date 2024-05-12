from datetime import date
from enum import StrEnum, auto
import os

from babel.dates import format_date
from flask import Flask, abort, jsonify, redirect, render_template, request
from flask.json import dumps as dump_json

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
    to = get_date_from_input(request.args.get('to')) or date(9999, 12, 31)

    repo = PickRepository(os.getenv('DB_CONNECTION'))

    if not query:
        results = repo.get_all()
    else:
        results = repo.search(query, from_, to)

    outputformat = request.args.get('outputformat')

    locale = (request.accept_languages.best or 'en')[:2]

    if outputformat == OutputFormat.HTML:
        return render_template(
            'index.html',
            query=query,
            search_results=list(results),
            date_format=date_format,
            locale=locale)
    elif outputformat == OutputFormat.JSON:
        return jsonify(list(results))
    else:
        return abort(BAD_REQUEST)


@app.route('/stats')
def stats():
    repo = PickRepository(os.getenv('DB_CONNECTION'))
    stats_all = dump_json(list(repo.fetch_statistics(None)))
    stats_current_year = dump_json(list(repo.fetch_statistics(date.today().year)))
    return render_template('stats.html', data_all=stats_all, data_year=stats_current_year)


@app.route('/stats/<int:year>')
def fetch_stats(year):
    return show_stats(year)


def show_stats(year):
    repo = PickRepository(os.getenv('DB_CONNECTION'))
    return render_template('stats.html', data=dump_json(list(repo.fetch_statistics(year))))


def get_date_from_input(input_):
    try:
        return date.fromisoformat(input_)
    except ValueError:
        return None
