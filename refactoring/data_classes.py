import configparser
import sqlite3
from typing import Union

config = configparser.ConfigParser()
config.read(r'settings.ini')
test_db_ = config['db_location']['test_db']


class SqliteData:
    db_path: str = test_db_
    con = sqlite3.connect(db_path)


class AbstractRow(SqliteData):
    table = None
    primary_key = None

    def __init__(self, index):
        self.index = index

    def __getattr__(self, item) -> Union[str, int, None]:
        try:
            value = self.con.execute(
                f'select {item} from {self.table} where {self.primary_key} = {self.index}'
            ).fetchone()[0]
            return value
        except sqlite3.OperationalError:
            return None

    def update(self, key, value) -> None:
        self.con.execute(
            f'update {self.table} set {key} = ? where {self.primary_key} = {self.index}',
            (value,))
        self.con.commit()


class Account(AbstractRow):
    table = 'accounts'
    primary_key = 'id'


class Device(AbstractRow):
    table = 'devices'
    primary_key = 'id'


class Proxy(AbstractRow):
    table = 'proxys'
    primary_key = 'id'


class Browser(AbstractRow):
    table = 'browsers'
    primary_key = 'id'
