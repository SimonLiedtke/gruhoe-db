from datetime import date

from gruhoedb.models import Pick, StatsEntry


def test_pick_from_list():
    assert Pick.from_list([2024, 3, 17, 'Artist', 'Album']) == Pick(2024, 3, 17, 'Artist', 'Album')


def test_pick_date():
    assert Pick(2024, 3, 7, 'Artist', 'Album').date == date(2024, 3, 7)


def test_pick_weekday_starts_on_monday():
    assert Pick(2024, 3, 18, 'Artist', 'Album').weekday == 0  # Monday
    assert Pick(2024, 3, 17, 'Artist', 'Album').weekday == 6  # Sunday


def test_stats_entry_from_list():
    assert StatsEntry.from_list([2024, 3, 12]) == StatsEntry(2024, 3, 12)
