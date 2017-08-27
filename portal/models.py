from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import validate_slug

from PIL import Image

# this file defines the custom tables inside the portal's database
# including homepage Posts and custom Pages,
# and a custom Employees table that extends the django built-in Users authentication table

# INSTRUCTIONS FOR UPDATING THIS FILE
    # if you add or modify any lines that start with: <name> = models.<field>
        # even if you modify the arguments like <field>(max_length=100) - follow these instructions
    # you need to perform django migrations. Run these commands in a bash console in the same directory as manage.py:
        # python manage.py makemigrations
        # python manage.py migrate
    # you might also need to reload the web app after doing this. (or restart the dev server)
    # if you change the <name> of any model fields, you will have to update any templates in templates/portal
    # because any template tags that reference that model will be broken.

    # if you modify the choice lists - you're good. Just save the file and refresh any page you're on.

    # if you add or create any class methods (starting wtih def <name>: ), you're probably good.
    # you may need to reload the web app but you don't need to run migrations.

    # BEFORE you change ANYTHING in this file, please read the django model documentation

# these are choice lists. Right-side is human readable (what gets loaded in a drop-down list)
# left-side is the value stored in the database.
BUILDING_CHOICES = (
    ('', ''),
    ('Acacia','Acacia'),
    ('Birch','Birch'),
    ('Cypress','Cypress'),
    ('Fig','Fig'),
    ('Elm','Elm'),
    ('Holly','Holly'),
    ('Juniper','Juniper'),
    ('Manzanita','Manzanita'),
    ('Oak','Oak'),
    ('Pine','Pine'),
    ('Sycamore','Sycamore'),
    ('Valencia','Valencia'),
    ('Willow','Willow'),
    )
DEPARTMENT_CHOICES = (
    ('ACS', 'Admin and Conference Services'),
    ('RE', 'Residential Engagement'),
    ('FO', 'Facilities Operations'),
    ('RSA', 'Resident Student Association'),
    ('NRHH', 'National Residence Hall Honorary'),
)

COLOR_CHOICES = (('purple', 'purple'), ('blue','blue'), ('green', 'green'), ('orange','orange'), ('red', 'red'), ('rose', 'rose'))
STATUS_CHOICES = [('default', 'default'), ('primary', 'primary'), ('info', 'info'), ('success', 'success'), ('warning', 'warning'), ('danger', 'danger'), ('rose', 'rose')]
PRONOUN_CHOICES = [('M', 'He/Him/His'), ('F', 'She/Her/Hers'), ('T', 'They/Them/Theirs'), ('', '')]
TABBED_PAGE_CHOICES = [('P', 'Programming'), ('M', 'Marketing'), ('C', 'Calendars'), ('F', 'Full-Time Staff Resources')]

def notify_devs(context, message):
    devs = Employee.objects.filter(user__is_superuser=True)
    for d in devs:
        d.notify(context, message)

def supervisor_choices():
    return User.objects.all().filter(is_staff=True)

def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
        # this OneToOneField relationship relates an Employee to a built-in User,
        # which allows us to store more information about Users
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'user__is_staff':True})
    department = models.CharField(max_length=100, blank=True, choices=DEPARTMENT_CHOICES)
    title = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True, help_text=('Use a 4-digit extension or full phone number. It\'ll be formatted automatically.'))
    building = models.CharField(max_length=10, blank=True, choices=BUILDING_CHOICES, help_text=('For live-on staff only.'))
    room = models.CharField(max_length=3, blank=True)
    birthday = models.DateField(blank=True, null=True, auto_now=False, auto_now_add=False, help_text=("The database requires you enter a year, but don't worry - it isn't shown in the directory :)"))
    photo = models.ImageField(upload_to=user_directory_path, blank=True)
    bio = models.TextField(blank=True)
    pronouns = models.CharField(max_length=10, blank=True, choices=PRONOUN_CHOICES)
    last_password_change = models.DateField(blank=True, null=True, auto_now_add=False)
    def get_initials(self):
        first = self.user.first_name[0:1]
        last = self.user.last_name[0:1]
        return str(first+last)
    def __str__(self):
        return self.user.get_full_name() # get_full_name is a method defined in the built-in django user model
        # __str__ is called automatically when you try to display an object in a template without referencing any attributes
        # for example, in a template you could have
            # <p>{{ employee }}</p>
        # because of defining a __str__ method, this would have the same output as
            # <p>{{ employee.user.get_full_name }}</p>
    def notify(self, context, message):
        nn = Notification(to=self, context=context, message=message)
        nn.save()
    def get_personal_pronoun(self):
        if self.pronouns == 'M':
            return 'him'
        elif self.pronouns == 'F':
            return 'her'
        else:
            return 'them'
    def get_RA_floor(self): # for the stupid single apartments double floor RAs
        string = self.building
        if self.room and self.building in ['Acacia', 'Birch', 'Manzanita', 'Oak', 'Willow']:
            if self.room[0] == '1':
                string += ' 1 and 2'
            elif self.room[0] == '3':
                string += ' 3 and 4'
            return string
        else:
            try:
                return string + ' ' + self.room[0]
            except IndexError:
                return ''
        return ''

    # OVERRIDE of standard save() method to force formatting on phone numbers and resizing images
    def save(self, *args, **kwargs):
        if self.photo:
            image = Image.open(self.photo)
            image = image.resize((250, 250))
            image.save(self.photo.path)
        if len(self.phone) != 14:
            if self.phone == '() -':
                pass
            if len(self.phone) == 4:
                old = self.phone
                self.phone = '(657) 278-{}'.format(old)
            else:
                old = self.phone
                for token in old:
                    if not token.isdigit():
                        old = old.replace(token, '')
                area = old[0:3]
                first = old[3:6]
                second = old[6:10]
                self.phone = '({}) {}-{}'.format(area, first, second)
        super(Employee, self).save(*args, **kwargs) # Call the "real" save() method.


