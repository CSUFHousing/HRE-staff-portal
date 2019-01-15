from django.db import models
from django.urls import reverse

from portal.models import Employee

# Create your models here.


class Asset(models.Model):
    assigned_user = models.ForeignKey(to=Employee, verbose_name="Assigned to User", on_delete=models.CASCADE, null=True, blank=True)
    asset_tag = models.PositiveIntegerField(null=True, blank=True)
    model = models.CharField(max_length=60, null=True, blank=True)
    url = models.URLField(null=True, blank=True, verbose_name="URL")

    def __str__(self):
        if hasattr(self, 'computer'):
            return self.computer.__str__()
        if hasattr(self, 'monitor'):
            return self.monitor.__str__()
        if hasattr(self, 'accessory'):
            return self.accessory.__str__()

    def get_absolute_url(self):
        # return '/technology/user/{}'.format(self.assigned_user.user.username)
        return reverse('inventory.views.user_it_equipment', args=[self.assigned_user.user.username])

    # def __str__(self):
    #     s = "{}".format(self.id)
    #     if self.asset_tag and self.assigned_user:
    #         return s+"|{} assigned to {}".format(self.asset_tag, self.assigned_user)
    #     if self.asset_tag:
    #         return s+"|{} assigned to nobody".format(self.asset_tag)
    #     if self.assigned_user:
    #         return s+"|unmarked asset assigned to {}".format(self.assigned_user)
    #     else:
    #         return s+"|unmarked, unassigned asset"


class DisplayPortType(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class AudioPortType(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class OperatingSystem(models.Model):
    name = models.CharField(max_length=50)
    version = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        s = '{}'.format(self.name)
        if self.version:
            s += ' - {}'.format(self.version)
        return s


class Monitor(Asset):
    display_inputs = models.ManyToManyField(to=DisplayPortType)
    audio_inputs = models.ManyToManyField(to=AudioPortType, blank=True)
    has_builtin_speakers = models.BooleanField(default=False)
    USB_ports = models.PositiveSmallIntegerField(default=0)
    in_use = models.BooleanField(default=False)

    def get_connected_computer(self):
        try:
            return self.computer_set.all()[0].__str__() + " via {}".format(self.monitorconnection_set.all()[0].using.name)
        except IndexError:
            return None

    def get_display_inputs(self):
        try:
            l = [i.name for i in self.display_inputs.all()]
            return ", ".join(sorted(l))
        except IndexError:
            return None

    def __str__(self):
        s= ''
        if self.monitor.asset_tag:
            s = '{} - '.format(self.monitor.asset_tag)
        s += '{}'.format(self.monitor.model)
        return s


class Computer(Asset):
    display_outputs = models.ManyToManyField(to=DisplayPortType)
    audio_outputs = models.ManyToManyField(to=AudioPortType, blank=True)
    USB_ports = models.PositiveIntegerField(default=2)
    operating_system = models.ForeignKey(to=OperatingSystem, on_delete=models.PROTECT)
    primary_domain = models.CharField(null=True, max_length=4, blank=True, default="AD", choices=[("AD","AD"), ("ACAD","ACAD")])
    name = models.SlugField(unique=True, null=True, blank=True)
    IP_address = models.CharField(null=True, blank=True, max_length=15)
    connected_monitors = models.ManyToManyField(to=Monitor, through='MonitorConnection')

    def get_absolute_url(self):
        return '/technology/user/lhiggott'

    def get_connected_monitors(self):
        try:
            l = list()
            # l = [m.asset_tag for m in self.connected_monitors.all()]
            for m in self.connected_monitors.all():
                if m.asset_tag:
                    l.append(str(m.asset_tag))
                else:
                    l.append("Untagged monitor")
            return ", ".join(l)
        except IndexError:
            return None

    def save(self, *args, **kwargs):
        self.name = self.name.upper() # capitalize computer name
        super().save(*args, **kwargs)

    def __str__(self):
        return "{}\{}".format(self.primary_domain, self.name)


class MonitorConnection(models.Model):
    monitor = models.ForeignKey(to=Monitor, on_delete=models.CASCADE, unique=True,error_messages={'unique':'That monitor is already in use.'})
    computer = models.ForeignKey(to=Computer, on_delete=models.CASCADE)
    using = models.ForeignKey(to=DisplayPortType, on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "Connected Monitors"
        verbose_name = "Monitor"

    def __str__(self):
        return self.monitor.__str__()

    def save(self, *args, **kwargs):
        self.monitor.in_use = True
        self.monitor.assigned_user = self.computer.assigned_user
        self.monitor.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.monitor.in_use = False
        self.monitor.save()
        super().delete(*args, **kwargs)


class Accessory(Asset):
    type = models.CharField(max_length=20)

    def __str__(self):
        return "{} {}".format(self.type, self.model)

    class Meta:
        verbose_name_plural = "Accesories"


class Ticket(models.Model):
    user = models.ForeignKey(to=Employee, on_delete=models.SET_NULL, null=True, blank=True)
    Asset = models.ForeignKey(to=Asset, on_delete=models.SET_NULL, null=True, blank=True)
    date_opened = models.DateTimeField(auto_now_add=True, editable=False)
    description = models.TextField()

    def __str__(self):
        return "T{} opened by {} on {}".format(self.id, self.user, self.date_opened)


class Note(models.Model):
    ticket = models.ForeignKey(to=Ticket, on_delete=models.SET_NULL, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True, editable=False)
    description = models.TextField()

    def __str__(self):
        return "N{} added to T{} on {}".format(self.id, self.ticket.id, self.date_added)
