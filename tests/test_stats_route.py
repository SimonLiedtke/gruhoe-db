import json
from datetime import date
from unittest import mock

import pytest

from gruhoedb import webserver
from gruhoedb.models import Pick, StatsEntry


@pytest.fixture
def repo():
    with mock.patch.object(webserver, 'PickRepository') as repository_class:
        repo = repository_class.return_value
        repo.fetch_statistics.return_value = [StatsEntry(2023, 2, 4), StatsEntry(2023, 3, 1)]
        repo.get_all.return_value = [
            Pick(2024, 1, 3, 'A', 'A'),  # Wednesday
            Pick(2024, 1, 1, 'B', 'B'),  # Monday
            Pick(2024, 1, 8, 'C', 'C'),  # Monday
        ]
        yield repo


@pytest.fixture
def client():
    return webserver.app.test_client()


def test_index_renders_the_search_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert '<html' in response.get_data(as_text=True)


def test_favicon_redirects_to_the_static_file(client):
    response = client.get('/favicon.ico')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/static/favicon.ico')


def test_stats_renders_the_page_and_queries_all_time_and_current_year(client, repo):
    response = client.get('/stats')
    assert response.status_code == 200
    years = [call.args[0] for call in repo.fetch_statistics.call_args_list]
    assert years == [None, date.today().year]


def test_stats_passes_localized_chart_data_to_the_template(client, repo):
    with mock.patch.object(webserver, 'render_template', return_value='') as render:
        client.get('/stats', headers={'Accept-Language': 'de'})
    template, = render.call_args.args
    assert template == 'stats.html'
    assert json.loads(render.call_args.kwargs['data_all']) == [[2023, 2, 'Feb.', 4], [2023, 3, 'März', 1]]
    assert render.call_args.kwargs['data_weekdays'] == [['Montag', 2], ['Mittwoch', 1]]


def test_format_stats_results_adds_the_month_name():
    entries = [StatsEntry(2023, 2, 4)]
    assert list(webserver.format_stats_results(entries, 'en')) == [(2023, 2, 'Feb', 4)]


def test_weekday_stats_counts_picks_per_weekday_in_week_order(client, repo):
    with webserver.app.test_request_context(headers={'Accept-Language': 'en'}):
        assert list(webserver.weekday_stats(repo)) == [['Monday', 2], ['Wednesday', 1]]


@pytest.mark.parametrize('locale, index, expected', [
    ('en', 0, 'Monday'),
    ('de', 6, 'Sonntag'),
])
def test_weekday_format(locale, index, expected):
    assert webserver.weekday_format(index, locale) == expected


@pytest.mark.parametrize('locale, index, expected', [
    ('en', 1, 'Jan'),
    ('de', 3, 'März'),
])
def test_month_format(locale, index, expected):
    assert webserver.month_format(index, locale) == expected
