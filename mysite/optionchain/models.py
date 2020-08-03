from django.db import models

# Returns all options contracts and their prices for the given symbol and expiration date.
# Source: https://docs.intrinio.com/documentation/web_api/get_options_chain_v2
class Option(models.Model):
    stockName = models.CharField(max_length=50)
    ticker = models.CharField(max_length=8)
    # Modify DATE format for Model (Example: 2019-04-05)
    expiration = models.DateField()
    strike = models.IntegerField(default=0)
    type = models.CharField(max_length=4)

    def __str__(self):
        return self.stockName

# Returns all option prices for a given option contract identifier.
# Source: https://docs.intrinio.com/documentation/web_api/get_options_prices_v2
class OptionPrice(models.Model):
    # For every 1 Option contract, there are many option prices
    option = models.ForeignKey(Option, on_delete=models.CASCADE) 
    date = models.DateField()
    close = models.FloatField(default=0.0)
    close_bid = models.FloatField(default=0.0)
    close_ask = models.FloatField(default=0.0)
    volume = models.IntegerField(default=0)
    volume_bid = models.IntegerField(default=0)
    volume_ask = models.IntegerField(default=0)
    trades = models.IntegerField(default=0)
    open_interest = models.IntegerField(default=0)
    open_interest_change = models.IntegerField(default=0)
    next_day_open_interest = models.IntegerField(default=0)
    implied_volatility = models.FloatField(default=0)
    implied_volatility_change = models.FloatField(default=0)
    delta = models.FloatField(default=0)

    def __str__(self):
        return self.option.stockName
