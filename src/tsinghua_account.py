from datetime import datetime
from hashlib import md5
import logging
from re import match

from bs4 import BeautifulSoup
from requests import Session, RequestException

from abstract_account import AbstractAccount


def _head_int(s):
    return int(match(r'\d+', s).group())

def _head_float(s):
    return float(match(r'\d+(\.\d+)?', s).group())

class TsinghuaAccount(AbstractAccount):
    """Tsinghua account"""
    USEREG_BASE_URL = 'https://usereg.tsinghua.edu.cn'
    USEREG_LOGIN_PAGE = USEREG_BASE_URL + '/do.php'
    USEREG_INFO_PAGE = USEREG_BASE_URL + '/user_info.php'

    def __init__(self, username):
        super().__init__(username)

    def update(self):
        """Update infos of the account.
        Return True on success, False if network errors occur.
        Raise ValueError if the username/password is incorrect, or the password
        has not been set."""
        if self.password is None:
            raise ValueError('Password of user {} has not been set'
                             .format(self.username))
        try:
            s = Session()

            # Login.
            payload = dict(action='login',
                           user_login_name=self.username,
                           user_password=md5(self.password.encode()).hexdigest())
            # FIXME: Will cause warnings.
            r = s.post(self.USEREG_LOGIN_PAGE, payload, verify=False)
            r.raise_for_status()
            if r.text != 'ok':
                raise ValueError('Incorrect username / password for user {}'
                                 .format(self.username))
            # Parse.
            # FIXME: Will cause warnings.
            r = s.get(self.USEREG_INFO_PAGE, verify=False)
            r.raise_for_status()
            return self.__parse_info_page(r.text)

        except RequestException as e:
            logging.error('Failed to update info: %s', e)
            return False

    def __parse_info_page(self, page):
        """Parse infos from the info page of usereg"""
        try:
            soup = BeautifulSoup(page, 'html.parser')

            blocks = map(BeautifulSoup.get_text, soup.select('.maintd'))
            i = map(str.strip, blocks)  # Only works in python 3.
            infos = dict(zip(i, i))

            balance = _head_float(infos['帐户余额'])
            byte = _head_int(infos['使用流量(IPV4)'])

            # No errors, write it back.
            self.balance = balance
            self.byte = byte
            self.max_byte = self.balance_to_max_byte(balance)
            self.last_check = datetime.today()
            return True
        except Exception as e:
            logging.error('Exception received while parsing info page: %s', e)
            logging.error('Info page content:\n%s', page)
            return False

    @staticmethod
    def balance_to_max_byte(balance):
        """Calculate max byte from balance"""
        return 0  # TODO: Implement.

    def login(self):
        """Return True on success, False if network errors occur.
        Raise ValueError if the username/password is incorrect, or the password
        has not been set."""
        return False  # TODO: Implement.

    @staticmethod
    def logout(self):
        """Return True on success, False otherwise."""
        return False  # TODO: Implement.

    @staticmethod
    def status(self):
        """Return (username, session_start_byte, session_sec) if logged in,
        None if not.
        Raise ConnectionError if cannot connect to login server."""
        raise ConnectionError()  # TODO: Implement.
