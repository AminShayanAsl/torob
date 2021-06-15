from django.conf.urls import url
from . import views

app_name = 'app'

urlpatterns = [
    url('^mobiles_list/$', views.mobiles_list, name='mobiles_list'),
    url('^mobiles_list_download/$', views.mobiles_list_download, name='mobiles_list_download'),
    url('^merchants_list/$', views.merchants_list, name='merchants_list'),
    url('^price_list/$', views.price_list, name='price_list'),
    url('^merchants_list_download/$', views.merchants_list_download, name='merchants_list_download'),
]
