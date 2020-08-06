from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import Option, OptionPrice
from django.utils.dateparse import parse_date
from datetime import date, datetime
import requests
import json
import sys

# Create your views here.
def index(request):
    option_list = Option.objects.all()
    context = { 'option_list': option_list}
    return render(request, 'optionchain/index.html',context)

def stockName(request):
    if request.method == 'GET':
        stockTicker = request.GET.get('stockTicker', 'none').upper().strip()
        try:
            option = Option.objects.filter(ticker=stockTicker)[0] 
            if option is not None:
                return render(request, 'optionchain/stockTable.html', {'option': option})
        except Option.DoesNotExist:
            return render(request, 'optionchain/index.html', {"error_message": "Unable to find stock. Please try again."})
    return render(request, 'optionchain/index.html', {"error_message": "Unable to handle request to find stock. Please try again."})

def callOptionTable(request):
    if request.method == 'GET':
        optionTicker = request.GET.get("call","")
        # Source: https://simpleisbetterthancomplex.com/tutorial/2018/02/03/how-to-use-restful-apis-with-django.html
        if optionTicker is not None:
            response = requests.get("https://api-v2.intrinio.com/options/" + optionTicker + "?api_key=")
            optionsData = json.loads(response.text)['options']

            option_list_date = []

            # Create the Option Model from the JSON Response
            for option in optionsData:
                expiration = parse_date(option['expiration'])
                strike = float(option['strike'])
                ticker = option['ticker']
                type = option['type'].upper()
                
                if type == 'CALL':
                    op = Option(
                        ticker = ticker,
                        expiration = expiration,
                        strike = strike,
                        type = type)
                    op.save()
                    
                    # At the same time add the expiration/dates into option_list_date
                    option_list_date.append(expiration)                   

            # remove any duplicate dates
            option_set_date = set(option_list_date)
            
            context = {
                'option_ticker':optionTicker,
                'option_set_date': option_set_date
            }

            if len(option_set_date) > 0:
                return render(request, 'optionchain/callOptionTable.html',context)
            else:
                return HttpResponse("No option found.")
    return HttpResponse("Call option Table")

def putOptionTable(request):
    return HttpResponse("Put option Table")    
