import configparser
import logging
import string
from random import choice
from time import sleep

import requests

from actual_module.browser import Browser
from actual_module.database import BaseData, AccountData
from actual_module.services import OnlineSimApi


class Instareg(Browser):

    def __init__(self, **kwargs):
        super(Browser, self).__init__(**kwargs)

    def first_page(self, phone, username, password):
        self.driver.get('https://www.instagram.com/accounts/emailsignup/')
        self.wait_for_element('//*/input[@name="username"]').send_keys(username)
        self.wait_for_element('//*/input[@name="password"]').send_keys(password)
        self.wait_for_element('//*/input[@name="emailOrPhone"]').send_keys(phone)
        self.wait_for_element('//*/div[7]/div/button').click()

    def second_page(self):
        self.wait_for_element(f'//*/span/span[1]/select/option[{choice(range(1, 13))}]').click()
        self.wait_for_element(f'//*/span/span[2]/select/option[{choice(range(1, 20))}]').click()
        self.wait_for_element(f'//*/span/span[3]/select/option[{choice(range(20, 30))}]').click()
        self.wait_for_element('//*/div[6]/button').click()

    def phone_confirmation(self, code) -> bool:
        self.wait_for_element('//*/input[@name="confirmationCode"]').send_keys(code)
        self.wait_for_element('//form/div[2]/button').click()
        if self.wait_for_element_disappears('//*/input[@name="confirmationCode"]', 15):
            try:
                assert 'Чтобы войти, подтвердите, что это вы' not in self.driver.page_source
                return True
            except AssertionError:
                return False
        else:
            return False

    def teardown(self):
        self.driver.quit()


class MainClass:

    def random_string(self, length):
        value = ''.join(choice([c for c in string.digits + string.ascii_letters]) for _ in range(length))
        return value

    def __init__(self, index):
        data = AccountData(index)
        parser = configparser.ConfigParser()
        parser.read('config.ini')
        self.profile_id = data['profile_id']
        self.change_ip_link = data['change_ip']
        self.service = OnlineSimApi(parser['OnlineSim']['api_key'])
        self.browser = Instareg(profile_id=self.profile_id)
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
    data = BaseData()
    while True:
        empty_proxy = data.cur.execute('''
        select id from accounts where proxy and change_ip is not NULL and status is NULL
        ''').fetchall()
        for i in empty_proxy:
            try:
                reg = MainClass(i[0])
                result = reg()
                print(result)
                if result is False:
                    reg.browser.teardown()
                else:
                    data.cur.execute('''update accounts set username = ?, password = ?, status = 'new' where id = ?''',
                                     (result[0], result[1], i[0]))
                    data.connection.commit()
            except Exception as error:
                logging.exception(error)
