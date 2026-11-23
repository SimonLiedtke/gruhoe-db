import csv
from datetime import date
from io import StringIO
from unittest import mock

import pytest

from gruhoedb import webserver
from gruhoedb.models import Pick

PICKS = [Pick(2023, 2, 10, 'Artist', 'Album')]


@pytest.fixture
def repo():
    with mock.patch.object(webserver, 'PickRepository') as repository_class:
        repo = repository_class.return_value
        repo.search.return_value = PICKS
        yield repo


@pytest.fixture
def client():
    return webserver.app.test_client()


def test_search_requires_output_format(client, repo):
    dates = 'from=2023-01-01&to=2023-12-31'
    assert client.get(f'/search?{dates}').status_code == 400
    assert client.get(f'/search?{dates}&outputformat=xml').status_code == 400


def test_search_passes_query_and_dates_to_repository(client, repo):
    client.get('/search?query=abc&from=2023-01-20&to=2023-03-05&outputformat=json')
    repo.search.assert_called_once_with('abc', date(2023, 1, 20), date(2023, 3, 5))


def test_search_json(client, repo):
    response = client.get('/search?outputformat=json&from=2023-01-01&to=2023-12-31')
    assert response.get_json() == [[2023, 2, 10, 'Artist', 'Album']]


def test_search_csv(client, repo):
    response = client.get('/search?outputformat=csv&from=2023-01-01&to=2023-12-31')
    assert response.mimetype == 'text/plain'
    assert list(csv.reader(StringIO(response.get_data(as_text=True)))) == [['2023', '2', '10', 'Artist', 'Album']]


def test_search_html(client, repo):
    response = client.get('/search?outputformat=html&from=2023-01-01&to=2023-12-31')
    assert response.status_code == 200
    assert response.headers['Content-Security-Policy'] == "default-src 'self'"
    assert 'Artist' in response.get_data(as_text=True)


@pytest.mark.parametrize('value, expected', [
    ('2024-01-02', date(2024, 1, 2)),
    ('', None),
    ('not-a-date', None),
])
def test_get_date_from_input(value, expected):
    assert webserver.get_date_from_input(value) == expected


def test_csvify_quotes_fields_containing_commas():
    picks = [Pick(2023, 2, 10, 'Earth, Wind & Fire', 'Album')]
    assert webserver.csvify(picks) == '2023,2,10,"Earth, Wind & Fire",Album\r\n'
