from django.contrib.auth.models import User

from rest_framework import serializers

from portal.models import Employee, Page, Post, FormData, Notification

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Employee
        fields = ('__all__')
    def create(self, validated_data): # to-do
        user_data = validated_data.pop('user')
        newuser = User.objects.create(**user_data)
        newemp = Employee.objects.create(user=newuser, **validated_data)
        return newemp

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('__all__')

class PostSerializer(serializers.ModelSerializer):
    #last_published_by = serializers.HyperlinkedRelatedField(source='last_published_by.user.username')
    class Meta:
        model = Post
        fields = ('__all__')

class FDSerializer(serializers.ModelSerializer):
    #staff = serializers.HyperlinkedRelatedField(source='staff')
    class Meta:
        model = FormData
        fields = ('__all__')

class NotifSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('__all__')
