from django.shortcuts import render, get_object_or_404

from .models import Asset, Employee

# Create your views here.
def my_it_equipment(request):
    assets = Asset.objects.filter(assigned_user=request.user.employee)
    return render(request, 'inventory/equipment.html', {'assets': assets, 'user':request.user})

def user_it_equipment(request, username):
    employee = get_object_or_404(Employee, user__username=username)
    assets = Asset.objects.filter(assigned_user=employee)
    return render(request, 'inventory/equipment.html', {'assets': assets, 'user': employee.user})

def new_ticket(request, assetid):
    pass

def ticket_history(request, ticketid):
    pass
