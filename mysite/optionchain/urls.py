from django.urls import path
from . import views

app_name = "optionchain"
urlpatterns = [
    # ex: /optionchain/
    path('', views.index, name='index'),
    # ex: /optionchain/stockName
    path('stockName', views.stockName, name='stockName'),
    # ex: /optionchain/stockName/callOptionTable
    path('callOptionTable', views.callOptionTable, name='callOptionTable'),
    # ex: /optionchain/stockName/putOptionTable
    # path('putOptionTable', views.putOptionTable, name='putOptionTable')
]