from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse


class LoginCheckMiddleWare(MiddlewareMixin):

    def process_view(selfself, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user

        print(f'User {user} with module name {modulename} trying to access the application')

        if user == 'AnonymousUser':
            return HttpResponseRedirect(reverse('show_login'))

        if user.is_authenticated:
            if user.user_type == "1":
                if modulename == "student_management_app.HodViews":
                    pass
                elif modulename == "student_management_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse('admin_home'))
            elif user.user_type == "2":
                if modulename == "student_management_app.StaffViews":
                    pass
                elif modulename == "student_management_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse('staff_home'))
            elif user.user_type == "3":
                if modulename == "student_management_app.StudentViews":
                    pass
                elif modulename == "student_management_app.views" or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse('student_home'))
            else:
                return HttpResponseRedirect(reverse('show_login'))
        else:
            print(request.path)
            if request.path == reverse('show_login') or reverse('do_login') or modulename == "django.contrib.auth.urls":
                pass
            else:
                return HttpResponseRedirect(reverse('show_login'))


