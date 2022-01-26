import os

from old_project.actual_module.insta_bot import Bot
import json


def grab_data():
    for index in range(14, 66):
        try:
            with Bot(index) as bot:
                bot.login()
                account_insights = bot.client.insights_account()
                print(account_insights)
                with open(f'accounts_info/{bot.username}.json', 'w+') as f:
                    json.dump(account_insights, f)
        except Exception as error:
            print(error)


def extract_data():
    for i in os.listdir('accounts_info/'):
        if i.endswith('json'):
            with open('accounts_info/' + i) as f:
                data = json.load(f)
                print(f'{i}\t' + str(data['account_insights_unit']['website_visits_metric_count']))


if __name__ == '__main__':
    grab_data()
    extract_data()
