from collections import namedtuple
from datetime import date


class Pick(namedtuple('Pick', ['year', 'month', 'day', 'artist', 'album'])):
    @property
    def date(self):
        return date.fromisoformat(f'{int(self.year):04}-{int(self.month):02}-{int(self.day):02}')