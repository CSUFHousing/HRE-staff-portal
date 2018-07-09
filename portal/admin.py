from django.contrib import admin
from django.shortcuts import redirect
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group

from .models import Post, Employee, Page, TabbedPageContent, Notification, FormData

# inline admin descriptor for Employee model
# allows for storing contact information related to django auth users
class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'employee'
    fieldsets = (
    (_('Employee Details'), {'fields': ('department', 'title', 'supervisor', 'phone' )}),
    (_('For Live-On Staff'), {'fields': ('building', 'room')}),
    (_('Personal Details'), {'fields': ('photo', 'birthday', 'pronouns')}),
    )

class PageOnlyFilter(admin.SimpleListFilter):
    title = 'Content Type'
    parameter_name = 'type'
    def lookups(self, request, model_admin):
        return (
            ('pages', 'Pages Only'),
            ('tabs', 'Tab Content Only'),
            ('all', 'All'),
        )
    def queryset(self, request, queryset):
        if self.value() == 'tabs':
            return queryset.filter(tabbedpagecontent__isnull=False)
        elif self.value() == 'pages' or self.value() == None:
            return queryset.filter(tabbedpagecontent__isnull=True)

admin.site.unregister(User)

def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active='False')
make_inactive.short_description = "Set selected as inactive"

def assign_to_RAs(modeladmin, request, queryset):
    RA = Group.objects.get(name='Resident Advisors')
    for obj in queryset:
        obj.groups.add(RA)
        obj.save()
assign_to_RAs.short_description = "Assign selected as Resident Advisors"

def assign_to_OAs(modeladmin, request, queryset):
    OA = Group.objects.get(name='Office Assistants')
    for obj in queryset:
        obj.groups.add(OA)
        obj.save()
assign_to_OAs.short_description = "Assign selected as Office Assistants"

# overrides for the standard Django user management form in the admin interface
# prevents setting users as superuser or manually editing permissions per-user

def Department(obj):
    return '{}'.format(obj.employee.get_department_display())

def Title(obj):
    return '{}'.format(obj.employee.title)

class UserAdmin(BaseUserAdmin):
    list_display = ['first_name', 'last_name', Title, 'email', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'employee__department', 'groups']
    fieldsets = (
    (None, {'fields': ('username', 'password')}),
    (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
    (_('Permissions'), {'fields': ('is_active', 'is_staff', 'groups',)}),
    (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    # inline Employee Form relates a django.contrib.auth User entry to an Employee entry
    # to store additional data like contact info, room assignment for live-on staff, etc.
    inlines = (EmployeeInline, )
    actions = [make_inactive, assign_to_RAs, assign_to_OAs]

class PostAdmin(admin.ModelAdmin):
    fields = ('title', 'content', 'header_color', 'last_published_by', 'admin_only')
    list_display = ['title', 'last_published_by', 'published_date', 'admin_only']
    list_filter = ['last_published_by', 'published_date', 'admin_only']
    search_fields = ['title', 'content']

class PageAdmin(admin.ModelAdmin):
    fields = ('title', 'customurl', 'content', 'icon', 'admin_only')
    search_fields = ['title', 'customurl', 'content']
    list_display = ['title', 'published_date', 'customurl', 'admin_only']
    list_filter = [ 'published_date', 'admin_only', PageOnlyFilter]

class TabAdmin(admin.ModelAdmin):
    fields = ('title', 'customurl', 'content', 'icon', 'admin_only', 'parent')
    list_display = ['parent', 'title', 'admin_only']
    list_filter = ['parent', 'admin_only']
    list_display_links = ['title']
    search_fields = ['title', 'customurl', 'content']

class NotifAdmin(admin.ModelAdmin):
    fields = ['to', 'message', 'context', 'unread']
    list_display = ['to', 'context', 'unread', 'sent_date']
    list_filter = ['sent_date']
    list_display_links = ['to', 'context', 'unread', 'sent_date']
    search_fields = ['context', 'message', 'sent_date']

class FormDataAdmin(admin.ModelAdmin):
    list_display = ['formName', 'staff', 'date', 'qty', 'formID']
    search_fields = ['formName', 'staff__user__first_name', 'staff__user__last_name']
    list_filter = ['formName', 'staff', 'date']


# declare admin stuff here
admin.site.disable_action('delete_selected')
admin.site.site_title = 'HRE'
admin.site.index_title = 'Portal Management'
admin.site.site_header = 'HRE Staff Portal Management'
admin.site.register(Post, PostAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(TabbedPageContent, TabAdmin)
admin.site.register(Notification, NotifAdmin)
admin.site.register(FormData, FormDataAdmin)
