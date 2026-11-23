from unittest import mock

import pytest

from gruhoedb.models import Pick
from gruhoedb.repos import GoogleDocsRepo


def paragraph(text, style='NORMAL_TEXT'):
    return {
        'paragraph': {
            'paragraphStyle': {'namedStyleType': style},
            'elements': [{'textRun': {'content': f'{text}\n'}}],
        }
    }


def parse(*paragraphs, locale='en'):
    """Run the parser over a fake document and return only the picks it yields."""
    # The first content element of a real document is a section break, which the parser skips.
    document = {'body': {'content': [{'sectionBreak': {}}, *paragraphs]}}
    with mock.patch('gruhoedb.repos.build') as build:
        build.return_value.documents.return_value.get.return_value.execute.return_value = document
        repo = GoogleDocsRepo(mock.Mock(), 'doc-id', locale)
    return [pick for pick in repo if pick is not None]


def test_parses_picks_with_year_month_and_day():
    picks = parse(
        paragraph('Gruhö 2024', 'TITLE'),
        paragraph('March', 'HEADING_1'),
        paragraph('17.', 'HEADING_2'),
        paragraph('Artist - Album'),
        paragraph('Other Artist - Other Album'),
        paragraph('18.', 'HEADING_2'),
        paragraph('Third Artist - Third Album'),
    )
    assert picks == [
        Pick(2024, 3, 17, 'Artist', 'Album'),
        Pick(2024, 3, 17, 'Other Artist', 'Other Album'),
        Pick(2024, 3, 18, 'Third Artist', 'Third Album'),
    ]


def test_month_names_follow_the_locale():
    picks = parse(
        paragraph('Gruhö 2024', 'TITLE'),
        paragraph('März', 'HEADING_1'),
        paragraph('1.', 'HEADING_2'),
        paragraph('Artist - Album'),
        locale='de',
    )
    assert picks == [Pick(2024, 3, 1, 'Artist', 'Album')]


def test_splits_only_at_the_first_separator():
    picks = parse(
        paragraph('Gruhö 2024', 'TITLE'),
        paragraph('January', 'HEADING_1'),
        paragraph('5.', 'HEADING_2'),
        paragraph('Artist - Album - Deluxe Edition'),
    )
    assert picks == [Pick(2024, 1, 5, 'Artist', 'Album - Deluxe Edition')]


def test_line_without_separator_is_used_as_artist_and_album():
    picks = parse(
        paragraph('Gruhö 2024', 'TITLE'),
        paragraph('January', 'HEADING_1'),
        paragraph('5.', 'HEADING_2'),
        paragraph('Self-Titled'),
    )
    assert picks == [Pick(2024, 1, 5, 'Self-Titled', 'Self-Titled')]


def test_text_before_the_date_is_known_is_ignored():
    assert parse(paragraph('Artist - Album')) == []
    assert parse(paragraph('Gruhö 2024', 'TITLE'), paragraph('Artist - Album')) == []


def test_empty_paragraphs_are_ignored():
    picks = parse(
        paragraph('Gruhö 2024', 'TITLE'),
        paragraph('January', 'HEADING_1'),
        paragraph('5.', 'HEADING_2'),
        paragraph(''),
        paragraph('Artist - Album'),
    )
    assert picks == [Pick(2024, 1, 5, 'Artist', 'Album')]


def test_unknown_month_name_raises():
    with pytest.raises(ValueError):
        parse(paragraph('Gruhö 2024', 'TITLE'), paragraph('Smarch', 'HEADING_1'))
