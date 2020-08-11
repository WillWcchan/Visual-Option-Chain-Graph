from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import Option, OptionPrice
from django.utils.dateparse import parse_date
from intrinio_sdk.rest import ApiException
from datetime import datetime as dt, timedelta
from datetime import date
from matplotlib import pylab
from io import BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import base64
import intrinio_sdk as intrinio
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import requests
import json
import sys


# https://github.com/intrinio/python-sdk
intrinio.ApiClient().configuration.api_key['api_key'] = ''

# Create your views here.
def index(request):
    return render(request, 'optionchain/index.html')

def stockName(request):
    if request.method == 'GET':
        stock_ticker = request.GET.get('stock_ticker', 'none').upper().strip()
        try:
            option_exists = intrinio.OptionsApi().get_options_expirations(symbol=stock_ticker, after=str(date.today()))
            if option_exists.expirations is not None:
                request.session['stock_ticker'] = stock_ticker
                return render(request, 'optionchain/stockTable.html', {'option': stock_ticker})
            else:
                return render(request, 'optionchain/index.html', {"error_message": "Unable to find expirations for this ticker. Try another ticker"})
        except Exception as e:
            return render(request, 'optionchain/index.html', {"error_message": e})
    return render(request, 'optionchain/index.html', {"error_message": "Unable to handle request to find stock. Please try again."})

def callOptionTable(request):
    if request.method == 'GET':
        stock_ticker = request.GET.get("call",request.session['stock_ticker'])
        if stock_ticker is not None:
            # Rest Call Source: https://docs.intrinio.com/documentation/python/get_options_expirations_v2
            options_expirations = intrinio.OptionsApi().get_options_expirations(symbol=stock_ticker, after=str(date.today())) 
            options_expirations_converted = [parse_date(date) for date in options_expirations.expirations]
            
            context = {
                'stock_ticker':stock_ticker,
                'options_expirations': options_expirations_converted
            }

            if len(options_expirations_converted) > 0:
                return render(request, 'optionchain/callOptionTable.html',context)
            else:
                return render(request,'optionchain/index.html', {"error_message": "No options expirations found for this ticker. Try another ticker"})
    return HttpResponse("Call option Table")

