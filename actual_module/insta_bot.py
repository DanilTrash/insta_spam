import configparser
import json
import logging
import os
import random

from requests.exceptions import ProxyError

from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, ChallengeUnknownStep, ClientConnectionError


class RandomPhoto:  # todo photo fx script
    config = configparser.ConfigParser()
    config.read('config.ini')
    images_folder = config['options']['images_path']

    @property
    def random_photo(self) -> str:
        photo = random.choice(os.listdir(self.images_folder))
        return rf'{self.images_folder}\{photo}'


class Bot:
    def __init__(self, index):
        print('getting data')
        self.index = index
        self.accounts_data = AccountData(index)
        self.post_data = PostData('posting_data_oae')
        self.profile_id = self.accounts_data['profile_id']
        self.proxy = self.accounts_data['proxy']
        self.device = json.loads(self.accounts_data['device'])
        self.username = self.accounts_data['username']
        self.password = self.accounts_data['password']
        self.status = self.accounts_data['status']
        self.ip_change_url = self.accounts_data['change_ip']
        self.client = Client()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.client.dump_settings(f'{os.getcwd()}/user_data/{self.username}.json')
        del self

    def __enter__(self):
        print(f'entering to {self.username}')
        self.client.set_proxy(f'http://{self.proxy}')
        if os.path.exists(f'{os.getcwd()}/user_data/{self.username}'):
            self.client.load_settings(f'{os.getcwd()}/user_data/{self.username}.json')
        else:
            self.client.set_settings(self.device)
        return self

    def login(self) -> bool:
        print(f'logging {self.username}')
        try:
            result = self.client.login(self.username, self.password, True)
            return result
        except (ProxyError, ClientConnectionError) as error:
            logging.error(error)
            self.accounts_data.update('status', 'ProxyError or ClientConnectionError')
            return False
        except ChallengeRequired as error:
            logging.error(error)
            self.accounts_data.update('status', 'ChallengeRequired')
            return False
        except ChallengeUnknownStep as error:
            logging.error(error)
            self.accounts_data.update('status', 'ChallengeUnknownStep')
            return False
        except Exception as error:
            logging.exception(error)
            self.accounts_data.update('status', 'Login Exception')
            return False

    def _upload_photo(self):  # fix
        self.captions = self.post_data['caption']
        self.hashtags = self.post_data['hashtags']
        self.location = random.choice(self.post_data['location'])[0]
        self.caption = random.choice(self.captions)[0]
        random.shuffle(self.hashtags)
        iterable_tags = iter(self.hashtags)
        for _ in range(random.choice(range(15, 25))):
            try:
                self.caption += f' {next(iterable_tags)[0]}'
            except StopIteration:
                break
        location = self.client.fbsearch_places(self.location)[0]
        try:
            range_ = [self.random_photo for _ in range(2, random.choice(range(3, 7)))]
            photo_upload = self.client.album_upload(
                range_,
                self.caption,
                location=location
            )
        except Exception as error:
            logging.error(error)
            photo_upload = self.client.photo_upload(
                self.random_photo,
                self.caption,
                location=location
            )
        return photo_upload

    def _setup_profile(self):
        print('setting up {}'.format(self.username))
        self.biography = random.choice(self.post_data['biography'][0])
        self.external_url = self.accounts_data['external_url']
        self.client.account_change_picture(self.random_photo)
        self.client.account_edit(biography=self.biography, external_url=self.external_url)
        account_info = self.client.account_info()
        print('account changed to {}'.format(account_info))
