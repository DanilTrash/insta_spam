from typing import Union, Optional, Callable
from abc import ABC, abstractmethod, abstractproperty
import argparse
import logging
import sys
from configparser import ConfigParser
from time import sleep

import configparser
from onlinesimru import GetUser, GetNumbers
from loguru import logger


class Service(ABC):

    api_key = None

    @abstractmethod
    def __init__(self, api_key: ConfigParser):
        self.api_key = api_key

    @abstractmethod
    def get_number(self, **kwargs) -> Optional[str]:
        pass

    @abstractmethod
    def get_code(self, **kwargs) -> Optional[str]:
        pass

    @property
    @abstractmethod
    def balance(self) -> Optional[int]:
        pass


class OnlineSimService(Service):
    name = 'OnlineSimApi'
    tzid = None

    def __init__(self, api_key: str):
        self.sim = GetNumbers(api_key)
        self.user = GetUser(api_key)

    @property
    def balance(self) -> Union[int, None]:
        try:
            value = self.user.balance()["balance"]
            return value
        except Exception as error:
            logging.error(error)
            return None

    def get_code(self, tzid: int = None) -> Optional[str]:
        code = None
        if tzid:
            self.tzid = tzid
        if self.tzid is not None:
            code = self.sim.stateOne(self.tzid, 1)
        return code

    def get_number(self, **kwargs) -> Optional[str]:
        phone_number = None
        try:
            self.tzid = self.sim.get(**kwargs)
            phone_number = self.sim.stateOne(self.tzid)['number']
        except Exception as error:
            logger.error(error)
        finally:
            return phone_number


class SmsManService(Service):
    pass


class SmsActivateService(Service):
    pass


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(r'C:\Users\KIEV-COP-4\Desktop\insta_spam\refactoring\settings.ini')
    service = OnlineSimService(config['services']['online_sim'])
    phone = service.get_number(service='instagram')
    print(phone)
    code = service.get_code()
    print(code)
