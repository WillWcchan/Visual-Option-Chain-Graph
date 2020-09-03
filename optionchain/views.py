from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Option, OptionPrice
from django.utils.dateparse import parse_date
from django.core.cache import cache
from .tradier_api import *
import requests
import json
import sys
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('optionchain')

# Source: https://testdriven.io/blog/django-caching/x
CACHE_TTL = 10080 # Cache time to live for a week (60 * 24 * 7)
CACHE_EXPIRATION_DATE = 60 * 5 # Cache time to live for 5 minutes

def index(request):
    return render(request, 'optionchain/index.html')

def stock_ticker(request):
    if api_key is None or api_key == "":
       logger.critical("No API KEY provided")

    if request.method == 'GET':
        stock_ticker = request.GET.get('stock_ticker')
        logger.info("Stock ticker entered: %s" %stock_ticker)
        if not stock_ticker:
            return render(request, 'optionchain/index.html', {"error_message": "You've entered an empty ticker Try again."})
        else:
            if stock_ticker.isalpha():
                stock_ticker = stock_ticker.upper().strip()
                saved = cache.set("stock_ticker", stock_ticker, timeout=CACHE_TTL)
                if saved:
                    logger.info("Successfully saved %s in redis cache" % stock_ticker)        
            else:
                return render(request, 'optionchain/index.html', {"error_message": "You've entered a value with a number. Please try again with a real ticker"})

        try:
            expiration_list = cache.get(stock_ticker + "expiration_list")
            if not expiration_list:
                expiration_list = get_option_expirations(stock_ticker=stock_ticker)
                saved = cache.set(stock_ticker + "expiration_list", expiration_list, timeout=CACHE_TTL)
                if saved:
                    logger.info("Successfully saved %s\'s expiration list in redis cache" % stock_ticker)

            logger.info("%s\s expiration_list: %s" %(stock_ticker, expiration_list))
            if expiration_list and len(expiration_list) > 0:
                return render(request, 'optionchain/optionType.html', {'stock_ticker': stock_ticker})
            else:
                return render(request, 'optionchain/index.html', {"error_message": "Unable to find expirations %s. Try another ticker" %stock_ticker})
        except Exception as e:
            logger.exception(e)
            return render(request, 'optionchain/index.html', {"error_message": e})


def option_type(request):
    if request.method == 'GET':
        option_type = request.GET.get("option_type", None)
        logger.info("option type %s was found and saved as a session" %option_type)
        request.session['type'] = option_type
        stock_ticker = cache.get("stock_ticker")
        if stock_ticker:
            options_expirations_converted = cache.get(stock_ticker + "expiration_list")

            context = {
                'stock_ticker': stock_ticker,
                'type': option_type,
                'options_expirations': options_expirations_converted
            }

            logger.info("%s %s" % (stock_ticker, option_type))
            if options_expirations_converted and option_type and len(options_expirations_converted) > 0:
                return render(request, 'optionchain/optionDate.html', context)
            else:
                return render(request, 'optionchain/index.html', {"error_message": "No options expirations found for this ticker. Try another ticker"})


