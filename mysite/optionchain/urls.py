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
    # ex: /optionchain/optionTable
    path('optionTable', views.optionTable, name='callOptionGraph'),
    # ex: /optionchain/optionVisualGraphs
    path('optionVisualGraphs', views.optionVisualGraphs, name='optionVisualGraphs'),
]
