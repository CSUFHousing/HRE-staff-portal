from django import template
from django.template.defaultfilters import stringfilter
from django.contrib.auth.models import Group
from portal.models import Page

register = template.Library()

@register.filter(name='in_group')
def in_group(user, group_name):
    group =  Group.objects.get(name=group_name)
    return group in user.groups.all()

@register.filter(name='slicechars')
def slicechars(value, arg):
    length = int(arg)
    value = str(value)
    retval = value[0:length]
    return retval
