from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Option, OptionPrice
from django.utils.dateparse import parse_date
from .tradier_api import *
import base64
import requests
import json
import sys
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('optionchain')

# Source: https://testdriven.io/blog/django-caching/x
def index(request):
    return render(request, 'optionchain/index.html')

def stock_ticker(request):
    if api_key is None or api_key == "":
       logger.critical("No API KEY provided")

    if request.method == 'GET':
        stock_ticker = request.GET.get('stock_ticker')
        if not stock_ticker:
            logger.error("%s was not found" %stock_ticker)
            return render(request, 'optionchain/index.html', {"error_message": "You've entered an empty ticker Try again."})
        else:
            if stock_ticker.isalpha():
                logger.info("%s was found" %stock_ticker)
                stock_ticker = stock_ticker.upper().strip()
                request.session["stock_ticker"] = stock_ticker
            else:
                return render(request, 'optionchain/index.html', {"error_message": "You've entered a value with a number. Please try again with a real ticker"})

        try: 
            option_exists = get_option_expirations(stock_ticker=stock_ticker)
            if option_exists and len(option_exists) > 0:
                logger.info("option's expiration exist for this stock ticker")
                return render(request, 'optionchain/optionType.html', {'stock_ticker': stock_ticker})
            else:
                logger.error("option's expiration does not exist for this stock ticker")
                return render(request, 'optionchain/index.html', {"error_message": "Unable to find expirations %s. Try another ticker" %stock_ticker})
        except Exception as e:
            logger.exception(e)
            return render(request, 'optionchain/index.html', {"error_message": e})
    return render(request, 'optionchain/index.html', {"error_message": "Ensure the request method is a GET."})


def option_type(request):
    if request.method == 'GET':
        type = request.GET.get("option_type", None)
        if type is None:
            logger.error("option type was None")
        else:
            logger.info("option type %s was found and saved as a session" %type)
            request.session['type'] = type

        stock_ticker = request.session["stock_ticker"]
        if stock_ticker:
            options_expirations_converted = get_option_expirations(
                stock_ticker=stock_ticker)

            context = {
                'stock_ticker': stock_ticker,
                'type': type,
                'options_expirations': options_expirations_converted
            }

            if options_expirations_converted and type and len(options_expirations_converted) > 0:
                logger.info("option_expiration_converted and type are valid")
                return render(request, 'optionchain/optionDate.html', context)
            else:
                logger.info("option_expiration_converted and type are invalid")
                return render(request, 'optionchain/index.html', {"error_message": "No options expirations found for this ticker. Try another ticker"})
    else:
        return render(request, 'optionchain/index.html', {"error_message": "Ensure the request method is a GET."})


