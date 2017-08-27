from django import forms
from django.forms import Textarea, TextInput, Select, EmailInput, DateInput, RadioSelect, Form, FileInput
from django.contrib.auth.models import User

from .models import Post, Page, Employee
from .models import DEPARTMENT_CHOICES, BUILDING_CHOICES, PRONOUN_CHOICES

# this file determines how django renders forms into views.py for use in templates
# if you want to change any of these, be sure to read the django forms documentation
# specifically, these are ModelForms that are related to a particular database model

# save some typing
standardreq = {'class':'form-control', 'required':"", 'autocomplete':"off"}
standard = {'class':'form-control', 'autocomplete':"off"}

# these are self explanatory
class PostEditorForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['created_date', 'published_date'] # these shouldn't be manually editable
        widgets = {
            'title': TextInput(attrs=standardreq),
            'content': Textarea(attrs={"required":""}),
            'header_color': Select(attrs={"hidden":""})
            # "why is the input for header_color hidden?" because:
            # the header_color input is still rendered on the page so that it's included in the form
            # but it's set through buttons on the editor template that use jQuery to update the hidden input
            # because buttons are more fun. and interactive
            }

class PageEditorForm(forms.ModelForm):
    class Meta:
        model = Page
        exclude = ['created_date', 'published_date']
        widgets = {
            'title': TextInput(attrs=standardreq),
            'customurl': TextInput(attrs=standardreq),
            'content': Textarea(attrs={"required":""}),
            'icon': TextInput(attrs=standard),
            }
class UserDescForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['bio', 'photo', 'phone']
        widgets = {
            'bio': Textarea(attrs=standard),
            'photo': FileInput(attrs=standard),
            'phone': TextInput(attrs=standard),
        }

# this isn't completely implemented yet
class NewUserForm(Form):
    fname = forms.CharField(label="First Name", max_length=30, strip=True, widget=TextInput(attrs=standardreq))
    lname = forms.CharField(label="Last Name", max_length=30, strip=True, widget=TextInput(attrs=standardreq))
    email = forms.EmailField(widget=EmailInput(attrs={'class':'form-control', 'required':"", 'autocomplete':"off", 'email':"true"}))
    username = forms.CharField(min_length=6, max_length=150, widget=TextInput(attrs=standardreq))
    title = forms.ChoiceField(choices=[('Resident Advisor','Resident Advisor'), ('Senior Resident Advisor', 'Senior Resident Advisor'), ('Office Assistant', 'Office Assistant'), ('Senior Office Assistant', 'Senior Office Assistant')])
    pronouns = forms.ChoiceField(choices=PRONOUN_CHOICES, required=False)
    building = forms.ChoiceField(choices=BUILDING_CHOICES, required=False, initial='')
    room = forms.CharField(min_length=3, max_length=3, required=False, widget=TextInput(attrs=standard))
    birthday = forms.DateField(input_formats=['%m/%d/%Y'], widget=DateInput(attrs={'class':'form-control datepicker', 'required':"", 'autocomplete':"off"}))
