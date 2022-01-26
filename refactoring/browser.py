from random import randint, uniform, choice
from time import time, sleep

import requests
from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


DEFAULT_IMPLICIT_WAIT = 30


class MultiLoginDriver:

    def __init__(self, profile_id):
        mla_url = 'http://127.0.0.1:35000/api/v1/profile/start?automation=true&profileId=' + profile_id
        self.driver = None
        while self.driver is None:
            resp = requests.get(mla_url)
            json = resp.json()
            print(json)
            if json.get('value'):
                self.driver = webdriver.Remote(command_executor=json['value'], desired_capabilities={})


class Browser(MultiLoginDriver):
    username = None
    password = None

    selectors = {
        "accept_cookies": "//button[text()='Accept']",
        "home_to_login_button": "//button[text()='Log In']",
        "username_field": "username",
        "password_field": "password",
        "button_login": '//*[@id="loginForm"]/div/div[3]/button',
        "login_check": "//*[@aria-label='Home'] | //button[text()='Save Info'] | //button[text()='Not Now']",
        "search_user": "queryBox",
        "select_user": "//div[@aria-labelledby]/div/span//img[@data-testid='user-avatar']",
        "name": "((//div[@aria-labelledby]/div/span//img[@data-testid='u"
                "ser-avatar'])[1]//..//..//..//div[2]/div[2]/div)[1]",
        "next_button": "//button/*[text()='Next']",
        "textarea": "//textarea[@placeholder]",
        "send": "//button[text()='Send']"
    }

    def __enter__(self):
        return self

    def _get_to_login_page(self):
        self.driver.get('https://instagram.com/?hl=en')
        self.__random_sleep__(3, 5)
        if self.__wait_for_element__(self.selectors['accept_cookies'], 'xpath', 10):
            self.__get_element__(
                self.selectors['accept_cookies'], 'xpath').click()
            self.__random_sleep__(3, 5)
        if self.__wait_for_element__(self.selectors['home_to_login_button'], 'xpath', 10):
            self.__get_element__(
                self.selectors['home_to_login_button'], 'xpath').click()
            self.__random_sleep__(5, 7)

    def wait_for_element(self, xpath, wait_time: int = 10):
        try:
            element = WebDriverWait(self.driver, wait_time).until(lambda d: self.driver.find_element(By.XPATH, xpath))
            return element
        except Exception as error:
            logger.error(error)
            return None

    def wait_for_element_disappears(self, xpath, wait_time: int = 10):
        try:
            element = WebDriverWait(self.driver, wait_time).until_not(
                lambda d: self.driver.find_element(By.XPATH, xpath)
            )
            return element
        except Exception as error:
            logger.error(error)
            return None

    def login(self, username, password) -> bool:
        self.username = username
        self.password = password
        self.driver.get('https://instagram.com/?hl=ru')
        # self._get_to_login_page()
        logger.info(f'Login with {self.username}')
        if not self.wait_for_element('//*/input[@name="username"]'):
            logger.error('Login Failed: username field not visible')
        else:
            self.driver.find_element(By.NAME, self.selectors['username_field']).send_keys(self.username)
            self.driver.find_element(By.NAME, self.selectors['password_field']).send_keys(self.password)
            self.wait_for_element(self.selectors['button_login']).click()
            if self.wait_for_element(self.selectors['login_check'], 10):
                print('Login Successful')
                return True
            else:
                print('Login Failed: Incorrect credentials')
                return False

    def type_message(self, message):
        if self.__wait_for_element__(self.selectors['next_button'], "xpath"):
            self.__get_element__(
                self.selectors['next_button'], "xpath").click()
            self.__random_sleep__()

        if self.__wait_for_element__(self.selectors['textarea'], "xpath"):
            self.__type_slow__(self.selectors['textarea'], "xpath", message)
            self.__random_sleep__()

        if self.__wait_for_element__(self.selectors['send'], "xpath"):
            self.__get_element__(self.selectors['send'], "xpath").click()
            self.__random_sleep__(3, 5)
            print('Message sent successfully')

    def send_message(self, user, message):
        logger.info(f'Send message to {user}')
        self.driver.get('https://www.instagram.com/direct/new/?hl=en')
        self.__random_sleep__(5, 7)
        try:
            self.__wait_for_element__(self.selectors['search_user'], "name")
            self.__type_slow__(self.selectors['search_user'], "name", user)
            self.__random_sleep__(7, 10)
            elements = self.driver.find_elements(
                By.XPATH, self.selectors['select_user'])
            if elements and len(elements) > 0:
                elements[0].click()
                self.__random_sleep__()
                self.type_message(message)
                self.__random_sleep__(50, 60)
                return True
            else:
                print(f'User {user} not found! Skipping.')
                return False
        except Exception as e:
            logger.error(e)
            return False

    def send_group_message(self, users, message):
        logger.info(f'Send group message to {users}')
        self.driver.get('https://www.instagram.com/direct/new/?hl=en')
        self.__random_sleep__(5, 7)
        try:
            for user in users:
                self.__wait_for_element__(
                    self.selectors['search_user'], "name")
                self.__type_slow__(self.selectors['search_user'], "name", user)
                self.__random_sleep__()
                elements = self.driver.find_elements(
                    By.XPATH, self.selectors['select_user'])
                if elements and len(elements) > 0:
                    elements[0].click()
                    self.__random_sleep__()
                else:
                    print(f'User {user} not found! Skipping.')
            self.type_message(message)
            self.__random_sleep__(50, 60)
            return True
        except Exception as e:
            logger.error(e)
            return False

    def __get_element__(self, element_tag, locator):
        """Wait for element and then return when it is available"""
        try:
            locator = locator.upper()
            dr = self.driver
            if locator == 'ID' and self.is_element_present(By.ID, element_tag):
                return WebDriverWait(dr, 15).until(lambda d: dr.find_element(element_tag))
            elif locator == 'NAME' and self.is_element_present(By.NAME, element_tag):
                return WebDriverWait(dr, 15).until(lambda d: dr.find_element(By.NAME, element_tag))
            elif locator == 'XPATH' and self.is_element_present(By.XPATH, element_tag):
                return WebDriverWait(dr, 15).until(lambda d: dr.find_element(By.XPATH, element_tag))
            elif locator == 'CSS' and self.is_element_present(By.CSS_SELECTOR, element_tag):
                return WebDriverWait(dr, 15).until(lambda d: dr.find_element(By.CSS_SELECTOR, element_tag))
            else:
                logger.info(f"Error: Incorrect locator = {locator}")
        except Exception as e:
            logger.error(e)
        logger.info(f"Element not found with {locator} : {element_tag}")
        return None

    def is_element_present(self, how, what):
        """Check if an element is present"""
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

    def __wait_for_element__(self, element_tag, locator, timeout=30):
        """Wait till element present. Max 30 seconds"""
        result = False
        self.driver.implicitly_wait(0)
        locator = locator.upper()
        for i in range(timeout):
            initTime = time()
            try:
                if locator == 'ID' and self.is_element_present(By.ID, element_tag):
                    result = True
                    break
                elif locator == 'NAME' and self.is_element_present(By.NAME, element_tag):
                    result = True
                    break
                elif locator == 'XPATH' and self.is_element_present(By.XPATH, element_tag):
                    result = True
                    break
                elif locator == 'CSS' and self.is_element_present(By.CSS_SELECTOR, element_tag):
                    result = True
                    break
                else:
                    logger.info(f"Error: Incorrect locator = {locator}")
            except Exception as e:
                logger.error(e)
                print(f"Exception when __wait_for_element__ : {e}")
            sleep(1 - (time() - initTime))
        else:
            print(
                f"Timed out. Element not found with {locator} : {element_tag}")
        self.driver.implicitly_wait(DEFAULT_IMPLICIT_WAIT)
        return result

    def __type_slow__(self, element_tag, locator, input_text=''):
        """Type the given input text"""
        try:
            self.__wait_for_element__(element_tag, locator, 5)
            element = self.__get_element__(element_tag, locator)
            actions = ActionChains(self.driver)
            actions.click(element).perform()
            for s in input_text:
                element.send_keys(s)
                sleep(uniform(0.05, 0.15))
        except Exception as e:
            logger.error(e)
            print(f'Exception when __typeSlow__ : {e}')

    @staticmethod
    def __random_sleep__(minimum=5, maximum=10):
        t = randint(minimum, maximum)
        print(f'Wait {t} seconds')
        sleep(t)

    def __scrolldown__(self):
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

    def teardown(self):
        self.driver.quit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()


class Instareg(Browser):
    def first_page(self, phone: str, username: str, password: str):
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

    def phone_confirmation(self, code: str) -> bool:
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
