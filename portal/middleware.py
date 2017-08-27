from django.contrib import messages
from django.contrib.auth.hashers import check_password
from datetime import timedelta, date

def default_password_check(get_response):
    """
    Custom Middleware to check if users are still using their default-assigned password and display a warning message if they are.
    """
    def middleware(request):
        if request.user.is_authenticated:
            defaultpwd = request.user.first_name.lower() + '57'
            defaultpwd2 = request.user.first_name.lower() + '1957'
            pwd = request.user.password
            if check_password(defaultpwd, pwd) or check_password(defaultpwd2, pwd):
                if not request.get_full_path().startswith('/admin'):
                    messages.warning(request, 'You are still using your default password. <a href="/password-change/"><strong>Please click here to change your password to a more secure password as soon as possible.</strong></a><br />You will continue to see this alert until you change your password.')
            today = date.today()
            last = request.user.employee.last_password_change
            if not last:
                last = date.today()
            if today - last >= timedelta(120):
                if not request.get_full_path().startswith('/admin'):
                    messages.error(request, 'Your password hasn\'t been updated in 4 months. You must change your password in the next 5 days or your account will be locked.')

        response = get_response(request)

        return response

    return middleware
