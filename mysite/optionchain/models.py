from django.db import models

# Returns all options contracts and their prices for the given symbol and expiration date.
class Option(models.Model):
    intrinio_code = models.CharField(max_length=30, null=True)
    expiration = models.DateField()
    intrinio_id = models.CharField(max_length=20, null=True)
    strike = models.FloatField(default=0.0)
    ticker = models.CharField(max_length=8)
    type = models.CharField(max_length=4)

    def __str__(self):
        return "Intrinio_code: %s, Expiration: %s, Intrinio_id: %s, Strike: %s, Ticker: %s, Type: %s" %(self.intrinio_code, self.expiration, self.intrinio_id, self.strike, self.ticker, self.type)

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
    option = models.ForeignKey(Option, on_delete=models.CASCADE) 
    close = models.FloatField(default=0.0)
    close_ask = models.FloatField(default=0.0)
    close_bid = models.FloatField(default=0.0)        
    date = models.DateField()
    delta = models.FloatField(default=None, null=True)
    implied_volatility = models.FloatField(default=None, null=True)
    implied_volatility_change = models.FloatField(default=None, null=True)    
    next_day_open_interest = models.IntegerField(default=0)
    open_interest = models.IntegerField(default=0)
    open_interest_change = models.IntegerField(default=0)
    trades = models.IntegerField(default=0)
    volume = models.IntegerField(default=0)
    volume_ask = models.IntegerField(default=0)
    volume_bid = models.IntegerField(default=0)

    def __str__(self):
        return "close: %s, close_ask: %s, close_bid: %s, date: %s, delta: %s, implied_volatility: %s, implied_volatility_change: %s" %(self.close, self.close_ask, self.close_bid, str(self.date),  self.delta, self.implied_volatility, self.implied_volatility_change)

    def save(self, *args, **kwargs):
        # Don't save if found
        try:
            optionPrice = OptionPrice.objects.get(close=self.close,close_ask=self.close_ask,close_bid=self.close_bid,date=self.date
            ,delta=self.delta,implied_volatility=self.implied_volatility,implied_volatility_change=self.implied_volatility_change,
            next_day_open_interest=self.next_day_open_interest,open_interest=self.open_interest,
            open_interest_change=self.open_interest_change,trades=self.trades,volume=self.volume,
            volume_ask=self.volume_ask,volume_bid=self.volume_bid)
        except self.DoesNotExist:
            super().save(*args, **kwargs)        