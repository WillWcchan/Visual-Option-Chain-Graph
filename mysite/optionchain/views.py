from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import Option, OptionPrice

# Create your views here.
def index(request):
    option_list = Option.objects.all()
    context = { 'option_list': option_list}
    return render(request, 'optionchain/index.html',context)

def stockName(request):
    if request.method == 'GET':
        stockTickerOrName = request.GET.get('stockTickerOrName', 'none').upper()
        try:
            option_ticker = Option.objects.get(ticker__iexact=stockTickerOrName)
            option_stock_name = Option.objects.get(stockName__iexact=stockTickerOrName)
            if option_ticker != None and option_stock_name != None:
                return render(request, 'optionchain/stockTable.html', {'option': option_stock_name})
        except Option.DoesNotExist:
            return render(request, 'optionchain/index.html', {"error_message": "Unable to find stock. Please try again."})
    return render(request, 'optionchain/index.html', {"error_message": "Unable to handle request to find stock. Please try again."})

def callOptionTable(request):
    if request.method == 'GET':
        optionStockName = request.GET.get("call","")
        if optionStockName is not None:
           return render(request, 'optionchain/callOptionTable.html', {'option_stockName':optionStockName})
    return HttpResponse("Call option Table")

def putOptionTable(request):
    return HttpResponse("Put option Table")    
