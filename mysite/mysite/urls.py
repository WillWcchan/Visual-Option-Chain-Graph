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

urlpatterns = [
    # ex /optionchain/
    url(r'^optionchain/', include('optionchain.urls')),
    # ex /optionchain/getStock/?stock_ticker=msft
    url(r'^optionchain/getStock/$', v.stock_ticker, name = 'stock_ticker'),
    # ex /optionchain/getStock/optionType/?option_type=CALL
    url(r'^optionchain/getStock/optionType/$', v.optionType, name = 'optionType'),
    # ex /optionchain/getStock/optionType/optionDate/?expiration_date=2020-08-14
    url(r'^optionchain/getStock/optionType/optionDate/$', v.optionTable, name = 'optionTable'),
    # ex /optionchain/getStock/optionType/optionDate/optionVisualGraphs/?symbol=MSFT200814C00205000+205.0
    url(r'^optionchain/getStock/optionType/optionDate/optionVisualGraphs/$', v.optionVisualGraphs, name = 'optionVisualGraphs'),
    url(r'^admin/', admin.site.urls),
]
