import psycopg
from gruhoedb.models import Pick


def get_picks(db_connection_string):
    with psycopg.connect(db_connection_string) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT year, month, day, artist, album FROM gruhoedb.dbo.picks')
            results = cursor.fetchall()
    return map(Pick.from_list, results)
