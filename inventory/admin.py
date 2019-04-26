from django.contrib import admin
from django.db.models import Q
from portal.models import notify_devs

from .models import Asset, Accessory, AudioPortType, Computer, DisplayPortType, MobileDevice, AssetModel, Monitor, MonitorConnection, OperatingSystem, Note, Ticket

# Register your models here.

for item in [Accessory, AudioPortType, DisplayPortType, MobileDevice, AssetModel, OperatingSystem, Note, Ticket]:
    admin.site.register(item)


class MonitorInline(admin.TabularInline):
    model = Computer.connected_monitors.through
    extra = 0
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            compid = [int(s) for s in str(request.path).split('/') if s.isdigit()][0] or None
        except IndexError:
            compid = None
        return qs.filter(Q(monitor__in_use=False)|Q(computer__id=compid))

@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Assignment Information",
            {"fields": (('assigned_user', 'asset_tag'),)}
        ),
        ("Network Information",
            {"fields": (('IP_address', 'primary_domain'),)}
        ),
        ("System Information",
            {"fields": ('name', ('model', 'operating_system','USB_ports'),('display_outputs', 'audio_outputs'), 'url')}
        ),
    )
    list_display = ('assigned_user', 'name','IP_address', 'operating_system')
    list_display_links = ('name', 'IP_address')
    list_filter = ('operating_system__name', 'assigned_user__department')
    ordering = ('assigned_user',)
    radio_fields = {'primary_domain': admin.HORIZONTAL}
    save_as = True
    search_fields = ('assigned_user__user__first_name','assigned_user__user__last_name', 'name', 'IP_address')
    inlines = (MonitorInline,)

@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Assignment Information",
            {"fields": (('assigned_user', 'asset_tag'),)}
        ),
        ("Device Information",
            {"fields": (
                ('model'),
                ('display_inputs', 'audio_inputs'),
                ('has_builtin_speakers', 'USB_ports')
            )}
        ),
        )
    empty_value_display = '-- not assigned --'
    list_display = ('model', 'assigned_user', 'assigned_to_computer')
    def assigned_to_computer(self, obj):
        try:
            return obj.computer_set.all()[0]
        except IndexError:
            return None

admin.site.empty_value_display = '-- not set --'
