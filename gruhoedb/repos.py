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
        return len(self.get_all())