def callOptionGraph(request):
    if request.method == 'GET':
        stock_ticker = request.GET.get("stock_ticker",request.session['stock_ticker'])
        type = 'call'

        # Get the realtime stock price for security
        current_stock_price = intrinio.SecurityApi().get_security_realtime_price(identifier=stock_ticker)

        try:
            expiration = request.GET.get("expiration_date","")
            expiration_date = parse_date(expiration)
            request.session['expiration_date'] = expiration
        except ValueError:
            return HttpResponse("Incorrect expiration date format: " + expiration)

        if stock_ticker is not None and expiration_date is not None:
           option_exist_on_db = Option.objects.all().filter(ticker=stock_ticker).filter(expiration=expiration_date)
           if option_exist_on_db.count() > 0:
              list_of_optionChain = []
              for option in option_exist_on_db:
                  optionPrice = OptionPrice.objects.filter(option=option).first()
                  if optionPrice is not None:
                    list_of_optionChain.append(
                        {'option': {
                            'code': option.intrinio_code,
                            'expiration': str(option.expiration),
                            'id': option.intrinio_id,
                            'strike': option.strike,
                            'ticker': option.ticker,
                            'type': option.type,
                        },
                        'price': {
                            'close':optionPrice.close,
                            'close_ask':optionPrice.close_ask,
                            'close_bid':optionPrice.close_bid,
                            'date':str(optionPrice.date),
                            'delta':optionPrice.delta,
                            'implied_volatility':optionPrice.implied_volatility,
                            'implied_volatility_change':optionPrice.implied_volatility_change,
                            'next_day_open_interest': optionPrice.next_day_open_interest,
                            'open_interest': optionPrice.open_interest,
                            'open_interest_change':optionPrice.open_interest_change,
                            'trades':optionPrice.trades,
                            'volume':optionPrice.volume,
                            'volume_ask':optionPrice.volume_ask,
                            'volume_bid':optionPrice.volume_bid
                        }
                        }
                    )
                  else:
                     return HttpResponse("No option price for this option")
           else:
                response = intrinio.OptionsApi().get_options_chain(symbol=stock_ticker, expiration=expiration, type='call')
                list_of_optionChain = response.chain

                for option in list_of_optionChain:
                    option_code = option.option.code
                    option_expiration = option.option.expiration
                    option_id = option.option.id
                    option_strike = option.option.strike
                    option_ticker = option.option.ticker
                    option_type = option.option.type

                    # Create the Option object and store into the database
                    option_create = Option(
                        intrinio_code = option_code,
                        expiration = parse_date(option_expiration),
                        intrinio_id = option_id,
                        strike = option_strike,
                        ticker = option_ticker,
                        type = option_type
                    )
                    # Save or else we get an exception where save() prohibited to prevent data loss due to unsaved related object
                    option_create.save()

                    option_price_close = option.price.close
                    option_price_close_ask = option.price.close_ask
                    option_price_close_bid = option.price.close_bid
                    option_price_date = option.price.date
                    option_price_delta = option.price.delta
                    option_price_implied_volatility = option.price.implied_volatility
                    option_price_implied_volatility_change = option.price.implied_volatility_change
                    option_price_next_day_open_interest = option.price.next_day_open_interest
                    option_price_open_interest = option.price.open_interest
                    option_price_open_interest_change = option.price.open_interest_change
                    option_price_trades = option.price.trades
                    option_price_volume = option.price.volume
                    option_price_volume_ask = option.price.volume_ask
                    option_price_volume_bid = option.price.volume_bid
                    
                    option_price_create = OptionPrice(
                        option = option_create,
                        close = option_price_close,
                        close_ask = option_price_close_ask,
                        close_bid = option_price_close_bid,
                        date = parse_date(option.price.date),
                        delta = option_price_delta,
                        implied_volatility = option_price_implied_volatility,
                        implied_volatility_change = option_price_implied_volatility_change,
                        next_day_open_interest = option_price_next_day_open_interest,
                        open_interest = option_price_open_interest,
                        open_interest_change = option_price_open_interest_change,
                        trades = option_price_trades,
                        volume = option_price_volume,
                        volume_bid = option_price_volume_ask,
                        volume_ask = option_price_volume_ask
                    )

                    option_price_create.save()

        if current_stock_price.ask_price is not None and current_stock_price.bid_price is not None:
           request.session['current_ask_price'] = current_stock_price.ask_price
           request.session['current_bid_price'] = current_stock_price.bid_price
                    
        context = {
            "stock_ticker": stock_ticker,
            "option_expiration": expiration_date,
            "list_of_optionChain":list_of_optionChain,
            "current_ask_price":current_stock_price.ask_price,
            "current_bid_price":current_stock_price.bid_price
        }

        if stock_ticker is not None and expiration_date is not None and list_of_optionChain is not None:
            return render(request, 'optionchain/callOptionGraphs.html',context=context)
    return HttpResponse("Nothing found")

def callOptionVisualGraphs(request):
    if request.method == 'GET':
       stock_option_ticker = request.GET.get("stock_option_ticker","")
       option_ticker = request.GET.get("option_ticker",request.session['option_ticker'])
       expiration_date = request.GET.get("expiration_date",request.session['expiration_date'])

       if stock_option_ticker is not None and len(stock_option_ticker) > 0:
          request.session['stock_option_ticker'] = stock_option_ticker
          start = date.today()
          end = date.today() + timedelta(1)
          response = requests.get('https://sandbox.tradier.com/v1/markets/timesales',
                params={'symbol': stock_option_ticker, 'interval': '5min', 'start': str(date.today() - timedelta(days=5)), 'end': str(date.today() - timedelta(days=4)), 'session_filter': 'all'},
                headers={'Authorization': 'Bearer ', 'Accept': 'application/json'})
          json_response = response.json()
          if json_response['series'] is not None:
            timestamps = [str(dt.strptime(data['time'],"%Y-%m-%dT%H:%M:%S").time()) for data in json_response["series"]["data"]]
            price = [data['price'] for data in json_response["series"]["data"]]
            
            plt.clf() # Clears the entire current figure
            plt.xkcd()
            plt.plot(timestamps,price)
            plt.xlabel("Time",fontsize=18)
            plt.ylabel("Price",fontsize=18)
            plt.xticks(rotation=45)
            plt.tight_layout()

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()

            graphic = base64.b64encode(image_png)
            graphic = graphic.decode('utf-8')

            context = {
                'graph':graphic,
            }
            return render(request, 'optionchain/callOptionVisualGraphs.html',context)
          else:
            return render(request, 'optionchain/index.html', {"error_message": "Unable to plot the graph. Check if the parameters are correct or even the date."})

def putOptionTable(request):
    return HttpResponse("Put option Table")    
