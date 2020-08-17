from datetime import datetime as dt, timedelta, date
from django.utils.dateparse import parse_date
import requests
import json

api_key = ''

def get_option_expirations(stock_ticker):
    if stock_ticker:
        response = requests.get('https://api.tradier.com/v1/markets/options/expirations',
                                params={'symbol': stock_ticker, 'includeAllRoots': 'false', 'strikes': 'false'},
                                headers={'Authorization': 'Bearer ' + api_key, 'Accept': 'application/json'})
        if response.status_code == 401:
            logger.critical("Invalid API Call as there's no API_KEY")
            return render(request, 'optionchain/index.html', {"error_message": "Something wrong with the API call to get option expiration"})
        
        dates = response.json()
        if dates["expirations"] is None:
            logger.error("Unable to find an expiration for %s" %stock_ticker)
        else:
            dates = dates["expirations"]["date"]
            options_expirations_converted = [parse_date(date) for date in dates]
            return options_expirations_converted
    return None


def get_real_time_quote(ticker):
    if ticker:
        response = requests.get('https://api.tradier.com/v1/markets/quotes',
                                params={'symbols': ticker, 'greeks': 'false'},
                                headers={'Authorization': 'Bearer ' + api_key, 'Accept': 'application/json'})
        return response.json()
    return None


def get_option_chain(ticker, expiration):
    if ticker and expiration:
        response = requests.get('https://api.tradier.com/v1/markets/options/chains',
                                params={'symbol': ticker, 'expiration': expiration, 'greeks': 'true'},
                                headers={'Authorization': 'Bearer ' + api_key, 'Accept': 'application/json'})
        return response.json()
    return None


def get_time_and_sales(symbol, interval):
    if symbol and interval:
        start = date.today()
        end = date.today()

        if date.weekday(date.today()) < 5:  # Monday - Friday
            start = str(start) + " 9:30"
            end = str(end) + " 13:00"
        elif date.weekday(date.today()) == 5: # Saturday
            start = str(start - timedelta(days=1))
            end = str(end - timedelta(days=1)) + " 13:00"
        elif date.weekday(date.today()) == 6:  # Sunday
            start = str(start - timedelta(days=2)) + " 09:30"
            end = str(end - timedelta(days=2)) + " 13:00"

        if interval == "daily":
            start = str(start) + " 09:30"
            interval = '1min'
            logger.info("Daily request for %s" %(symbol))
        elif interval == "weekly":
            start = str(start - timedelta(days=7)) + " 09:30"
            interval = '5min'
            logger.info("Weekly request for %s" %(symbol))
        elif interval == 'monthly':
            start = str(start - timedelta(days=31)) + " 09:30"
            interval = '15min'
            logger.info("Monthly request for %s" %(symbol))
        else:  # unsure of passed in interval
            return None

        # Finally make the request
        response = requests.get('https://api.tradier.com/v1/markets/timesales',
                                params={'symbol': symbol, 'interval': interval, 'start': start, 'end': end, 'session_filter': 'open'},
                                headers={'Authorization': 'Bearer ' + api_key, 'Accept': 'application/json'})
        return response.json()
    else:
        return None


def get_timestamp_and_price(json_response, interval):
    timestamps = []
    price = []
    if interval and json_response["series"]["data"]:
        if interval == 'daily' or interval == 'weekly':
            for data in json_response["series"]["data"]:
                date = dt.strptime(data['time'], "%Y-%m-%dT%H:%M:%S")
                date = date.strftime("%-m/%-d/%y %H:%-M")
                timestamps.append(str(date))

        elif interval == 'monthly':
            for data in json_response["series"]["data"]:
                date = dt.strptime(data['time'], "%Y-%m-%dT%H:%M:%S")
                date = date.strftime("%-m/%-d")
                timestamps.append(str(date))

        price = [data['price'] for data in json_response["series"]["data"]]
        return timestamps, price
    else:
        return None, None

def get_list_of_option_strikes(symbol,expiration):
    if symbol:
        response = requests.get('https://api.tradier.com/v1/markets/options/strikes',
            params={'symbol': symbol, 'expiration': str(expiration)},
            headers={'Authorization': 'Bearer ' + api_key, 'Accept': 'application/json'}
        )
        json_response = response.json()
        if response.status_code == 200:
            return json_response
    return None

# def get_lookup_option_symbols(underlying):
#     if underlying:
#         response = requests.get('https://api.tradier.com/v1/markets/options/lookup',
#             params={'underlying': underlying},
#             headers={'Authorization': 'Bearer ' + api_key, 'Accept': 'application/json'}
#         )
#         json_response = response.json()
#         if response.status_code == 200:
#             return json_response
#     return None    