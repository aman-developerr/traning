from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, logout, login
from .models import Routine
from django.contrib.auth.models import User
import datetime as dt
import socket
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="geoapiExercises")

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def user_login(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            forms = AuthenticationForm(data=request.POST)
            if forms.is_valid():
                uname = forms.cleaned_data['username']
                upass = forms.cleaned_data['password']
                user = authenticate(username=uname, password=upass)
                if user is not None:
                    login(request, user)
                    messages.success(request, 'login successful!!!')
                    return HttpResponseRedirect('/profile/' + str(request.user.id) + '/')
            return HttpResponse('form is invalid')

        else:
            forms = AuthenticationForm()
        return render(request, 'login.html', {'forms': forms, 'messages': messages})
    else:
        return HttpResponseRedirect('/profile/' + str(request.user.id) + '/')


def user_profile(request, pk):
    if request.user.is_authenticated:
        ip = get_client_ip(request)
        routines = Routine.objects.filter(user_id=request.user.id).order_by('-today_date')
        context = {'name': request.user, 'routines': routines, 'ip': ip}
        return render(request, 'profile.html', context=context)
    else:
        return HttpResponseRedirect('/login/')


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/login/')


def today(request):
    if request.user.is_authenticated:
        todays_date = Routine.objects.filter(user_id=request.user.id).order_by('-today_date')[0]
        date = dt.datetime.today().date()

        if request.method == 'POST':
            time = dt.datetime.today().time()
            longitude = request.POST.get('longitude')
            latitude = request.POST.get('latitude')
            in_ip = hostname + '  ' + IPAddr
            location = geolocator.reverse(latitude + "," + longitude)

            if todays_date.today_date == date:
                todays_date.out_location = location
                todays_date.check_out_time = time
                todays_date.out_ip = in_ip
                todays_date.save()
                return HttpResponseRedirect('/profile/' + str(request.user.id) + '/')
            else:
                data = Routine(
                    user_id=User.objects.get(id=request.user.pk),
                    today_date=date,
                    in_location=location,
                    check_in_times=time,
                    in_ip=in_ip,
                )
                data.save()
                return HttpResponseRedirect('/profile/' + str(request.user.id) + '/')

        else:
            todays_date = Routine.objects.filter(user_id=request.user.id).order_by('-today_date')[0]
            date = dt.datetime.today().date()
            if todays_date.today_date == date:
                check = 1
                if todays_date.check_out_time:
                    check = 2
            else:
                check = 0
            todays_date = dt.datetime.today().strftime("%d/%m/%Y")
            context = {'todays_date': todays_date, 'check': check}
            return render(request, 'today.html', context=context)

    else:
        return HttpResponseRedirect('/login/')


def edit_routine(request, pk):
    if request.user.is_authenticated:
        if request.method == 'POST':
            routine = Routine.objects.get(pk=pk)
            routine.current_project = request.POST['current_project']
            routine.billable_task = request.POST['billable_task']
            routine.break_time = request.POST['break_time']
            routine.task_owner = request.POST['task_owner']
            routine.approved_by = request.POST['approved_by']
            routine.save()
            return HttpResponseRedirect('/profile/' + str(request.user.id) + '/')
        else:
            routine = Routine.objects.get(pk=pk)
            context = {'user': request.user,'routine':routine}
            return render(request, 'edit_routine.html', context=context)


def test(request):
    todays_date = Routine.objects.filter(user_id=request.user.id).order_by('-today_date')[0]
    date = dt.datetime.today().date()
    print(todays_date, date)
    if todays_date.today_date == date:
        date = 'true'
    context = {'date': date}
    return render(request, 'test.html', context=context)
