from django.conf.urls import url
from . import views
app_name = 'tezos_ifttt_interface'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ajax/ifttt/launch/$', views.ifttt_launch),
]