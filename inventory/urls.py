from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.my_it_equipment, name='my_it_equipment'),
    url(r'^user/(?P<username>[\w.@+-]+)/$', views.user_it_equipment, name='user_it_equipment')
]