def option_table(request):
    if request.method == 'GET':
        stock_ticker = cache.get("stock_ticker")
        option_type = request.session['type']

        try:
            expiration = request.GET.get("expiration_date", "")
            expiration_date = parse_date(expiration)
            logger.info("Able to parse in the expiration date %s" %expiration)
        except ValueError as e:
            logger.exception(e)
            return HttpResponse("Incorrect expiration date format: " + expiration)

        if stock_ticker and expiration_date:
            logger.info("Check if we have an option stored in our database for %s and %s" % (stock_ticker, expiration_date))
            option_list = Option.objects.all().filter(ticker=stock_ticker).filter(expiration=expiration_date).filter(type=option_type)        
            if option_list.count() > 0:
                for option in option_list:
                    option_price = OptionPrice.objects.filter(option=option).first()        
                    if option_price:
                        list_of_optionChain.append(
                            {
                                'option': {
                                    'symbol': option.symbol,
                                    'expiration': str(option.expiration),
                                    'id': option.intrinio_id,
                                    'strike': option.strike,
                                    'ticker': option.ticker,
                                    'type': option.type,
                                    'expiration_type': option.expiration_type,
                                },
                                    'price': {
                                    'close': option_price.close,
                                    'close_ask': option_price.close_ask,
                                    'close_bid': option_price.close_bid,
                                    'date': str(option_price.date),
                                    'delta': option_price.delta,
                                    'implied_volatility': option_price.implied_volatility,
                                    'implied_volatility_change': option_price.implied_volatility_change,
                                    'next_day_open_interest': option_price.next_day_open_interest,
                                    'open_interest': option_price.open_interest,
                                    'open_interest_change': option_price.open_interest_change,
                                    'trades': option_price.trades,
                                    'volume': option_price.volume,
                                    'volume_ask': option_price.volume_ask,
                                    'volume_bid': option_price.volume_bid
                                    }
                            }
                        )
                    else:
                        return HttpResponse("No option price for this option")
            else:
                logger.info("Option does not exist in our database. Will make a REST API call to Tradier with %s and %s" %(stock_ticker, expiration_date))
                response = get_option_chain(ticker=stock_ticker, expiration=expiration)
                logger.info("Recieved option chain from Tradier API")
                list_of_optionChain = response["options"]["option"]

                for option in list_of_optionChain:
                    option_symbol = option["symbol"]
                    option_expiration = option["expiration_date"]
                    option_strike = option["strike"]
                    option_ticker = option["underlying"]
                    option_type = option["option_type"]
                    option_expiration_type = option["expiration_type"]

                    logger.info("Creating the option and storing into the database")
                    option_create = Option(
                        symbol=option_symbol,
                        expiration=parse_date(option_expiration),
                        strike=option_strike,
                        ticker=option_ticker,
                        type=option_type,
                        expiration_type=option_expiration_type,
                    )
                    option_create.save()
                    logger.info("Finished creating the option %s" %(option_create))

                    if option_create.pk:
                        option_price_close = option["close"]
                        option_price_close_ask = option["ask"]
                        option_price_close_bid = option["bid"]

                        try:
                            option_price_delta = option["greeks"]["delta"]
                            option_price_implied_volatility = option["greeks"]["ask_iv"]
                        except KeyError as e:
                            # greek is not available for this stock_ticker, possibly new stock
                            option_price_delta = 0
                            option_price_implied_volatility = 0

                        option_price_open_interest = option["open_interest"]
                        option_price_volume = option["volume"]
                        logger.info("Creating the optionPrice for the recently created option to store into the database")
                        OptionPrice.objects.create(
                            option=option_create,
                            close=option_price_close,
                            close_ask=option_price_close_ask,
                            close_bid=option_price_close_bid,
                            delta=option_price_delta,
                            implied_volatility=option_price_implied_volatility,
                            open_interest=option_price_open_interest,
                            volume=option_price_volume,
                        )
                        logger.info("Finished creating the optionPrice")

        quote = cache.get(stock_ticker + "real_time_quote")
        if not quote:
            quote = get_real_time_quote(ticker=stock_ticker)["quotes"]["quote"]
            saved = cache.set(stock_ticker + "real_time_quote", quote, timeout=CACHE_EXPIRATION_DATE)
            if saved:
                logger.info("Saved real time quote %s for 5 minutes" %stock_ticker)

        context = {
            "stock_ticker": stock_ticker,
            "type": option_type.lower(),
            "option_expiration": expiration_date,
            "list_of_optionChain": list_of_optionChain,
            "current_ask_price": quote['ask'],
            "current_bid_price": quote['bid']
        }

        if stock_ticker and expiration_date and list_of_optionChain:
            return render(request, 'optionchain/optionTable.html', context=context)

def option_visual_graphs(request):
    if request.method == 'GET':
        symbolAndStrike = request.GET.get("symbol", "")
        symbol, strike = symbolAndStrike.split(" ")[0], symbolAndStrike.split(" ")[1]
        
        if symbol and len(symbol) > 0:
            # Shows the daily Graph
            daily_timestamps = []
            daily_price = []
            try:
                logger.info("Making RESTAPI call to Tradier to get the daily timestamps and price")
                response = get_time_and_sales(symbol=symbol, interval="daily")
                if response is None or response['series'] is None:
                    return render(request, 'optionchain/index.html', {"error_message": "No time and sales for this daily %s. Visit an actual brokerage for their option graph." %symbol})
                daily_timestamps, daily_price = get_timestamp_and_price(json_response=response, interval="daily")
                logger.info("Got and parsed the daily timestamps and price successfully")   
            except Exception as e:
                logger.exception(e)

            if len(daily_timestamps) == 0 or len(daily_price) == 0:
                logger.warning("Daily_timestamps or daily_price were parsed successfully, but one of them are empty for symbol: %s" % (symbol))

            context = {
                'stock_ticker': symbol,
                'strike': strike,
                'daily_timestamps': daily_timestamps,
                'daily_price': daily_price
            }

            return render(request, 'optionchain/optionVisualGraphs.html', context)
        else:
            return render(request, 'optionchain/index.html', {"error_message": "Unable to plot the graph. Check if the parameters are correct or even the date."})