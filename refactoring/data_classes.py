import configparser
from typing import Union
import sqlite3

config = configparser.ConfigParser()
config.read(r'C:\Users\KIEV-COP-4\Desktop\insta_spam\refactoring\config.ini')
test_db_ = config['db_location']['test_db']


class SqliteData:
    db_path: str = test_db_
    con = sqlite3.connect(db_path)


class AbstractData(SqliteData):
    table = None
    primary_key = None

    def __init__(self, index):
        self.index = index

    def __getattr__(self, item):
        try:
            value = self.con.execute(f'select {item} from {self.table} where {self.primary_key} = ?', (self.index,)).fetchone()
            return value
        except sqlite3.OperationalError:
            return None


class Account(SqliteData):
    table = 'accounts'
    primary_key = 'account_id'

    def __init__(self, index):
        self.index = index

    def __getattr__(self, item):
        try:
            value = self.con.execute(f'select {item} from {self.table} where {self.primary_key} = ?', (self.index,)).fetchone()
            return value
        except sqlite3.OperationalError:
            return None

    def update(self, key, value):
        self.con.execute(
            f'update {self.table} set {key} = ? where {self.primary_key} = ?', (value, self.index)
        )
        self.con.commit()


class Device(AbstractData):
    table = 'devices'
    primary_key = 'device_id'
    foreign_key = 'account_id'

    def __getattr__(self, item):
        try:
            value = self.con.execute(f'select {item} from {self.table} where {self.foreign_key} = ?', (self.index,)).fetchone()
            return value
        except sqlite3.OperationalError:
            return None


device = Device(1)
print(device.proxy)
