from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseServerError, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime
import json
from xkcdpass import xkcd_password as xp

from .models import Post, Employee, Page, TabbedPageContent, Notification, notify_devs
from .forms import PostEditorForm, PageEditorForm, UserDescForm, NewUserForm
from .json_interpreter import interpret

@login_required
def home(request):
    posts = Post.objects.all().order_by('-published_date')
    return render(request, 'portal/home.html', {'posts': posts})

@login_required
def staff(request):
    employees = Employee.objects.all()
    form = NewUserForm
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            pwd = request.POST['fname'].lower() + '57'
            if len(request.POST['username']) < 6:
                messages.warning(request, 'Usernames must be at least six characters. You should manually set a name for this user if the generator button makes a username of less than 6 characters.')
                return render(request, 'portal/staff.html', {'employees': employees, 'form': form})
            try:
                newuser = User.objects.create_user(request.POST['username'], email=request.POST['email'], password=pwd, first_name=request.POST['fname'], last_name=request.POST['lname'])
                newuser.save()
                birthday = datetime.strptime(request.POST['birthday'], '%m/%d/%Y')
                dept = ''
                if request.POST['title'] in ['Resident Advisor', 'Senior Resident Advisor']:
                    dept = 'RE'
                else:
                    dept = 'ACS'
                newemp = Employee(user=newuser, supervisor=request.user.employee, department=dept, title=request.POST['title'], building=request.POST['building'], room=request.POST['room'], birthday=birthday, pronouns=request.POST['pronouns'])
                newemp.save()
                messages.success(request, 'New user "{}" created successfully with username: "{}" and password: "{}" <br /><strong><a href="/admin/auth/user/{}/change/">Click here to make changes to their profile.</a></strong>'.format(newemp, request.POST['username'], pwd, newuser.id))
                request.user.employee.notify('success', 'You successfully created a new account for {}.'.format(newemp))
            except:
                messages.error(request, 'Something went wrong trying to create a new user.')
        else:
            messages.error(request, str(form.errors))
    return render(request, 'portal/staff.html', {'employees': employees, 'form': form})

@login_required
def custom_page(request, name):
    slug = name # this is used to look up the page by its customurl field
    customPage = get_object_or_404(Page, customurl=slug)
    if request.user.is_staff and customPage.admin_only:
        # if the page is visible to managers only
        return render(request, 'portal/custom.html', {'CustomPage': customPage})
    elif customPage.admin_only and not request.user.is_staff:
        # even though the manager-only links won't appear for non-managers to click on
        # this will redirect them if they type in the URL directly and display an error
        messages.error(request, "You don't have permission to view that page.")
        return redirect('/')
    else:
        return render(request, 'portal/custom.html', {'CustomPage': customPage})

@login_required
def calendars(request):
    tabs = TabbedPageContent.objects.all().filter(parent='C')
    return render(request, 'portal/calendars.html', {'tabs':tabs})

@login_required
def marketing(request):
    tabs = TabbedPageContent.objects.all().filter(parent='M')
    return render(request, 'portal/marketing.html', {'tabs':tabs})

@login_required
def programming(request):
    tabs = TabbedPageContent.objects.all().filter(parent='P')
    return render(request, 'portal/programming.html', {'tabs':tabs})

@staff_member_required
def ftresources(request):
    tabs = TabbedPageContent.objects.all().filter(parent='F')
    return render(request, 'portal/staff-resources.html', {'tabs':tabs})

@user_passes_test(lambda u: u.is_superuser)
def devdocs(request):
    return render(request, 'portal/devdocs.html')

@login_required
def profile(request, username):
    employee = get_object_or_404(Employee, user__username=username)
    if request.method == 'POST':
        form = UserDescForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your description was updated successfully.')
            request.user.employee.supervisor.notify('info', '{} updated their profile.'.format(request.user.employee))
            return redirect('/staff/{}'.format(employee.user.username))
    else:
        form = UserDescForm(instance=employee)
    return render(request, 'portal/profile.html', {'employee':employee, 'form':form})

@login_required
def notifications(request):
    return render(request, 'portal/notifications.html')

@login_required
def notif_clear(request, id):
    emp = request.user.employee
    notifs = Notification.objects.filter(to=emp)
    notifs.update(unread=False)
    return redirect('/notifications/')

@staff_member_required(login_url='portal:login')
def all_pages(request):
    return render(request, 'portal/pages.html')

@staff_member_required(login_url='portal:login') # decorator to require Portal Administrator permission
def post_edit(request, id):
    item = get_object_or_404(Post, id=id)
    cname = 'Post' # used by the editor template
    if request.method == 'POST':
        form = PostEditorForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post "{}" was saved successfully.'.format(item.title))
            item.last_published_by = request.user.employee
            item.save()
            notify_devs('info', "{} updated the post: '{}' at {}.".format(request.user.get_full_name(), item.title, datetime.now().strftime('%I:%M %p on %A, %B %d, %Y')))
            return redirect('/')
    else:
        form = PostEditorForm(instance=item)
    return render(request, 'portal/editor.html', {'item': item, 'cname':cname, 'form':form})

