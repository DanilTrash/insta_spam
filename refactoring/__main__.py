from data_classes import SqliteData
from bot import Bot


def main():
    data = SqliteData().con
    accounts_id = data.execute(
        'select id from accounts where device_id is not NULL and username is not NULL and status is NULL'
    ).fetchall()
    for account_id in accounts_id:
        with Bot(*account_id) as bot:
            login = bot.login()
            if login is not True:
                continue


if __name__ == '__main__':
    main()
