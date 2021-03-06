from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, logout, login
from .models import Routine, Feedback, Profile
from django.contrib.auth.models import User
import datetime as dt
import socket
from geopy.geocoders import Nominatim
from django.contrib.auth.decorators import login_required
from django.db.models import Q

geolocator = Nominatim(user_agent="geoapiExercises")

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
login_url = '/'


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
                    return HttpResponseRedirect('/today/')
            return HttpResponse('form is invalid')
        else:
            forms = AuthenticationForm()
        return render(request, 'login.html', {'forms': forms, 'messages': messages})
    else:
        return HttpResponseRedirect('/dashboard/' + str(request.user.id) + '/')


@login_required(login_url=login_url)
def user_dashboard(request, pk):
    todays_date = Routine.objects.filter(user=request.user.id).order_by('-today_date').first()
    date = dt.datetime.today().date()
    if not todays_date:
        return HttpResponseRedirect('/today/')
    else:
        if todays_date.today_date != date:
            return HttpResponseRedirect('/today/')

    routines = Routine.objects.filter(user=request.user.id).order_by('-today_date')
    context = {'routines': routines}
    return render(request, 'dashboard.html', context=context)


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required(login_url=login_url)
def today(request):
    todays_date = Routine.objects.filter(user=request.user.id).order_by('-today_date').first()
    date = dt.datetime.today().date()
    if request.method == 'POST':
        time = dt.datetime.today().time()
        try:
            longitude = request.POST.get('longitude')
            latitude = request.POST.get('latitude')
        except:
            messages.error(request,'Turn on your location and Try again')
            return HttpResponseRedirect('/today/')
        # in_ip = hostname + '  ' + IPAddr
        in_ip = f"{hostname}  {IPAddr}"
        location = geolocator.reverse(latitude + "," + longitude)
        if todays_date != None:
            if todays_date.today_date == date:
                todays_date.out_location = location
                todays_date.check_out_time = time
                todays_date.out_ip = in_ip
                todays_date.save()
                return HttpResponseRedirect('/dashboard/' + str(request.user.id) + '/')
            else:
                data = Routine(
                    user=User.objects.get(id=request.user.pk),
                    today_date=date,
                    in_location=location,
                    check_in_times=time,
                    in_ip=in_ip,
                )
                data.save()
                return HttpResponseRedirect('/dashboard/' + str(request.user.id) + '/')
        else:
            data = Routine(
                user=User.objects.get(id=request.user.pk),
                today_date=date,
                in_location=location,
                check_in_times=time,
                in_ip=in_ip,
            )
            data.save()
            return HttpResponseRedirect('/dashboard/' + str(request.user.id) + '/')

    else:
        todays_date = Routine.objects.filter(user=request.user.id).order_by('-today_date').first()
        date = dt.datetime.today().date()
        if todays_date == None:
            check = 0
        else:
            if todays_date.today_date == date:
                check = 1
                if todays_date.check_out_time:
                    check = 2
            else:
                check = 0
        todays_date = dt.datetime.today().strftime("%d/%m/%Y")
        context = {'todays_date': date, 'check': check}
        return render(request, 'today.html', context=context)


@login_required(login_url=login_url)
def edit_routine(request, pk):
    routinees = Routine.objects.filter(user=request.user.id)._values('pk')
    for routinee in routinees:
        if routinee.id == pk:
            if request.method == 'POST':
                routine = Routine.objects.get(pk=pk)
                routine.current_project = request.POST['current_project']
                routine.billable_task = request.POST['billable_task']
                routine.break_time = request.POST['break_time']
                routine.task_owner = request.POST['task_owner']
                routine.approved_by = 'Pending'

                if routine.task_owner == 'me':
                    routine.approved_by = str(request.user)
                routine.save()
                return HttpResponseRedirect('/dashboard/' + str(request.user.id) + '/')
            else:
                routine = Routine.objects.get(pk=pk)
                trainers = User.objects.filter(groups__name='trainers')
                context = {'user': request.user, 'routine': routine, 'trainers': trainers}
                return render(request, 'edit_routine.html', context=context)
    return HttpResponseRedirect('/')


@login_required(login_url=login_url)
def trainee(request):
    if request.user.groups.filter(name='trainers').exists():
        trainees = User.objects.filter(groups__name='trainee')
        context = {'trainees': trainees}
        return render(request, 'trainees.html', context)
    else:
        return HttpResponseRedirect('/')


@login_required(login_url=login_url)
def trainee_details(request, pk):
    routines = Routine.objects.filter(user=pk).order_by('-today_date')
    trainee = User.objects.get(pk=pk)
    context = {'name': request.user, 'routines': routines, 'trainee': trainee}
    return render(request, 'trainee_profile.html', context=context)


@login_required(login_url=login_url)
def notifications(request, pk):
    if request.method == 'POST':
        routine = Routine.objects.get(pk=pk)
        approval = request.POST.get('approval')
        if approval == 'approved':
            routine.approved_by = str(request.user)
        else:
            routine.approved_by = approval
        routine.save()
        return HttpResponseRedirect('/notifications/' + str(request.user.id) + '/')
    else:
        # routines = Routine.objects.filter(Q(task_owner__contains=str(request.user)),(Q(approved_by__icontains='pending') | Q(approved_by__icontains=str(request.user))))
        routines = Routine.objects.filter().order_by('-today_date')
        context = {'routines': routines}
        return render(request, 'notification.html', context)


@login_required(login_url=login_url)
def profile(request, pk):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        s
        user = User.objects.get(pk=pk)
        if first_name:
            user.first_name=first_name
        if last_name:
            user.last_name=last_name
        if email:
            user.email=email

        user.save()
        return HttpResponseRedirect('/')
    else:
        user = User.objects.get(pk=pk)
        context = {'user': user}
        return render(request, 'profile.html', context)


def test(request):
    b = 12
    # a = Routine.objects.filter(user=request.user.id)._values('pk')
    # print(a)
    abc = 'none'

    if b == b:
        abc = 'abc'
        return render(request, 'test.html', {'a': abc})

    else:
        abc = 'efg'

    return render(request, 'test.html', {'a': abc})

    # if request.user.groups.filter(name='trainers').exists():
    #     context = {'todays_date': request.user}
    #     return render(request, 'test.html', context=context)
    # else:
    #     context = {'todays_date': 'fjhasjdlfj'}
    #     return render(request, 'test.html', context=context)
    # todays_date = User.objects.filter(groups__name='trainers')
    # # date = dt.datetime.today().date()
    # # print(todays_date, date)
    # # if todays_date.today_date == date:
    # #     date = 'true'
