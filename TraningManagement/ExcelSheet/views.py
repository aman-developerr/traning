from django.shortcuts import render, HttpResponseRedirect, HttpResponse, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, logout, login
from .models import Routine, Feedback, Profile, FeedbackRequest
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
            return render(request, 'login.html', {'forms': forms, 'messages': messages})
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
            messages.error(request, 'Turn on your location and Try again')
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
    trainee = User.objects.get(pk=pk)
    print(trainee.get_all_permissions())
    if len(trainee.get_all_permissions())  < 10:
        routines = Routine.objects.filter(user=pk).order_by('-today_date')
        print(len(trainee.get_all_permissions()))
        context = {'name': request.user, 'routines': routines, 'trainee': trainee}
        return render(request, 'trainee_profile.html', context=context)
    else:
        return HttpResponseRedirect('/trainee/')


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
    if request.user.pk == pk:
        if request.method == "POST":
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            try:
                img = request.FILES['file']
                x = float(request.POST['x'])
                y = float(request.POST['y'])
                w = float(request.POST['width'])
                h = float(request.POST['height'])

                image = Image.open(img)

                cropped_image = image.crop((x, y, w + x, h + y))

                resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)

                pic_io = BytesIO()

                resized_image.save(pic_io, image.format)

                pic_file = InMemoryUploadedFile(
                    file=pic_io, field_name=None, name=img.name, content_type=img.content_type, size=img.size, charset=None
                )

            except:
                pic_file = False
            user = User.objects.get(pk=pk)
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if email:
                user.email = email
            print('a')
            if pic_file:
                print('a')
                try:
                    profile = Profile.objects.get(user=request.user.id)
                    if pic_file:
                        profile.file = pic_file
                        profile.save()
                        print('a')
                except:
                    if pic_file:
                        data = Profile(
                            user=user,
                            file=pic_file,
                        )
                        data.save()
            user.save()
            messages.success(request,'Update Success full')


        user = User.objects.get(pk=pk)
        context = {'user': user}
        return render(request, 'profile.html', context)

    else:
        return HttpResponseRedirect('/')


@login_required(login_url=login_url)
def feedback(request):
    if request.method == 'POST':
        trainer = request.POST['trainer_name']
        date_time = dt.datetime.now()
        feedback_request = FeedbackRequest.objects.filter(trainer__exact=trainer, user__exact=request.user)
        print('bbb')
        if feedback_request:
            messages.info(request, 'Already requested')
            return HttpResponseRedirect('/feedback/')
        data = FeedbackRequest(
            user=request.user,
            feedback_request=True,
            trainer=trainer,
            request_time=date_time
        )
        data.save()
        return HttpResponseRedirect('/feedback/')

    else:
        feedbacks = Feedback.objects.filter(user=request.user.id)
        feedback_requested = FeedbackRequest.objects.filter(user=request.user.id)
        feedback_requests = FeedbackRequest.objects.filter(trainer__contains=request.user)
        trainers = User.objects.filter(groups__name='trainers')
        context = {'trainers': trainers, 'feedbacks': feedbacks, 'feedback_requested': feedback_requested,
                   'feedback_requests': feedback_requests}
        return render(request, 'feedback.html', context)


def feedback_add(request):
    date_time = dt.datetime.now()
    if request.method == "POST":
        feedback = request.POST['feedback']
        feedback_id = request.POST['feedback_id']

        trainee_id = request.POST.get('trainee_id')
        data = Feedback(
            trainer=request.user,
            user=User.objects.get(pk=trainee_id),
            feedback_time=date_time,
            feedback=feedback
        )
        data.save()
        data = FeedbackRequest.objects.get(pk=feedback_id)
        data.delete()
        return HttpResponseRedirect('/feedback/')


from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from io import BytesIO

def test(request):
    global w, y, x, h
    print(type(request.user))
    print(type(request.user.id))
    print(type(request.user.pk))

    pk = request.user.pk
    if request.method == "POST":
        print('inside post')
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        try:
            x = float(request.POST['x'])
            y = float(request.POST['y'])
            w = float(request.POST['width'])
            h = float(request.POST['height'])
            print(x)
        except:
            img = False

        print('insidety')
        img = request.FILES['file']

        print(type(img))
        image = Image.open(img)
        print(type(image))
        cropped_image = image.crop((x, y, w + x, h + y))
        print("image = Image.open(img.file)")
        resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)

        pic_io = BytesIO()
        resized_image.save(pic_io, image.format)
        pic_file = InMemoryUploadedFile(
            file=pic_io, field_name=None, name=img.name, content_type=img.content_type, size=img.size, charset=None
        )

        profile = Profile.objects.get(user=request.user.id)
        print(profile)
        # data = Profile(file=img, user=request.user)
        print('ab')
        profile.file = pic_file
        print('an')
        profile.save()
        return HttpResponseRedirect('/t/')
        # except:
        #     print('inside except')
        #     img = False
        # user = User.objects.get(pk=pk)
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email
        if img:
            try:
                profile = Profile.objects.get(user=request.user.id)
                if img:
                    profile.profile_image = img
                    profile.save()
            except:
                if img:
                    data = Profile(
                        user=user,
                        profile_image=img,
                    )
                    data.save()
        user.save()
        return HttpResponseRedirect('/t/')
    else:
        user = User.objects.get(pk=pk)
        context = {'user': user}
        return render(request, 'test.html', context)

    # b = 12
    # # a = Routine.objects.filter(user=request.user.id)._values('pk')
    # # print(a)
    # abc = 'none'
    #
    # if b == b:
    #     abc = 'abc'
    #     return render(request, 'test.html', {'a': abc})
    #
    # else:
    #     abc = 'efg'
    #
    # return render(request, 'test.html', {'a': abc})

    # if request.user.groups.filter(name='trainers').exists():
    #     context = {'todays_date': request.user}
    #     return render(request, 'test.html', context=context)
    # else:
    #     context = {'todays_date': 'fjhasjdlfj'}
    #     return render(request, 'test.html', context=context)
    # todays_date = User.objects.filter(groups__name='trainers')
    # # date = dt.datetime.today().date()
    # #     date = 'true'
    # # print(todays_date, date)
    # # if todays_date.today_date == date:
