from django.contrib import messages
from django.db.models.query import QuerySet

from .models import FormData, Employee
from .models import notify_devs

#from .rcrstorage import send_to_server

from datetime import date
from dateutil.parser import parse as timeparse

def interpret(json):
    if type(json) != dict:
        raise TypeError('Expecting a dictionary representing a valid JSON object.')
    else:
        # let's do it
        form_internals = json['Form']
        form_entry = json['Entry']
        formId = form_internals['Id']
        # formID has ID 17 for RCRs
        formTimeStamp = form_entry['DateSubmitted']
        today = date.today()
        formDate = timeparse(formTimeStamp)
        # FD object holds a queryset of the formData objects on the date of the form, of that form id
        FD = FormData.objects.filter(date=formDate).filter(formID=formId)
        # RCR processing first
        if formId == '17': # RCRs will also filter by staff name
            #send_to_server(json)
            # Uncomment the next line if you want a copy of the RCR data sent to dev accounts. NOT RECOMMENDED FOR PRODUCTION
            #notify_devs('info', 'RCR Form data recorded. Type is: "{}" and its data is: "{}".'.format(form_internals['Name'], str(json)))
            fname = json['StaffName']['First']
            lname = json['StaffName']['Last']
            try:
                staff = Employee.objects.filter(user__first_name=fname).get(user__last_name=lname)
            except Employee.DoesNotExist:
                staff = Employee.objects.get(user__username='admin') # anonymous RCR, assign it to the django admin superuser account
            try:
                FD = FD.get(staff=staff)
                FD.qty += 1
                FD.save()
            except FormData.DoesNotExist:
                new = FormData.objects.create(formID=int(formId), formName=form_internals['Name'], date=date.today(), qty=1)
                new.staff = staff
                new.save()
        else:
            notify_devs('warning', 'Form data recorded: Type is: "{}" and its data is: "{}".'.format(form_internals['Name'], str(json)))
            try:
                data = FD[0]
                data.qty = data.qty + 1
                data.save()
            except IndexError:
                new = FormData.objects.create(formID=int(formId), formName=form_internals['Name'], date=date.today(), qty=1)
                new.save()
