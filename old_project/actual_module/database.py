from dataclasses import dataclass
import sqlite3
import pandas as pd


class GoogleSheetsData:
    url = ('https://docs.google.com/spreadsheets/u/0/d/1zaxjdu9ESYy2MCNuDow0_5PnZpwEsyrdTQ_kk0PMZbw/export'
           '?format=csv&id=1zaxjdu9ESYy2MCNuDow0_5PnZpwEsyrdTQ_kk0PMZbw&gid=1623842316')

    def __init__(self):
        self.dataframe = pd.read_csv(self.url)

    def __call__(self, item):
        value = self.dataframe[item]
        return value


if __name__ == '__main__':
    old_data = sqlite3.connect(r'/database.sqlite')
    new_data = sqlite3.connect(r'C:\Users\KIEV-COP-4\Desktop\insta_spam\test_data.db')
