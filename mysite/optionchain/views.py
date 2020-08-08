from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import Option, OptionPrice
from django.utils.dateparse import parse_date
import intrinio_sdk as intrinio
from intrinio_sdk.rest import ApiException
import datetime
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
        option_ticker = request.GET.get('option_ticker', 'none').upper().strip()
        try:
            option_exists = intrinio.OptionsApi().get_options_expirations(symbol=option_ticker, after=datetime.date.today()) 
            if option_exists:
                request.session['option_ticker'] = option_ticker
                return render(request, 'optionchain/stockTable.html', {'option': option_ticker})
        except Exception:
            return render(request, 'optionchain/index.html', {"error_message": "Unable to find stock. Please try again."})
    return render(request, 'optionchain/index.html', {"error_message": "Unable to handle request to find stock. Please try again."})

def callOptionTable(request):
    if request.method == 'GET':
        option_ticker = request.GET.get("call",request.session['option_ticker'])
        if option_ticker is not None:
            # Rest Call Source: https://docs.intrinio.com/documentation/python/get_options_expirations_v2
            options_expirations = intrinio.OptionsApi().get_options_expirations(option_ticker, after=datetime.date.today()) 
            options_expirations_converted = [parse_date(date) for date in options_expirations.expirations]
            
            context = {
                'option_ticker':option_ticker,
                'options_expirations': options_expirations_converted
            }

            if options_expirations is not None:
                return render(request, 'optionchain/callOptionTable.html',context)
            else:
                return HttpResponse("No option found.")
    return HttpResponse("Call option Table")

def callOptionGraph(request):
    if request.method == 'GET':
        ticker = request.GET.get("option_ticker",request.session['option_ticker'])
        type = 'call'

        # Get the realtime stock price for security
        current_stock_price = intrinio.SecurityApi().get_security_realtime_price(identifier=ticker)

        try:
            expiration = request.GET.get("expiration_date","")
            expiration_date = parse_date(expiration)
        except ValueError:
            return HttpResponse("Incorrect expiration date format: " + expiration)

        if ticker is not None and expiration_date is not None:
           option_exist_on_db = Option.objects.all().filter(ticker=ticker).filter(expiration=expiration_date)
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
                response = intrinio.OptionsApi().get_options_chain(symbol=ticker, expiration=expiration, type='call')
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
                    
        context = {
            "option_ticker": ticker,
            "option_expiration": expiration_date,
            "list_of_optionChain":list_of_optionChain,
            "current_ask_price":current_stock_price.ask_price,
            "current_bid_price":current_stock_price.bid_price
        }

        if ticker is not None and expiration_date is not None and list_of_optionChain is not None:
            return render(request, 'optionchain/callOptionGraphs.html',context=context)
    return HttpResponse("Nothing found")

def putOptionTable(request):
    return HttpResponse("Put option Table")    
