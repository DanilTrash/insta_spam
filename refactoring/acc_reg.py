import configparser
import string
from random import choice

from loguru import logger

from refactoring.browser import Instareg
from refactoring.data_classes import SqliteData, Browser, Device
from services import OnlineSimService


class GeneratedAccount:
    pass_len: int = 8
    acc_prefix: str = ''
    acc_suffix_len = 5
    username = None
    password = None

    def __init__(self):
        self.username = self.acc_prefix + self.random_string(5)
        self.password = self.random_string(self.pass_len)

    @staticmethod
    def random_string(lenght):
        value = ''.join(choice([c for c in string.digits + string.ascii_letters]) for _ in range(lenght))
        return value

    def __repr__(self):
        return f'{self.username, self.password}'


class RegistrationBot:
    service = None
    browser_data = None
    account_data = None

    def __call__(self, **kwargs) -> bool:
        result = False
        phone = self.service.get_number(**kwargs)
        if phone is None:
            return False
        logger.info(phone)
        multilogin_id = self.browser_data.multilogin_id
        with Instareg(multilogin_id) as browser:
            browser.first_page(phone, self.account_data.username, self.account_data.password)
            browser.second_page()
            code = self.service.get_code()
            if code:
                result = browser.phone_confirmation(code)
        return result


def main():
    config = configparser.ConfigParser()
    config.read(r'C:\Users\KIEV-COP-4\Desktop\insta_spam\refactoring\settings.ini')

    account_data = GeneratedAccount
    account_data.password_length = 8
    account_data.acc_prefix = 'paris_for_girls_'

    data = SqliteData().con
    devices_id = data.execute(
        'select device_id from accounts where username is NULL'
    ).fetchall()

    for device_id in devices_id:
        reg_bot = RegistrationBot()
        reg_bot.service = OnlineSimService(config['services']['online_sim'])
        reg_bot.browser_data = Browser(Device(*device_id).multilogin_id)
        reg_bot.account_data = account_data()
        registered_account = (reg_bot.account_data.username, reg_bot.account_data.password, *device_id)
        print(registered_account)
        result = reg_bot(service='instagram')
        if result is True:
            data.execute('update accounts '
                         'set username = ?, password = ? where device_id = ?',
                         registered_account)
            data.commit()


if __name__ == '__main__':
    main()
