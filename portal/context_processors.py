from . import urls
from .models import Page, Employee, Notification, FormData
from django.contrib.auth.models import User

import inspect
from datetime import date, timedelta
# context processors - these make additional variables available to templates

# basically, this makes 'cpages' a variable that can be referenced in any template
# so that the navbar can load the links in cpages

def custom_pages(request):
    cpages = Page.objects.all().filter(tabbedpagecontent=None).order_by('created_date')
    return {'cpages': cpages}

def urlconf(request):
    urlconf = inspect.getsource(urls)
    return {'urlconf': urlconf}

def notifs(request):
    d = {}
    if request.user.is_authenticated:
        emp = request.user.employee
        notifs = Notification.objects.filter(to=emp).order_by('-sent_date')
        d['notifs'] = notifs
        unreads = notifs.filter(unread=True)
        d['unreads'] = unreads
    return d

def rcr_stats(request):
    if not request.user.is_authenticated:
        return {}
    d = {}
    RCRs = FormData.objects.filter(formID=17)
    userRCRs = RCRs.filter(staff=request.user.employee)
    last7 = []
    useractivity = []
    allactivity = []
    allentries = 0
    today = date.today()
    for i in range(0,7):
        last7.append(today - timedelta(i))
        rdate = today - timedelta(i)
        try:
            useractivity.append(userRCRs.get(date=rdate))
        except FormData.DoesNotExist:
            useractivity.append(0)
        these = RCRs.filter(date=rdate)
        qty = 0
        for entry in these:
            qty = qty + entry.qty
        allactivity.append(qty)
    d['rcrs_all_activity'] = allactivity[::-1]
    allqty = 0
    for entry in RCRs:
        allqty = allqty + entry.qty
    d['rcrs_all_qty'] = allqty
    d['last7'] = last7[::-1]
    d['rcrs_user_activity'] = useractivity[::-1]
    todaytop5 = RCRs.filter(date=today).order_by('-qty')[0:5]
    d['rcrs_top5'] = todaytop5
    try:
        latest = RCRs.latest('last_saved')
        d['rcrs_latest'] = latest
    except FormData.DoesNotExist:
        pass
    start = today - timedelta(7)
    try:
        d['rcrs_user_today'] = userRCRs.get(date=today).qty
    except FormData.DoesNotExist:
        d['rcrs_user_today'] = 0
    qty = 0
    userRCRs = RCRs.filter(staff=request.user.employee)
    for entry in userRCRs:
        qty = qty + entry.qty
    d['rcrs_user_total'] = qty
    try:
        last = RCRs.filter(staff=request.user.employee).latest('last_saved')
        d['rcrs_user_last'] = last.last_saved
    except FormData.DoesNotExist:
        pass
    return d
