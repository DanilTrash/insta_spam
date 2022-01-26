
def posting():  # todo алгортим __main__
    while True:
        data = BaseData()
        accounts = data.cur.execute('''
        select id from accounts where status is not 'banned' and status not NULL
        ''').fetchall()
        for i in reversed(accounts):
            with Bot(i[0]) as bot:
                if not bot.login():
                    continue
                if bot.status == 'new':
                    try:
                        bot.setup_profile()
                        bot.accounts_data.update('status', 'posting')
                    except Exception as error:
                        logging.exception(error)
                        continue
                if bot.status == 'posting':
                    try:
                        media = bot.upload_photo()
                        print(media)
                        sleep(30)
                    except ProxyError as error:
                        logging.error(error)
                        bot.accounts_data.update('status', 'Exception at posting')
                    except Exception as error:
                        logging.exception(error)


if __name__ == '__main__':
    posting()