class Post(models.Model):
    # this is the model that stores the posts on the homepage of the portal
    title = models.CharField(max_length=200)
    content = models.TextField(help_text='Use this editor to customize what your homepage post will look like. Please note that the exact appearance may differ slightly.')
    created_date = models.DateTimeField(blank=True, default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    header_color = models.CharField(max_length=7, choices=COLOR_CHOICES, default='blue')
    admin_only = models.BooleanField(default=False, help_text='If yes, this post will only be visible to Portal Administrators', verbose_name='Admin-Visible Only')
    last_published_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'user__is_staff':True})

    # OVERRIDE of standard save() method to force update published date.
    def save(self, *args, **kwargs):
        self.published_date = timezone.now()
        super(Post, self).save(*args, **kwargs) # Call the "real" save() method.
    def __str__(self):
        return self.title

class Page(models.Model):
    title = models.CharField(max_length=100)
    customurl = models.CharField(max_length=30, unique=True, validators=[validate_slug], help_text='Use a single word or multiple words separated by a dash(-)', verbose_name="Link")
    content = models.TextField()
    created_date = models.DateTimeField(blank=True, default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    admin_only = models.BooleanField(default=False, help_text='If yes, this page will only be visible to Portal Administrators', verbose_name='Admin-Visible Only')
    icon = models.CharField(max_length=20, default="do_not_disturb", help_text='For icon options, visit <a href="https://material.io/icons/" target="_blank">https://material.io/icons/</a>. If the icon name has a space, replae it with an underscore (_).')
    # OVERRIDE of standard save() method to force update published date
    def save(self, *args, **kwargs):
        self.published_date = timezone.now()
        super(Page, self).save(*args, **kwargs) # Call the "real" save() method.
    def get_cname(self):
        return 'Page'
    def __str__(self):
        return self.title

class TabbedPageContent(Page):
    parent = models.CharField(choices=TABBED_PAGE_CHOICES, blank=True, null=True, max_length=1)
    def get_cname(self):
        return 'Tab'
    class Meta:
        verbose_name_plural = 'Tab Content'

class Notification(models.Model):
    to = models.ForeignKey(Employee, on_delete=models.CASCADE)
    message = models.TextField()
    context = models.CharField(max_length=10, choices=STATUS_CHOICES, default='info')
    unread = models.BooleanField(default=True)
    sent_date = models.DateTimeField(blank=True, null=True)
    # OVERRIDE of standard save() method to force update published date.
    def save(self, *args, **kwargs):
        self.sent_date = timezone.now()
        super(Notification, self).save(*args, **kwargs) # Call the "real" save() method.
    def __str__(self):
        string = '{}-level message sent to {}'.format(self.context, self.to)
        return string

class FormData(models.Model):
    formID = models.SmallIntegerField(blank=True)
    formName = models.CharField(max_length=30, default='')
    date = models.DateField(auto_now_add=True, editable=True)
    qty = models.SmallIntegerField(default=0)
    staff = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True)
    last_saved = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        string = "{}s submitted on {}: {}".format(self.formName, self.date, self.qty)
        if self.formID == 17:
            string += " by {}.".format(self.staff)
        return string
    def save(self, *args, **kwargs):
        self.last_saved = timezone.now()
        super(FormData, self).save(*args, **kwargs)
    class Meta:
        verbose_name_plural = 'Form Data Records'
