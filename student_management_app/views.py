from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .EmailBackEnd import EmailBackEnd
from django.contrib.auth import login, logout
from django.contrib import messages

# Create your views here.
def showDemoPage(request):
    return render(request, "demo.html")

def showLoginPage(request):
    return render(request, "login.html")

def doLogin(request):
    if request.method != "POST":
        return HttpResponse('<h2>Method Not Allowed</h2>')
    else:
        user = EmailBackEnd.authenticate(request, request.POST.get("email"), request.POST.get("password"))
        if user != None:
            login(request, user)
            if user.user_type == "1":
                return HttpResponseRedirect("/admin_home")
            elif user.user_type == "2":
                return HttpResponseRedirect("/staff_home")
            elif user.user_type == "3":
                return HttpResponseRedirect("/student_home")
            else:
                messages.error(request, 'Invalid Login Details For Profile')
                return HttpResponseRedirect("/")
        else:
            messages.error(request, 'Invalid Login Details')
            return HttpResponseRedirect("/")

def getUserDetail(request):
    if request.user != None:
        return HttpResponse(f'User : {request.user.email} UserType : {request.user.user_type}')
    else:
        return HttpResponse("<h2> Please login first </h2>")

def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")