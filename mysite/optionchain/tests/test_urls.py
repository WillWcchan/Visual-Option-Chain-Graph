from django.test import SimpleTestCase
from django.urls import reverse, resolve
from optionchain.views import index, stock_ticker, option_type, option_table, option_visual_graphs

class TestUrls(SimpleTestCase):

    def test_index_url_is_resolved(self):
        url = reverse('optionchain:index')
        self.assertEquals(resolve(url).func, index)

    def test_stock_ticker_url_is_resolved(self):
        url = reverse('stock_ticker')
        self.assertEquals(resolve(url).func, stock_ticker)

    def test_optionType_url_is_resolved(self):
        url = reverse('optionType')
        self.assertEquals(resolve(url).func, option_type)

    def test_optionTable_url_is_resolved(self):
        url = reverse('optionTable')
        self.assertEquals(resolve(url).func, option_table)
             
    def test_optionVisualGraphs_url_is_resolved(self):
        url = reverse('optionVisualGraphs')
        self.assertEquals(resolve(url).func, option_visual_graphs)