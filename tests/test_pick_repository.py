"""Integration tests for PickRepository against a real PostgreSQL database.

Set TEST_DB_CONNECTION to a connection string for an empty database named ``gruhoedb`` (the name is
hard-coded in create-schema.sql). The tests create ``dbo.picks`` and drop it afterwards, and refuse to
run if that table already exists so they can never wipe real data.
"""
import os
from datetime import date
from pathlib import Path

import psycopg
import pytest

from gruhoedb.models import Pick, StatsEntry
from gruhoedb.repos import PickRepository

DB_CONNECTION = os.getenv('TEST_DB_CONNECTION')
DB_NAME = 'gruhoedb'
SCHEMA_SQL = (Path(__file__).parent.parent / 'create-schema.sql').read_text()

pytestmark = pytest.mark.skipif(not DB_CONNECTION, reason='TEST_DB_CONNECTION is not set')


@pytest.fixture
def repo():
    with psycopg.connect(DB_CONNECTION, autocommit=True) as connection:
        if connection.execute("SELECT to_regclass('dbo.picks')").fetchone()[0] is not None:
            pytest.fail('Refusing to run: dbo.picks already exists. Point TEST_DB_CONNECTION at an empty database.')
        connection.execute('CREATE SCHEMA IF NOT EXISTS dbo')
        connection.execute(SCHEMA_SQL)
    try:
        yield PickRepository(DB_CONNECTION, DB_NAME)
    finally:
        with psycopg.connect(DB_CONNECTION, autocommit=True) as connection:
            connection.execute('DROP TABLE IF EXISTS dbo.picks')


def albums(picks):
    return sorted(pick.album for pick in picks)


def test_add_many_and_get_all_round_trip(repo):
    picks = [Pick(2023, 1, 1, 'A', 'one'), Pick(2023, 1, 2, 'B', 'two'), Pick(2023, 1, 3, 'C', 'three')]
    repo.add_many(picks)
    assert sorted(repo.get_all()) == picks


def test_add_many_accepts_a_single_pick_and_an_empty_list(repo):
    repo.add_many([])
    repo.add_many([Pick(2023, 1, 1, 'A', 'one')])
    assert list(repo.get_all()) == [Pick(2023, 1, 1, 'A', 'one')]


def test_contains(repo):
    pick = Pick(2023, 1, 1, 'A', 'one')
    assert pick not in repo
    repo.add_many([pick])
    assert pick in repo
    assert Pick(2023, 1, 2, 'A', 'one') not in repo


def test_contains_rejects_non_picks(repo):
    with pytest.raises(TypeError):
        ('A', 'one') in repo


class TestSearch:
    @pytest.fixture(autouse=True)
    def picks(self, repo):
        repo.add_many([
            Pick(2022, 12, 20, 'Alpha', 'prev-year'),
            Pick(2023, 1, 19, 'Beta', 'day-before'),
            Pick(2023, 1, 20, 'Gamma', 'first-day'),
            Pick(2023, 2, 10, 'Delta', 'middle'),
            Pick(2023, 3, 5, 'Epsilon', 'last-day'),
            Pick(2023, 3, 6, 'Zeta', 'day-after'),
        ])

    def test_range_spanning_months_with_later_start_day_than_end_day(self, repo):
        # Regression: year, month and day used to be compared independently ("day BETWEEN 20 AND 5").
        results = repo.search('', date(2023, 1, 20), date(2023, 3, 5))
        assert albums(results) == ['first-day', 'last-day', 'middle']

    def test_range_spanning_years(self, repo):
        results = repo.search('', date(2022, 12, 20), date(2023, 1, 19))
        assert albums(results) == ['day-before', 'prev-year']

    def test_both_boundaries_are_inclusive(self, repo):
        assert albums(repo.search('', date(2023, 2, 10), date(2023, 2, 10))) == ['middle']

    def test_unbounded_range_returns_everything(self, repo):
        assert len(list(repo.search('', date(1, 1, 1), date(9999, 12, 31)))) == 6

    def test_empty_range_returns_nothing(self, repo):
        assert list(repo.search('', date(2024, 1, 1), date(2024, 12, 31))) == []

    @pytest.mark.parametrize('query, expected', [
        ('gamma', ['first-day']),      # artist, case-insensitive
        ('MIDDLE', ['middle']),        # album, case-insensitive
        ('day', ['day-before', 'day-after', 'first-day', 'last-day']),
        ('nothing matches this', []),
    ])
    def test_text_query_matches_artist_or_album(self, repo, query, expected):
        results = repo.search(query, date(1, 1, 1), date(9999, 12, 31))
        assert albums(results) == sorted(expected)

    def test_text_query_is_combined_with_the_date_range(self, repo):
        results = repo.search('day', date(2023, 1, 20), date(2023, 3, 5))
        assert albums(results) == ['first-day', 'last-day']

    def test_stored_dates_that_do_not_exist_do_not_break_the_search(self, repo):
        repo.add_many([Pick(2023, 4, 31, 'Eta', 'invalid-date')])
        results = repo.search('', date(2023, 1, 20), date(2023, 3, 5))
        assert albums(results) == ['first-day', 'last-day', 'middle']


def test_fetch_statistics(repo):
    repo.add_many([
        Pick(2022, 12, 1, 'A', 'a'),
        Pick(2023, 2, 1, 'B', 'b'),
        Pick(2023, 2, 2, 'C', 'c'),
        Pick(2023, 1, 1, 'D', 'd'),
    ])
    assert list(repo.fetch_statistics()) == [StatsEntry(2022, 12, 1), StatsEntry(2023, 1, 1), StatsEntry(2023, 2, 2)]
    assert list(repo.fetch_statistics(2023)) == [StatsEntry(2023, 1, 1), StatsEntry(2023, 2, 2)]
