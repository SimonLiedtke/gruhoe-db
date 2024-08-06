from collections.abc import Iterator
from datetime import date
from itertools import repeat
import os
import re

from babel.dates import get_month_names
from googleapiclient.discovery import build
import psycopg

from gruhoedb.models import Pick, StatsEntry
from gruhoedb.credentials import GoogleDocsCredentials


class PickRepository:
    def __init__(self, db_connection_string, db_name) -> None:
        self.db_connection_string = db_connection_string
        self.db_name = db_name

    def __contains__(self, pick: Pick) -> bool:
        if not (isinstance(pick, Pick)):
            raise TypeError
        sql = f'''
        SELECT EXISTS (
            SELECT 1
            FROM {self.db_name}.dbo.picks
            WHERE
                year = %s
                AND month = %s
                AND day = %s
                AND artist = %s
                AND album = %s
        )
        '''
        data = (pick.year, pick.month, pick.day, pick.artist, pick.album)

        with psycopg.connect(self.db_connection_string) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, data)
                result = cursor.fetchone()
        return result[0]

    def add_many(self, picks: list[Pick]) -> None:
        if not picks:
            return

        sql = f'INSERT INTO {self.db_name}.dbo.picks (year, month, day, artist, album) VALUES\n'

        if len(picks) > 1:
            sql += '\n'.join(repeat('(%s, %s, %s, %s, %s),', len(picks[:-1])))
        sql += '(%s, %s, %s, %s, %s);'

        data = []
        for pick in picks:
            data.extend([pick.year, pick.month, pick.day, pick.artist, pick.album])

        with psycopg.connect(self.db_connection_string) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, tuple(data))
            connection.commit()

    def get_all(self) -> list[Pick]:
        with psycopg.connect(self.db_connection_string) as connection:
            with connection.cursor() as cursor:
                cursor.execute(f'SELECT year, month, day, artist, album FROM {self.db_name}.dbo.picks')
                results = cursor.fetchall()
        return map(Pick.from_list, results)

    def search(self, query: str, from_: date, to: date) -> list[Pick]:
        sql = f'''
            SELECT year, month, day, artist, album
            FROM {self.db_name}.dbo.picks
            WHERE
                year BETWEEN %s AND %s
                AND month BETWEEN %s AND %s
                AND day between %s AND %s
        '''
        data = [
            from_.year, to.year,
            from_.month, to.month,
            from_.day, to.day,
        ]

        if query:
            sql += ' AND (artist ILIKE %s OR album ILIKE %s)'
            query = f'%{query}%'
            data += [query, query]

        with psycopg.connect(self.db_connection_string) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, tuple(data))
                results = cursor.fetchall()
        return map(Pick.from_list, results)

    def fetch_statistics(self, year: int = None) -> list[StatsEntry]:
        sql = f'''
            SELECT year, month, count(*)
            FROM {self.db_name}.dbo.picks
            GROUP BY year, month
        '''

        if year is None:
            data = ()
        else:
            data = (year,)
            sql += ' HAVING year = %s'

        sql += ' ORDER BY year, month'

        with psycopg.connect(self.db_connection_string) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, data)
                results = cursor.fetchall()
        return map(StatsEntry.from_list, results)


class GoogleDocsRepo:
    def __init__(self, credentials: GoogleDocsCredentials, document_id: str, locale: str) -> None:
        self.translated_months = list(get_month_names('wide', locale=locale).values())
        service = build('docs', 'v1', credentials=credentials.credentials)
        document = service.documents().get(documentId=document_id).execute()
        body = document['body']
        self.content = body['content']
        self.linepos = 0
        self.year = 0
        self.month = 0
        self.day = 0

    def __iter__(self) -> Iterator[Pick]:
        return self

    def __next__(self) -> Pick:
        self.linepos += 1
        try:
            line = self.content[self.linepos]
        except IndexError:
            raise StopIteration

        paragraph = line['paragraph']
        style_type = paragraph['paragraphStyle']['namedStyleType']
        content = paragraph['elements'][0]['textRun']['content'].strip()
        if not content:
            return None
        if style_type == 'TITLE':
            m = re.search(r'\d{4}', content)
            if m is not None:
                self.year = int(m.group())
            return None
        elif style_type == 'HEADING_1':
            month_name = content
            self.month = self.translated_months.index(month_name) + 1
            return None
        elif style_type == 'HEADING_2':
            m = re.search(r'(\d{1,2})\.', content)
            if m is not None:
                self.day = int(m.group(1))
        elif style_type == 'NORMAL_TEXT':
            try:
                artist, album = content.split(' - ', maxsplit=1)
            except ValueError:
                # print(f'Error: year {self.year}: line {self.linepos}: "{content}": could not parse to artist and album')
                artist = album = content
            if self.year > 0 and self.month > 0 and self.day > 0 and artist and album:
                return Pick(self.year, self.month, self.day, artist, album)

        return None
