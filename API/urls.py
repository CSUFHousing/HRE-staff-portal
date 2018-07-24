from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from . import slack
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'employees', views.EmployeeViewSet)
router.register(r'pages', views.PageViewSet)
router.register(r'post', views.PostViewSet)
router.register(r'tabcontent', views.TabbedContentViewSet)
router.register(r'notifs', views.NotifViewSet)
router.register(r'formdata', views.FormDataViewSet)

schema_view = get_schema_view(title='Pastebin API')

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^schema/$', schema_view),
    url(r'^slack/$', )
    url(r'^', include(router.urls)),
]
