from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import Option, OptionPrice
from django.utils.dateparse import parse_date
import requests
import json

# Create your views here.
def index(request):
    option_list = Option.objects.all()
    context = { 'option_list': option_list}
    return render(request, 'optionchain/index.html',context)

def stockName(request):
    if request.method == 'GET':
        stockTicker = request.GET.get('stockTicker', 'none').upper()
        try:
            option_ticker = Option.objects.get(ticker=stockTicker)
            if option_ticker != None:
                return render(request, 'optionchain/stockTable.html', {'option': option_ticker})
        except Option.DoesNotExist:
            return render(request, 'optionchain/index.html', {"error_message": "Unable to find stock. Please try again."})
    return render(request, 'optionchain/index.html', {"error_message": "Unable to handle request to find stock. Please try again."})

def callOptionTable(request):
    if request.method == 'GET':
        optionTicker = request.GET.get("call","")
        # Source: https://simpleisbetterthancomplex.com/tutorial/2018/02/03/how-to-use-restful-apis-with-django.html
        if optionTicker is not None:
            response = requests.get("https://api-v2.intrinio.com/options/MSFT?api_key=")
            option_list = json.loads(response.text)['options']

            # Create the Option Model from the JSON Response
            for option in option_list:
                Option.objects.create(
                    ticker    = option['ticker'],
                    expiration = parse_date(option['expiration']),
                    strike = float(option['strike']),
                    type = option['type'])
            
            return render(request, 'optionchain/callOptionTable.html',
             {'option_stockName':optionTicker,
              'option_list': Option.objects.filter(ticker=optionTicker,type='CALL')})
    return HttpResponse("Call option Table")

def putOptionTable(request):
    return HttpResponse("Put option Table")    
