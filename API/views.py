from django.http import Http404
from django.contrib.auth.models import User

from rest_framework import status, mixins, generics, permissions, renderers, viewsets
from rest_framework.decorators import api_view, detail_route
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from portal.models import Employee, Page, Post, TabbedPageContent, Notification, FormData
from API.serializers import EmployeeSerializer, PageSerializer, PostSerializer, FDSerializer, NotifSerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'employees': reverse('employee-list', request=request, format=format),
    })

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    #permission_classes = (permissions.IsAuthenticated,)

class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all().filter(tabbedpagecontent__isnull=True)
    serializer_class = PageSerializer
    #permission_classes = (permissions.IsAuthenticated,)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    #permission_classes = (permissions.IsAuthenticated,)

class NotifViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotifSerializer
    #permission_classes = (permissions.IsAuthenticated,)

class FormDataViewSet(viewsets.ModelViewSet):
    queryset = FormData.objects.all()
    serializer_class = FDSerializer
    #permission_classes = (permissions.IsAdminUser,)

class TabbedContentViewSet(viewsets.ModelViewSet):
    queryset = TabbedPageContent.objects.all()
    serializer_class = PageSerializer
    #permission_classes = (permissions.IsAuthenticated,)
