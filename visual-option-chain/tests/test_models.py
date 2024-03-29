from django.test import TestCase	
from django.core.exceptions import ValidationError
from ..models import Option, OptionPrice	

class TestModels(TestCase):	

    def setUp(self):	
        self.option = Option.objects.create(	
                symbol="FAKESYMBOL",	
                expiration="2020-02-20",	
                strike="120",	
                ticker="FAKE",	
                option_type="call",	
                expiration_type="weekly",            	
        )	

    def test_create_fake_valid_option(self):	
        self.assertEquals(self.option.symbol, "FAKESYMBOL")	

    def test_create_fake_invalid_option(self):	
        try:	
            self.invalid_option = Option.objects.create(	
                    symbol="FAKESYMBOL",	
                    expiration="2-2-2", # invalid DateField	
                    strike="120",	
                    ticker="FAKE",	
                    option_type="call",	
                    expiration_type="weekly"	
            )	
        except ValidationError as e:	
            self.assertTrue	

    def test_create_fake_valid_option_price(self):	
        if self.option.pk:	
            self.option_price = OptionPrice.objects.create(	
                option=self.option,	
                close=1.10,	
                close_ask=1.12,	
                close_bid=1.11,	
                delta=-1.0,	
                implied_volatility=1.82,	
                open_interest=998,	
                volume=1121,	
            )	
            self.assertEquals(self.option_price.close,1.10)	
        else:	
            self.fail("Option created in the setUp() wasn't properly created.")	

    def test_create_fake_invalid_option_price(self):	
        try:	
            self.option_price = OptionPrice.objects.create(	
                option=self.option,	
                close="I am the close", # Invalid FloatField	
                close_ask=1.12,	
                close_bid=1.11,	
                delta=-1.0,	
                implied_volatility=1.82,	
                open_interest=998,	
                volume=1121,	
            )	
        except ValueError as e:	
            self.assertTrue