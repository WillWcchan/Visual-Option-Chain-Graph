from django.db import models

# Returns all options contracts and their prices for the given symbol and expiration date.
class Option(models.Model):
    symbol = models.CharField(max_length=30, null=True)
    expiration = models.DateField()
    strike = models.FloatField(default=0.0)
    ticker = models.CharField(max_length=8)
    type = models.CharField(max_length=4)
    expiration_type = models.CharField(max_length=8)

    def __str__(self):
        return "Symbol: %s, Expiration: %s, Strike: %s, Ticker: %s, Type: %s, Expiration: %s" %(self.symbol, self.expiration, self.strike, self.ticker, self.type, self.expiration_type)

    def save(self, *args, **kwargs):
        # Don't save if found
        try:
            self.type = self.type.lower()
            option = Option.objects.get(ticker=self.ticker,expiration=self.expiration,strike=self.strike)
        except self.DoesNotExist:
            super().save(*args, **kwargs)

# Returns all option prices for a given option contract identifier.
# For every 1 Option contract, there are many option prices
class OptionPrice(models.Model):
    option = models.ForeignKey(Option, on_delete=models.CASCADE, null=True, blank=True) 
    close = models.FloatField(default=0.0, null=True)
    close_ask = models.FloatField(default=0.0)
    close_bid = models.FloatField(default=0.0)        
    delta = models.FloatField(default=None, null=True)
    implied_volatility = models.FloatField(default=None, null=True)
    open_interest = models.IntegerField(default=0)
    trades = models.IntegerField(default=0)
    volume = models.IntegerField(default=0)
    volume_ask = models.IntegerField(default=0)
    volume_bid = models.IntegerField(default=0)

    def __str__(self):
        return "close: %s, close_ask: %s, close_bid: %s, delta: %s, implied_volatility: %s" %(self.close, self.close_ask, self.close_bid,  self.delta, self.implied_volatility)

    def save(self, *args, **kwargs):
        # Don't save if found
        try:      
            optionPrice = OptionPrice.objects.get(
                close=self.close,
                close_ask=self.close_ask,
                close_bid=self.close_bid,
                delta=self.delta,
                implied_volatility=self.implied_volatility,
                open_interest=self.open_interest,
                volume=self.volume,
            )
        except self.DoesNotExist:
            super().save(*args, **kwargs)      