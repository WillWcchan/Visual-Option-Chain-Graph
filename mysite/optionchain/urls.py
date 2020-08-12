from django.urls import path
from . import views

app_name = "optionchain"
urlpatterns = [
    # ex: /optionchain/
    path('', views.index, name='index'),
    # ex: /optionchain/stock_ticker
    path('stock_ticker', views.stock_ticker, name='stock_ticker'),
    # ex: /optionchain/stock_ticker/optionChain
    path('optionDate', views.optionDate, name='optionChain'),
    # ex: /optionchain/optionsTable
    path('optionsTable', views.optionsTable, name='callOptionGraph'),
    # ex: /optionchain/callOptionVisualGraphs
    path('callOptionVisualGraphs', views.callOptionVisualGraphs, name='callOptionVisualGraphs'),
]