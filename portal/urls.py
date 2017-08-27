from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login/$', auth_views.login, {'template_name': 'registration/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^password-change/$', views.password_change, name='password_change'),
    url(r'^calendars/$', views.calendars, name='calendars'),
    url(r'^marketing/$', views.marketing, name='marketing'),
    url(r'^programs/$', views.programming, name='programming'),
    url(r'^full-time-resources/$', views.ftresources, name='fulltime_staff_resources'),
    url(r'^staff/$', views.staff, name='staff_directory'),
    url(r'^docs/$', views.devdocs, name='development_documentation'),
    url(r'^staff/(?P<username>[\w.@+-]+)/$', views.profile, name='staff_profile'),
    url(r'^pages/all/$', views.all_pages, name='pages_list'),
    url(r'^pages/new/$', views.new_page, name='new_page'),
    url(r'^posts/new/$', views.new_post, name='new_post'),
    url(r'^posts/edit/([0-9]*)/$', views.post_edit, name='post_edit'),
    url(r'^pages/edit/([0-9]*)/$', views.page_edit, name='page_edit'),
    url(r'^tabs/edit/([0-9]*)/$', views.tab_edit, name='tab_edit'),
    url(r'^posts/delete/([0-9]*)/$', views.post_delete, name='post_delete'),
    url(r'^pages/delete/([0-9]*)/$', views.page_delete, name='page_delete'),
    url(r'^unactivate/([0-9]*)/$', views.make_user_inactive, name='unactivate_user'),
    url(r'^pages/([a-zA-Z0-9-\']*)/$', views.custom_page, name='custom_page'),
    url(r'^notifications/$', views.notifications, name='notifications'),
    url(r'^notif-clear/([0-9]*)/$', views.notif_clear, name='clear_notifs_ajax_only'),
    url(r'^passgen/$', views.password_generator),
    url(r'^json-consumer/$', views.json_consumer, name='json-data-consumer'),
]
