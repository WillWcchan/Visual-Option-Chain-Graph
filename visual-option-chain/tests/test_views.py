from django.test import TestCase, Client
from django.urls import reverse
from ..models import Option, OptionPrice
from ..tradier_api import *
import json

class TestViews(TestCase):

    # Command: python manage.py test optionchain.tests.test_views.TestViews.setUp
    def setUp(self):
        self.client = Client()
        self.index_url = reverse('index')
        self.stock_ticker_url = reverse('stock_ticker')
        self.option_type_url = reverse('optionType')
        self.option_table_url = reverse('optionTable')
        self.option_visual_graph_url = reverse('optionVisualGraphs')
        self.STOCK_TICKER_EXAMPLE = "IBM"

    # Command: python manage.py test optionchain.tests.test_views.TestViews.test_stock_ticker_GET
    def test_index_GET(self):
        response = self.client.get(self.index_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_stock_ticker_GET_with_empty_string(self):
        response = self.client.get(self.stock_ticker_url + "?stock_ticker=")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_stock_ticker_GET_with_invalid_ticker(self):
        response = self.client.get(self.stock_ticker_url + "?stock_ticker=ROFL")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_stock_ticker_GET_with_valid_ticker(self):
        response = self.client.get(self.stock_ticker_url + "?stock_ticker=" + self.STOCK_TICKER_EXAMPLE)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'optionType.html')
        
    def test_stock_ticker_GET_with_numeric_stock_ticker(self):
        response = self.client.get(self.stock_ticker_url + "?stock_ticker=1")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
    
    def test_option_type_GET_with_valid_ticker_and_call_option_type(self):
        response = self.client.get(self.stock_ticker_url + "?stock_ticker=" + self.STOCK_TICKER_EXAMPLE)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'optionType.html')
        response = self.client.get(self.option_type_url + "?option_type=call")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'optionDate.html')

    def test_option_type_GET_with_valid_ticker_and_put_option_type(self):
        response = self.client.get(self.stock_ticker_url + "?stock_ticker=" + self.STOCK_TICKER_EXAMPLE)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'optionType.html')
        response = self.client.get(self.option_type_url + "?option_type=put")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'optionDate.html')

    def test_option_table_GET_with_valid_ticker_and_call_option_type(self):
        response = self.client.get(self.stock_ticker_url + "?stock_ticker=" + self.STOCK_TICKER_EXAMPLE)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'optionType.html')
        response = self.client.get(self.option_type_url + "?option_type=call")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'optionDate.html')
        options_expirations_converted = get_option_expirations(stock_ticker=self.STOCK_TICKER_EXAMPLE)
        response = self.client.get(self.option_table_url + "?expiration_date=" + str(options_expirations_converted[0]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'optionTable.html')        

    def test_option_table_GET_with_valid_ticker_and_put_option_type(self):
        response = self.client.get(self.stock_ticker_url + "?stock_ticker=" + self.STOCK_TICKER_EXAMPLE)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'optionType.html')
        response = self.client.get(self.option_type_url + "?option_type=put")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'optionDate.html')
        options_expirations_converted = get_option_expirations(stock_ticker=self.STOCK_TICKER_EXAMPLE)
        response = self.client.get(self.option_table_url + "?expiration_date=" + str(options_expirations_converted[0]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'optionTable.html')

    def test_option_visual_graph_GET_with_valid_ticker_and_call_and_strike_price(self):
        response = self.client.get(self.stock_ticker_url + "?stock_ticker=" + self.STOCK_TICKER_EXAMPLE)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'optionType.html')
        response = self.client.get(self.option_type_url + "?option_type=call")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'optionDate.html')
        options_expirations_converted = get_option_expirations(stock_ticker=self.STOCK_TICKER_EXAMPLE)
        response = self.client.get(self.option_table_url + "?expiration_date=" + str(options_expirations_converted[0]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'optionTable.html')
        list_of_strikes = get_list_of_option_strikes(symbol=self.STOCK_TICKER_EXAMPLE,expiration=options_expirations_converted[0])["strikes"]["strike"]
        real_time_quote = get_real_time_quote(ticker=self.STOCK_TICKER_EXAMPLE)["quotes"]["quote"]["last"]
        closest_number = min(list_of_strikes, key=lambda x: abs(x - real_time_quote))
        symbol = Option.objects.filter(ticker=self.STOCK_TICKER_EXAMPLE, strike=closest_number).first()
        response = self.client.get(self.option_visual_graph_url + "?symbol=" + symbol.symbol + "+" + str(closest_number))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'optionVisualGraphs.html')         
