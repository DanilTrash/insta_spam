import json

from instagrapi import Client
from loguru import logger

from refactoring.data_classes import Account, Device


class Bot:
    def __init__(self, index):
        self.account = Account(index)
        self.device = Device(index)
        self.client = Client()

    def set_settings(self):  # todo test
        '''
        existing settings
        self.client.load_settings()

        new settings
        self.client.set_settings()
        '''
        self.client.set_proxy(f'http://{self.device.proxy}')
        if self.account.device_settings:
            self.client.load_settings(json.loads(self.account.device_settings))
        else:
            self.client.set_settings(self.device.get_available_device())

    def dump_settings(self):  # todo method for update database account.device_settings to self.client.settings
        '''
        saving self.client.settings
        '''

        self.account.update('device_settings', self.client.settings)

    def __enter__(self):
        self.set_settings()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dump_settings()

    def login(self):  # todo test
        '''
        username password
        '''
        try:
            self.client.login(self.account.username, self.account.password)
            return True
        except Exception as error:
            logger.error(error)
            return str(error)
