from django.urls import path
from . import views

app_name = "optionchain"
urlpatterns = [
    # ex: /optionchain/
    path('', views.index, name='index'),
    # ex: /optionchain/stockName
    path('stockName', views.stockName, name='stockName')
]