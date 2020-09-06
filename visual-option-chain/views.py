from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail, BadHeaderError
from django.utils.dateparse import parse_date
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.debug import sensitive_variables
from django_redis import get_redis_connection
from .models import Option, OptionPrice
from .forms import ContactForm
from .tasks import send_email_task
from .tradier_api import *
import requests
import json
import sys
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('views.py')

# Source: https://testdriven.io/blog/django-caching/x
CACHE_TTL = 10080 # Cache time to live for a week (60 * 24 * 7)
CACHE_EXPIRATION_DATE = 60 * 5  # Cache time to live for 5 minutes

def index(request):
    return render(request, 'index.html')

# Source: https://learndjango.com/tutorials/django-email-contact-form
def contactView(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_Email']
            message = form.cleaned_data['message']
            try:
                # send_mail(subject, message, from_email, ['willwcchan@gmail.com'])
                send_email_task.delay(subject=subject, from_email=from_email, message=message, recipient_list=['willwcchan@gmail.com'])
                logger.info("Sent email with subject: %s and from email: %s" %(subject, from_email))
            except BadHeaderError as e:
                logger.exception(e)
                return HttpResponse('Invalid header found.')
            return render(request, 'index.html', {"info_message": "Email has been sent!"})
    return render(request, 'email.html', {'form': form})

# Source: https://docs.djangoproject.com/en/1.11/howto/error-reporting/
@sensitive_variables('api_key')
def stock_ticker(request):
    if api_key is None or api_key == "":
       logger.critical("No API KEY provided")

    if request.method == 'GET':
        stock_ticker = request.GET.get('stock_ticker')
        logger.info("Stock ticker entered: %s" %stock_ticker)
        if not stock_ticker:
            return render(request, 'index.html', {"info_message": "You've entered an empty ticker Try again."})
        else:
            if stock_ticker.isalpha():
                stock_ticker = stock_ticker.upper().strip()
                saved = cache.set("stock_ticker", stock_ticker, timeout=CACHE_TTL)
                if saved:
                    logger.info("Successfully saved %s in redis cache" % stock_ticker)        
            else:
                return render(request, 'index.html', {"info_message": "You've entered a value with a number. Please try again with a real ticker"})

        try:
            expiration_list = cache.get(stock_ticker + "expiration_list")
            if not expiration_list:
                expiration_list = get_option_expirations(stock_ticker=stock_ticker)
                saved = cache.set(stock_ticker + "expiration_list", expiration_list, timeout=CACHE_TTL)
                if saved:
                    logger.info("Successfully saved %s\'s expiration list in redis cache" % stock_ticker)

            logger.info("%s\s expiration_list: %s" %(stock_ticker, expiration_list))
            if expiration_list and len(expiration_list) > 0:
                return render(request, 'optionType.html', {'stock_ticker': stock_ticker})
            else:
                return render(request, 'index.html', {"info_message": "Unable to find expirations %s. Try another ticker" %stock_ticker})
        except Exception as e:
            logger.exception(e)
            return render(request, 'index.html', {"info_message": e})


def option_type(request):
    if request.method == 'GET':
        option_type = request.GET.get("option_type", None)
        logger.info("option type %s was found and saved in cache" % option_type)
        saved = cache.set('option_type', option_type, timeout=CACHE_EXPIRATION_DATE)
        if saved:
            logger.info("Saved option_type %s in redis" % option_type)
            
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
                return render(request, 'optionDate.html', context)
            else:
                return render(request, 'index.html', {"info_message": "No options expirations found for this ticker. Try another ticker"})


def option_table(request):
    if request.method == 'GET':
        stock_ticker = cache.get("stock_ticker")
        option_type = cache.get('option_type')

        try:
            expiration = request.GET.get("expiration_date", "")
            expiration_date = parse_date(expiration)
            logger.info("Able to parse in the expiration date %s" %expiration)
        except ValueError as e:
            logger.exception(e)
            return HttpResponse("Incorrect expiration date format: " + expiration)

        if stock_ticker and expiration_date:
            logger.info("Check if we have an option stored in our database for %s and %s" % (stock_ticker, expiration_date))
            option_list = Option.objects.all().filter(ticker=stock_ticker).filter(expiration=expiration_date).filter(option_type=option_type)        
            list_of_optionChain = []
            if option_list.count() > 0:
                for option in option_list:
                    option_price = OptionPrice.objects.filter(option=option).first()        
                    if option_price:
                        list_of_optionChain.append({
                            'symbol': option.symbol,
                            'expiration': str(option.expiration),
                            'strike': option.strike,
                            'ticker': option.ticker,
                            'option_type': option.option_type,
                            'expiration_type': option.expiration_type,
                            'close': option_price.close,
                            'close_ask': option_price.close_ask,
                            'close_bid': option_price.close_bid,
                            'delta': option_price.delta,
                            'implied_volatility': option_price.implied_volatility,
                            'open_interest': option_price.open_interest,
                            'trades': option_price.trades,
                            'volume': option_price.volume,
                            'volume_ask': option_price.volume_ask,
                            'volume_bid': option_price.volume_bid
                            })
                    else:
                        return HttpResponse("No option price for this option")
            else:
                logger.info("Option does not exist in our database. Will make a REST API call to Tradier with %s and %s" %(stock_ticker, expiration_date))
                response = get_option_chain(ticker=stock_ticker, expiration=expiration)
                logger.info("Recieved option chain from Tradier API")
                list_of_optionChain = response["options"]["option"]

                for option in list_of_optionChain:
                    logger.info("Creating the option and storing into the database")
                    option_create = Option(
                        symbol=option["symbol"],
                        expiration=parse_date(option["expiration_date"]),
                        strike=option["strike"],
                        ticker=option["underlying"],
                        option_type=option["option_type"],
                        expiration_type=option["expiration_type"],
                    )
                    option_create.save()
                    logger.info("Finished creating the option %s" %(option_create))

                    if option_create.pk:
                        logger.info("Creating the optionPrice for the recently created option to store into the database")
                        try:
                            option_price_delta = option["greeks"]["delta"]
                            option_price_implied_volatility = option["greeks"]["ask_iv"]
                        except KeyError as e:
                            logger.exception("greek is not available for %s, possibly new stock" %stock_ticker)
                            option_price_delta = 0
                            option_price_implied_volatility = 0
                            
                        OptionPrice.objects.create(
                            option=option_create,
                            close=option["close"],
                            close_ask=option["ask"],
                            close_bid=option["bid"],
                            delta=option_price_delta,
                            implied_volatility=option_price_implied_volatility,
                            open_interest=option["open_interest"],
                            volume=option["volume"],
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
            "option_expiration": expiration_date,
            "list_of_optionChain": list_of_optionChain,
            "current_ask_price": quote['ask'],
            "current_bid_price": quote['bid']
        }

        if stock_ticker and expiration_date and list_of_optionChain:
            # logger.info("Passed in context to optionTable.html %s" %context)
            return render(request, 'optionTable.html', context=context)

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
                    return render(request, 'index.html', {"info_message": "No time and sales for this daily %s. Visit an actual brokerage for their option graph." %symbol})
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

            return render(request, 'optionVisualGraphs.html', context)
        else:
            return render(request, 'index.html', {"info_message": "Unable to plot the graph. Check if the parameters are correct or even the date."})

def error_404_view(request, exception):
    return render(request, '404.html')

def error_500_view(request):
    return render(request, '500.html')

def tearDown(self):
    get_redis_connection("default").flushall()