@staff_member_required(login_url='portal:login')
def page_edit(request, id):
    item = get_object_or_404(Page, id=id)
    cname = 'Page' # used by the editor template
    if request.method == 'POST':
        form = PageEditorForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Page "{}" was saved successfully.'.format(item.title))
            notify_devs('info', "{} updated the page: '{}' at {}.".format(request.user.get_full_name(), item.title, datetime.now().strftime('%I:%M %p on %A, %B %d, %Y')))
            return redirect('/pages/all/')
        else:
            messages.error(request, 'Error saving changes to page "{}"'.format(item.title))
            return redirect('/pages/all/')
    else:
        form = PageEditorForm(instance=item)
    return render(request, 'portal/editor.html', {'item': item, 'cname':cname, 'form':form})

@staff_member_required(login_url='portal:login')
def tab_edit(request, id):
    item = get_object_or_404(TabbedPageContent, id=id)
    cname = 'Tab'
    if request.method == 'POST':
        form = PageEditorForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            notify_devs('info', "{} updated tab content: '{}' at {}.".format(request.user.get_full_name(), item.title, datetime.now().strftime('%I:%M %p on %A, %B %d, %Y')))
            messages.success(request, 'Tab content saved successfully: "{}" on the {} page.'.format(item.title, item.get_parent_display()))
            return redirect('/')
        else:
            messages.error(request, 'Error saving changes. Please try again or contact a web admin. Error details: {}'.format(form.errors))
            return redirect('/')
    else:
        form = PageEditorForm(instance=item)
    return render(request, 'portal/editor.html', {'item': item, 'cname':cname, 'form':form})

# adding new posts and pages uses the following pattern:
# 1. user navigates to a /new page that django routes to these views
# 2. views just create a new post or page entry with default, pre-filled values
# 3. the browser is then directed to the /edit page for that entry id
# so -->> if a user clicks to add a page and didn't mean to, they need to go back and delete it.
@staff_member_required(login_url='portal:login')
def new_post(request):
    newpost = Post.objects.create(title='put your title here', content='<p>Insert post content here.</p>')
    newpost.save()
    request.user.employee.notify('info', 'You created a new homepage post. <strong><a href="/posts/edit/{}">Click here to edit it.</a></strong>'.format(newpost.id))
    return redirect('/posts/edit/{}'.format(newpost.id))

@staff_member_required(login_url='portal:login')
def new_page(request):
    newpage = Page.objects.create(title='put your title here', content='<p>Insert page content here.</p>', customurl="url-goes-here", icon="do_not_disturb")
    newpage.save()
    request.user.employee.notify('info', 'You created a new page. <strong><a href="/pages/edit/{}">Click here to edit it.</a></strong>'.format(newpage.id))
    return redirect('/pages/edit/{}'.format(newpage.id))

@staff_member_required(login_url='portal:login')
def post_delete(request, id):
    item = get_object_or_404(Post, id=id)
    if item.delete(): # returns true if it's successful
        messages.success(request, 'Post deleted successfully.')
        return redirect('/')
    else:
        messages.error(request, 'There was an error trying to delete the post.')
        return redirect('/')

@staff_member_required(login_url='portal:login')
def page_delete(request, id):
    item = get_object_or_404(Page, id=id)
    if item.delete():
        messages.success(request, 'Page deleted successfully.')
        return redirect('/')
    else:
        messages.error(request, 'There was an error trying to delete the page.')
        return redirect('/')

@staff_member_required(login_url='portal:login')
def make_user_inactive(request, id):
    # this is the equivalent to deleting a user but deleting is bad
    item = get_object_or_404(User, id=id)
    try:
        if item.is_staff:
            # if some tries to make a Portal Administrator inactive
            # note that this eliminates the need to check if a user is deleting themself
            # we just have to trust superusers not to do this
            # because a superuser can set themself as inactive but they shouldn't
            # other note: this permission checking won't happen if a manager tries to set another manager
            #    as inactive through the django admin. need to fix that.
            if request.user.is_superuser:
                # only superusers can do this
                item.is_active = False
                item.save()
                messages.success(request, 'Staff member "{}" successfully set as inactive. They will no longer be able to access this portal.')
                return redirect('/staff/')
            else:
                messages.error(request, "You don't have permission to mark another Portal Administrator as inactive. Contact a web admin for assistance.")
                return redirect('/staff/')
        else:
            item.is_active = False
            item.save()
            messages.success(request, 'Staff member successfully set as inactive. They will no longer be able to access this portal. To restore their Active status, click "Add or Modify Staff" in the sidebar.')
        return redirect('/staff/')
    except:
        messages.error(request, 'There was an error accessing the user\'s account.')
        return redirect('/staff/')

@csrf_exempt
def json_consumer(request):
    if request.content_type == 'application/json':
        string = str(request.body, 'utf-8')
        output = json.loads(string)
        interpret(output)
        return redirect('/')
    else:
        return redirect('/')

def password_generator(request):
    wordfile = xp.locate_wordfile()
    words = xp.generate_wordlist(wordfile=wordfile, min_length=2, max_length=8)
    generated = xp.generate_xkcdpassword(words, acrostic=request.user.first_name.lower())
    messages.info(request, 'Your randomly generated password is: <strong>{}</strong>'.format(generated))
    return redirect('/')

def server_error(request):
    notify_devs('danger', '{} caused a 500 error. Please check the error log for details.'.format(request.user.get_full_name()))
    messages.error(request, 'Something went wrong trying to process your request. Our web admins have been notified of the error and will try to fix it as soon as possible.')
    return redirect('/')

# Auth Views
# don't touch these
# they are taken directly from django built-ins.
def login(request):
	return render(request, 'portal/login.html')

def logout(request):
    return render(request, 'portal/login.html')

def password_change(request):
    pages = Page.objects.all().order_by('created_date')
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {'form': form})
