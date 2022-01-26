import json

from instagrapi import Client
from instagrapi.exceptions import ChallengeUnknownStep
from loguru import logger

from data_classes import Account, Device, Proxy


class Bot:
    def __init__(self, index):
        self.account_data = Account(index)
        logger.info(self.account_data.username)
        self.device_data = Device(self.account_data.device_id)
        self.proxy_data = Proxy(self.device_data.proxy_id)
        self.client = Client()

    def load_settings(self):
        proxy_link = f'http://{self.proxy_data.proxy}'
        device_settings = json.loads(self.device_data.settings)
        self.client.set_proxy(proxy_link)
        self.client.set_settings(device_settings)

    def dump_settings(self):
        dumps = json.dumps(self.client.settings)
        self.device_data.update('settings', dumps)

    def __enter__(self):
        self.load_settings()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dump_settings()

    def login(self):
        try:
            self.client.login(self.account_data.username, self.account_data.password)
            logger.info('Authorized')
            self.account_data.update('status', 'Authorized')
        except Exception as error:
            logger.error(error)
            self.account_data.update('status', str(error))
