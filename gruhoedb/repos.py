from datetime import date

import psycopg

from gruhoedb.models import Pick, StatsEntry


class PickRepository:
    def __init__(self, db_connection_string) -> None:
        self.db_connection_string = db_connection_string

    def get_all(self) -> list[Pick]:
        with psycopg.connect(self.db_connection_string) as connection:
            with connection.cursor() as cursor:
                cursor.execute('SELECT year, month, day, artist, album FROM gruhoedb.dbo.picks')
                results = cursor.fetchall()
        return map(Pick.from_list, results)

    def search(self, query: str, from_: date, to: date) -> list[Pick]:
        sql = '''
            SELECT year, month, day, artist, album
            FROM gruhoedb.dbo.picks
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
        sql = '''
            SELECT year, month, count(*)
            FROM gruhoedb.dbo.picks
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
