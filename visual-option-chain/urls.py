"""visual-option-chain URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import *

urlpatterns = [
    # ex /admin
    url(r'^admin', admin.site.urls),
    # ex /contact
    url(r'^contact', contactView, name="contact"),
    # ex /stockTicker/?stock_ticker=msft
    url(r'^stockTicker/$', stock_ticker, name = 'stock_ticker'),
    # ex /stockTicker/optionType/?option_type=call
    url(r'^stockTicker/optionType/$', option_type, name = 'optionType'),
    # ex /stockTicker/optionType/optionDate/?expiration_date=2020-08-14
    url(r'^stockTicker/optionType/optionDate/$', option_table, name = 'optionTable'),
    # ex /stockTicker/optionType/optionDate/optionVisualGraphs/?symbol=MSFT200814C00205000+205.0
    url(r'^stockTicker/optionType/optionDate/optionVisualGraphs/$', option_visual_graphs, name = 'optionVisualGraphs'),
    
    # ex localhost:8000 or home page
    url(r'^', index, name='index'),
]

urlpatterns += staticfiles_urlpatterns()

handler404 = 'visual-option-chain.views.error_404_view'
handler500 = 'visual-option-chain.views.error_500_view'