def option_table(request):
    if request.method == 'GET':
        stock_ticker = request.session["stock_ticker"]
        type = request.session['type']

        try:
            expiration = request.GET.get("expiration_date", "")
            expiration_date = parse_date(expiration)
            logger.info("Able to parse in the expiration date")
            request.session['expiration_date'] = expiration
        except ValueError as e:
            logger.exception(e)
            return HttpResponse("Incorrect expiration date format: " + expiration)

        if stock_ticker and expiration_date:
            logger.info("Check if we have an option stored into our database for %s and %s" %(stock_ticker, expiration_date))
            option_exist_on_db = Option.objects.all().filter(ticker=stock_ticker).filter(expiration=expiration_date).filter(type=type)
            if option_exist_on_db.count() > 0:
                logger.info("Option exists in our database.")
                for option in option_exist_on_db:
                    optionPrice = OptionPrice.objects.filter(
                        option=option).first()
                    if optionPrice:
                        list_of_optionChain.append(
                            {'option': {
                                'symbol': option.symbol,
                                'expiration': str(option.expiration),
                                'id': option.intrinio_id,
                                'strike': option.strike,
                                'ticker': option.ticker,
                                'type': option.type,
                                'expiration_type': option.expiration_type,
                            },
                                'price': {
                                'close': optionPrice.close,
                                'close_ask': optionPrice.close_ask,
                                'close_bid': optionPrice.close_bid,
                                'date': str(optionPrice.date),
                                'delta': optionPrice.delta,
                                'implied_volatility': optionPrice.implied_volatility,
                                'implied_volatility_change': optionPrice.implied_volatility_change,
                                'next_day_open_interest': optionPrice.next_day_open_interest,
                                'open_interest': optionPrice.open_interest,
                                'open_interest_change': optionPrice.open_interest_change,
                                'trades': optionPrice.trades,
                                'volume': optionPrice.volume,
                                'volume_ask': optionPrice.volume_ask,
                                'volume_bid': optionPrice.volume_bid
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
                    # Create the Option object and store into the database
                    option_create = Option(
                        symbol=option_symbol,
                        expiration=parse_date(option_expiration),
                        strike=option_strike,
                        ticker=option_ticker,
                        type=option_type,
                        expiration_type=option_expiration_type,
                    )
                    # Save or else we get an exception where save() prohibited to prevent data loss due to unsaved related object
                    option_create.save()
                    logger.info("Finished creating the option %s" %(option_create))

                    # Verify that the Option created has a primary key that will be stored as a foreign key for Option Price
                    if option_create.pk:
                        option_price_close = option["close"]
                        option_price_close_ask = option["ask"]
                        option_price_close_bid = option["bid"]
                        option_price_delta = option["greeks"]["delta"]
                        option_price_implied_volatility = option["greeks"]["ask_iv"]
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

        quote = get_real_time_quote(ticker=stock_ticker)["quotes"]["quote"]

        if quote['ask'] and quote['bid']:
            request.session['current_ask_price'] = quote['ask']
            request.session['current_bid_price'] = quote['bid']

        context = {
            "stock_ticker": stock_ticker,
            "type": type.lower(),
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
        symbol = symbolAndStrike.split(" ")[0]
        strike = symbolAndStrike.split(" ")[1]
        
        if symbol and len(symbol) > 0:
            logger.info("Able to get the %s and %s to show the visual graphs" %(symbol, strike))
            request.session['symbol'] = symbol  # cache the option_ticker (Ex: 'MSFT200807C00300000')

            # Shows the daily Graph
            logger.info("Making RESTAPI call to Tradier to get the daily timestamps and price")
            daily_timestamps = []
            daily_price = []
            try: 
                response = get_time_and_sales(symbol=symbol, interval="daily")
                if response is None or response['series'] is None:
                    return render(request, 'optionchain/index.html', {"error_message": "No time and sales for this daily %s. Visit an actual brokerage for their option graph." %symbol})
                daily_timestamps, daily_price = get_timestamp_and_price(json_response=response, interval="daily")   
            except Exception as e:
                logger.exception(e)
            logger.info("Got and parsed the daily timestamps and price successfully")

            if len(daily_timestamps) == 0 or len(daily_price) == 0:
                logger.warning("Daily_timestamps or daily_price were parsed successfully, but one of them are empty for symbol: %s" % (symbol))

            weekly_timestamps = []
            weekly_price = []
            # Shows the weekly graph
            # response = __get_time_and_sales(
            #     ticker=stock_ticker, interval="weekly")
            # if response is None:
            #     return render(request, 'optionchain/index.html', {"error_message": "No time and sales for this weekly ticker: " + stock_ticker})
            # weekly_timestamps, weekly_price = __get_timestamp_and_price(
            #     json_response=response, interval="weekly")

            monthly_timestamps = []
            monthly_price = []
            # Shows the monthly graph
            # if expiration_type != 'weeklys':
            #     response = __get_time_and_sales(
            #         ticker=stock_ticker, interval="monthly")
            #     if response is None:
            #         return render(request, 'optionchain/index.html', {"error_message": "No time and sales for this monthly ticker: " + stock_ticker})
            #     monthly_timestamps, monthly_price = __get_timestamp_and_price(
            #         json_response=response, interval="monthly")

            context = {
                'stock_ticker': symbol,
                'strike': strike,
                'daily_timestamps': daily_timestamps,
                'daily_price': daily_price,
                'weekly_timestamps': weekly_timestamps,
                'weekly_price': weekly_price,
                'monthly_timestamps': monthly_timestamps,
                'monthly_price': monthly_price,
            }

            return render(request, 'optionchain/optionVisualGraphs.html', context)
        else:
            return render(request, 'optionchain/index.html', {"error_message": "Unable to plot the graph. Check if the parameters are correct or even the date."})