"""mysite URL Configuration

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
from optionchain import views as v
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    # ex /optionchain/
    url(r'^optionchain/', include('optionchain.urls')),
    # ex /optionchain/stockTicker/?stock_ticker=msft
    url(r'^optionchain/stockTicker/$', v.stock_ticker, name = 'stock_ticker'),
    # ex /optionchain/stockTicker/optionType/?option_type=CALL
    url(r'^optionchain/stockTicker/optionType/$', v.option_type, name = 'optionType'),
    # ex /optionchain/stockTicker/optionType/optionDate/?expiration_date=2020-08-14
    url(r'^optionchain/stockTicker/optionType/optionDate/$', v.option_table, name = 'optionTable'),
    # ex /optionchain/stockTicker/optionType/optionDate/optionVisualGraphs/?symbol=MSFT200814C00205000+205.0
    url(r'^optionchain/stockTicker/optionType/optionDate/optionVisualGraphs/$', v.option_visual_graphs, name = 'optionVisualGraphs'),
    url(r'^admin/', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()