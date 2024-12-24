
# Import Libraries
import os
import json
import time
import urllib
from selenium import webdriver
from kiteconnect import KiteConnect
import hmac, base64, struct, hashlib, time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from dotenv import load_dotenv
load_dotenv()


class Selenium:

    def __init__(self) -> None:

        options = Options()
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


class LoginKite(Selenium):

    def __init__(self):
        self.user_id = os.getenv('USER_ID')
        self.pass_word = os.getenv('PASSWORD')
        self.api_key = os.getenv('API_KEY')
        self.auth_key = os.getenv('AUTH_KEY')
        self.api_secret = os.getenv('API_SECRET')
        super().__init__()

    def get_hotp_token(self,secret, intervals_no):

        key = base64.b32decode(secret, True)
        msg = struct.pack(">Q", intervals_no)
        h = hmac.new(key, msg, hashlib.sha1).digest()
        o = h[19] & 15
        h = (struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 1000000
        return h

    def get_external_totp(self, secret):
        totp = str(self.get_hotp_token(secret, intervals_no=int(time.time()) // 30))
        if len(totp) < 6:
            totp = '0' + totp
        return totp

    def generate_request_token(self,login_url=""):

        self.driver.get(login_url)
        time.sleep(2)

        login_page_input_fields = self.driver.find_elements(By.TAG_NAME, 'input')
        login_page_input_fields[0].send_keys(self.user_id)
        login_page_input_fields[1].send_keys(self.pass_word)
        login_page_input_fields[1].send_keys(Keys.ENTER)
        time.sleep(2)

        external_totp = self.get_external_totp(os.getenv('AUTH_KEY'))

        auth_page_input_fields = self.driver.find_elements(By.TAG_NAME, 'input')
        auth_page_input_fields[0].send_keys(str(external_totp))
        # auth_page_input_fields[0].send_keys(Keys.ENTER)
        time.sleep(2)

        redirect_url = self.driver.current_url
        parsed = urllib.parse.urlparse(redirect_url)
        query_dict = dict(urllib.parse.parse_qsl(parsed.query))
        print(query_dict)
        self.driver.quit()

        return query_dict['request_token']

    def generate_kite_session(self):

        kite = KiteConnect(api_key=self.api_key)


        meta_data = {"success":True}


        try:
            request_token = self.generate_request_token(login_url=kite.login_url())
            meta_data['request_token'] = request_token

            data = kite.generate_session(request_token, api_secret=self.api_secret)
            meta_data.update(data)

            meta_data['login_time'] = meta_data['login_time'].strftime('%d:%m:%Y %H:%M:%S')

            kite.set_access_token(data["access_token"])

            print(f"{meta_data['user_name']} has successfully signed in.")

        except Exception as ex:
            template = "An exception of type {0} occurred. {1!r}"
            message = template.format(type(ex).__name__, str(ex))

            meta_data['success']=False
            meta_data['error'] = "User Authentication Failed"
            meta_data['exception'] = message

        return kite,meta_data



