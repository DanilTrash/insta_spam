import configparser
import string
from random import choice
from time import sleep

import requests

from refactoring.browser import Browser
from refactoring.data_classes import Account

config = configparser.ConfigParser()
config.read('config.ini')


class MainClass:
    service = None

    @staticmethod
    def random_string(length):
        value = ''.join(choice([c for c in string.digits + string.ascii_letters]) for _ in range(length))
        return value

    def __init__(self, index):
        device = Device(index)
        self.profile_id = device['profile_id']
        self.change_ip_link = device['change_ip']
        self.browser = Instareg(profile_id=self.profile_id)

    def choose_method(self, option):
        services = {
            'online_sim': OnlineSimApi(config['OnlineSim']['api_key'])
        }
        self.service = services[option]

    def change_ip(self):
        print(requests.get('http://' + self.change_ip_link).content)

    def __call__(self):
        tzid = self.service.get_number('instagram', 380)
        phone = self.service.state(tzid)
        username = 'massage_moscow_%s' % self.random_string(6)
        password = self.random_string(10)
        print(phone)
        print(f'{username}\t{password}')
        self.browser.first_page(phone['number'], username, password)
        self.browser.second_page()
        message = None
        count = 0
        while message is None and count < 60:
            count += 1
            code = self.service.get_sms(tzid)
            print(code)
            try:
                message = code['msg'][-1]['msg']
            except KeyError:
                continue
            finally:
                sleep(1)
        if message is None:
            return False
        confirmation = self.browser.phone_confirmation(message)
        if confirmation:
            return username, password
        else:
            return False


if __name__ == '__main__':
    pass
