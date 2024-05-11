from datetime import date

import psycopg

from gruhoedb.models import Pick


class PickRepository:
    def __init__(self, db_connection_string) -> None:
        self.db_connection_string = db_connection_string

    def get_all(self) -> list[Pick]:
        with psycopg.connect(self.db_connection_string) as connection:
            with connection.cursor() as cursor:
                cursor.execute('SELECT year, month, day, artist, album FROM gruhoedb.dbo.picks')
                results = cursor.fetchall()
        return map(Pick.from_list, results)

    def count(self) -> int:
        return len(list(self.get_all()))

    def search(self, query: str, from_: date, to: date) -> list[Pick]:
        query = f'%{query}%'
        data = (
            query, query,
            from_.year, to.year,
            from_.month, to.month,
            from_.day, to.day
        )
        sql = '''
            SELECT year, month, day, artist, album
            FROM gruhoedb.dbo.picks
            WHERE
                (artist ILIKE %s OR album ILIKE %s)
                AND year BETWEEN %s AND %s
                AND month BETWEEN %s AND %s
                AND day between %s AND %s
        '''
        with psycopg.connect(self.db_connection_string) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, data)
                results = cursor.fetchall()
        return map(Pick.from_list, results)
