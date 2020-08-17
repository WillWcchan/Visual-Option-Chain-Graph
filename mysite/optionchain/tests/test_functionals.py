from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from optionchain.models import Option, OptionPrice
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from datetime import datetime
from ..tradier_api import *
import time

# If testcase fail, ensure that django server is running
# python manage.py test optionchain.tests.test_functionals --parallel=4
class TestOptionChainPage(StaticLiveServerTestCase):

    def setUp(self):
        self.STOCK_TICKER_EXAMPLE = "MSFT"
        self.browser = webdriver.Chrome(executable_path="/mysite/optionchain/tests/chromedriver")

    def tearDown(self):
        self.browser.close()

    def test_index_page(self):
        self.browser.get("http://127.0.0.1:8000/optionchain")
        text_input = self.browser.find_elements_by_class_name("form-control").pop()
        self.assertEquals(
            text_input.text,
            ""
        )
    
    def test_option_type_page(self):
        self.browser.get("http://127.0.0.1:8000/optionchain")
        text_input = self.browser.find_elements_by_class_name("form-control").pop().send_keys(self.STOCK_TICKER_EXAMPLE + Keys.ENTER)
        self.assertEquals(
            self.browser.current_url,
            "http://127.0.0.1:8000/optionchain/stockTicker/?stock_ticker=" + self.STOCK_TICKER_EXAMPLE
        )

    def test_option_type_CALL_page(self):
        self.browser.get("http://127.0.0.1:8000/optionchain")
        text_input = self.browser.find_elements_by_class_name("form-control").pop().send_keys(self.STOCK_TICKER_EXAMPLE + Keys.ENTER)
        self.assertEquals(
            self.browser.current_url,
            "http://127.0.0.1:8000/optionchain/stockTicker/?stock_ticker=" + self.STOCK_TICKER_EXAMPLE
        )
        call_button = self.browser.find_element_by_class_name("btn-success").click()
        self.assertEquals(
            self.browser.current_url,
            "http://127.0.0.1:8000/optionchain/stockTicker/optionType/?option_type=CALL"
        )
        
    def test_option_type_PUT_page(self):
        self.browser.get("http://127.0.0.1:8000/optionchain")
        text_input = self.browser.find_elements_by_class_name("form-control").pop().send_keys(self.STOCK_TICKER_EXAMPLE + Keys.ENTER)
        self.assertEquals(
            self.browser.current_url,
            "http://127.0.0.1:8000/optionchain/stockTicker/?stock_ticker=" + self.STOCK_TICKER_EXAMPLE
        )
        call_button = self.browser.find_element_by_class_name("btn-danger").click()
        self.assertEquals(
            self.browser.current_url,
            "http://127.0.0.1:8000/optionchain/stockTicker/optionType/?option_type=PUT"
        )

    def test_option_date_with_valid_call_and_stock_ticker(self):
        self.browser.get("http://127.0.0.1:8000/optionchain")
        text_input = self.browser.find_elements_by_class_name("form-control").pop().send_keys(self.STOCK_TICKER_EXAMPLE + Keys.ENTER)
        self.assertEquals(
            self.browser.current_url,
            "http://127.0.0.1:8000/optionchain/stockTicker/?stock_ticker=" + self.STOCK_TICKER_EXAMPLE
        )
        call_button = self.browser.find_element_by_class_name("btn-success").click()
        self.assertEquals(
            self.browser.current_url,
            "http://127.0.0.1:8000/optionchain/stockTicker/optionType/?option_type=CALL"
        )
        expiration_button = self.browser.find_element_by_class_name("buttonOptionLinkColor")
        expiration_date = datetime.strptime(expiration_button.text, "%B %d, %Y")
        expiration_date_converted = expiration_date.strftime("%Y-%m-%d")
        expiration_button.click()
        self.assertEquals(
            self.browser.current_url,
            "http://127.0.0.1:8000/optionchain/stockTicker/optionType/optionDate/?expiration_date=" + expiration_date_converted  
        )

    def test_option_date_with_valid_put_and_stock_ticker(self):
        self.browser.get("http://127.0.0.1:8000/optionchain")
        text_input = self.browser.find_elements_by_class_name("form-control").pop().send_keys(self.STOCK_TICKER_EXAMPLE + Keys.ENTER)
        self.assertEquals(
            self.browser.current_url,
            "http://127.0.0.1:8000/optionchain/stockTicker/?stock_ticker=" + self.STOCK_TICKER_EXAMPLE
        )
        call_button = self.browser.find_element_by_class_name("btn-danger").click()
        self.assertEquals(
            self.browser.current_url,
            "http://127.0.0.1:8000/optionchain/stockTicker/optionType/?option_type=PUT"
        )
        expiration_button = self.browser.find_element_by_class_name("buttonOptionLinkColor")
        expiration_date = datetime.strptime(expiration_button.text, "%B %d, %Y")
        expiration_date_converted = expiration_date.strftime("%Y-%m-%d")
        expiration_button.click()
        self.assertEquals(
            self.browser.current_url,
            "http://127.0.0.1:8000/optionchain/stockTicker/optionType/optionDate/?expiration_date=" + expiration_date_converted  
        )

    # def test_option_table_with_valid_stock_ticker_and_strike(self):
    #     self.browser.get("http://127.0.0.1:8000/optionchain")
    #     text_input = self.browser.find_element_by_name('stock_ticker').send_keys(self.STOCK_TICKER_EXAMPLE + Keys.ENTER)
    #     self.assertEquals(
    #         self.browser.current_url,
    #         "http://127.0.0.1:8000/optionchain/stockTicker/?stock_ticker=" + self.STOCK_TICKER_EXAMPLE
    #     )
    #     call_button = self.browser.find_element_by_class_name("btn-danger").click()
    #     self.assertEquals(
    #         self.browser.current_url,
    #         "http://127.0.0.1:8000/optionchain/stockTicker/optionType/?option_type=PUT"
    #     )
    #     expiration_button = self.browser.find_element_by_class_name("buttonOptionLinkColor")
    #     expiration_date = datetime.strptime(expiration_button.text, "%B %d, %Y")
    #     expiration_date_converted = expiration_date.strftime("%Y-%m-%d")
    #     expiration_button.click()
    #     self.assertEquals(
    #         self.browser.current_url,
    #         "http://127.0.0.1:8000/optionchain/stockTicker/optionType/optionDate/?expiration_date=" + expiration_date_converted  
    #     )
    #     list_of_strikes = get_list_of_option_strikes(symbol=self.STOCK_TICKER_EXAMPLE, expiration=expiration_date_converted)["strikes"]["strike"]
    #     real_time_quote = get_real_time_quote(ticker=self.STOCK_TICKER_EXAMPLE)["quotes"]["quote"]["last"]
    #     closest_number = min(list_of_strikes, key=lambda x: abs(x - real_time_quote))
    #     list_of_options = get_option_chain(ticker=self.STOCK_TICKER_EXAMPLE, expiration=expiration_date_converted)["options"]["option"]
    #     option = [obj for obj in list_of_options if obj["strike"] == closest_number and obj["option_type"] == 'put']
    #     self.browser.get("http://127.0.0.1:8000/optionchain/stockTicker/optionType/optionDate/optionVisualGraphs/?symbol=%s+%s" % (option[0]['symbol'], option[0]['strike']))
    #     self.assertEquals(
    #         self.browser.current_url,
    #         "http://127.0.0.1:8000/optionchain/stockTicker/optionType/optionDate/optionVisualGraphs/?symbol=%s+%s" % (option[0]['symbol'], option[0]['strike'])
    #     )        

        


    
        

        