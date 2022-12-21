from django.shortcuts import render, redirect, HttpResponse
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.contrib import messages
from .models import Tour, Location, Availability
from .forms import TourForm, TourFormEdit, AvailabilityForm
import requests
import uuid
import calendar
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from datetime import date, datetime, timedelta, time
from django.db.models import Q
from django.http import JsonResponse



def main(request):

    context = {
        'tours': Tour.objects.filter(date__gte=date.today()).exclude(status="Rejected").exclude(status="Canceled").order_by('date', 'start_time'),
    }
    return render(request, "main.html", context)

@login_required(login_url='/login/')
def tour_details(request, pk):
    tour_data = Tour.objects.filter(id=pk).values()[0]

    if request.method == 'POST':
        instance = Tour.objects.get(id=pk)
        form = TourFormEdit(request.POST, instance=instance)
        if form.is_valid():
            if form.has_changed():
                messages.success(request, 'Tour details updated')
                form.save()
                return redirect('/tour-details/'+pk)

    location = Location.objects.get(id=tour_data['location_id'])

    context = {
        'nocc_representatives_list': location.nocc_representatives_list.split(','),
        'selected_nocc_representative': tour_data['nocc_person_assigned'],
        'selected_location': location.location,
        'tour_data': tour_data,
        'form': TourFormEdit(initial=tour_data)
    }
    print (context)
    return render(request, "tour-details.html", context)


def view_calendar(request):
    if request.method == 'POST':
        try:
            month = int(request.POST["month"])
            year = int(request.POST["year"])
        except:
            month = datetime.now().month
            year = datetime.now().year
    else:
        month = datetime.now().month
        year = datetime.now().year
    month_dates = calendar.Calendar().monthdatescalendar(year, month)
    context = {
        'tours': Tour.objects.filter(date__gte=month_dates[0][0]).exclude(date__gte=month_dates[-1][-1]).exclude(status="Rejected").order_by('date', 'start_time'),
        'month': month,
        'year': year,
        'month_dates': month_dates,
    }
    return render(request, "calendar.html", context)


@login_required(login_url='/login/')
def archives(request):
    tours = Tour.objects.filter(Q(date__lt=date.today()) | Q(status="Rejected") | Q(status="Canceled")).order_by('date', 'start_time')
    context = {
        'tours': tours,
    }
    return render(request, "archives.html", context)


def login_user(request):

    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST['f_username']
        password = request.POST['f_password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.warning(request, 'User not found')
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.warning(
                request, 'Username or password incorrect, try again')
            return render(request, 'login.html')

    return render(request, "login.html")


def logout_user(request):
    logout(request)
    return redirect("/")


@login_required(login_url='/login/')
def ask_for_feedback(request, pk):
    tour_data = Tour.objects.filter(id=pk).values()[0]
    subject = '[NOCC-Tour-Scheduler] - Please tell us more about " ' + \
        tour_data['tour_name'] + " \" - survey invitation"
    from_email = 'nocc-tour-scheduler@akamai.com'
    to = [tour_data['requestor_email'], 'rmirek@akamai.com']
    html_content = "<h2>Hi " + tour_data['requestor_name'] + \
        ", </h2><br> Please visit <br> <a href=\"http://194.233.175.38:8000/feedback/"+pk+"\">Link</a>"
    msg = EmailMessage(subject, html_content, from_email, to)
    msg.content_subtype = "html"
    msg.send()
    messages.success(request, 'Invitation for after-tour survey sent to requestor')

    return redirect("/tour-details/"+pk)

@login_required(login_url='/login/')
def status_change(request, pk):
    tour_data = Tour.objects.filter(id=pk).values()[0]
    if request.method == 'POST':
        status=request.POST['f_status']
        if tour_data['status'] != status:
            Tour.objects.filter(id=pk).update(status=status)
            if status == "Approved":
                messages.success(request, 'Requestor will be informed via email that tour was approved')
                subject = '[NOCC-Tour-Scheduler] - Your tour " ' + \
                    tour_data['tour_name'] + " \" was approved"
                from_email = 'nocc-tour-scheduler@akamai.com'
                to = [tour_data['requestor_email'], 'rmirek@akamai.com']
                html_content = "<h2>Hi " + \
                    tour_data['requestor_name'] + \
                    ", </h2><br> To check status of the request see <br> <a href=\"http://194.233.175.38:8000/\">Link</a>"
                msg = EmailMessage(subject, html_content, from_email, to)
                msg.content_subtype = "html"
                msg.send()
            elif status == "Requested":
                messages.warning(request, 'Tour status set to requested')
            else:
                availability_entry=Availability.objects.get(avail_date=tour_data['date'], location_id=tour_data['location_id'])
                availability_entry_list=availability_entry.time_slots.split(',')
                start_time_string = tour_data['start_time'].strftime("%H:%M")
                end_time_string = tour_data['end_time'].strftime("%H:%M")
                availability_entry_list.append(start_time_string + "-" + end_time_string)
                availability_entry_list.sort()
                availability_entry.time_slots = ','.join(availability_entry_list)
                availability_entry.save()
                if status == "Rejected":
                    messages.warning(request, 'Requestor will be informed via email that tour was rejected')
                    subject = '[NOCC-Tour-Scheduler] - Your tour " ' + \
                        tour_data['tour_name'] + " \" was rejected"
                else:
                    messages.warning(request, 'Requestor will be informed via email that tour was canceled')
                    subject = '[NOCC-Tour-Scheduler] - Your tour " ' + \
                        tour_data['tour_name'] + " \" was canceled"

                from_email = 'nocc-tour-scheduler@akamai.com'
                to = [tour_data['requestor_email'], 'rmirek@akamai.com']
                html_content = "<h2>Hi " + \
                    tour_data['requestor_name'] + \
                    ", </h2><br> To check status of the request see <br> <a href=\"http://194.233.175.38:8000/\">Link</a>"
                msg = EmailMessage(subject, html_content, from_email, to)
                msg.content_subtype = "html"
                msg.send()

    return redirect("/tour-details/"+pk)


def feedback(request, pk):
    if request.method == 'POST':
        feedback = request.POST['f_feedback']
        Tour.objects.filter(id=pk).update(feedback=feedback)
        messages.success(request, 'Thank You, feedback submitted successfully')

    return render(request, "feedback.html" )

def new_tour(request):
    if request.method == 'POST':
        form = TourForm(request.POST)
        r=request.POST
        tour_data= r.dict()
        print("Form is valid")
        print(form.errors)
        start_time= r['start_time']
        end_time = r['end_time']
        dbentry = form.save(commit=False)
        dbentry.tour_name = str(r['customer_or_group_name']) + "--" + str(r['category']) + "--" + str(r['date'])
        uuid_value = uuid.uuid4()
        dbentry.id = uuid_value
        dbentry.start_time = datetime.strptime(start_time, "%H:%M").time()
        dbentry.end_time = datetime.strptime(end_time, "%H:%M").time()
        print (dbentry, dbentry.start_time , dbentry.end_time )
        dbentry.save()
        print (dbentry.date)
        availability_entry=Availability.objects.get(avail_date=dbentry.date, location_id=dbentry.location)
        time_slots_updated = availability_entry.time_slots.replace(r['time_slot_selection'] + ",",'',1)
        availability_entry.time_slots = time_slots_updated
        availability_entry.save()

        messages.success(request, 'Your tour has been submited and confirmation email sent to You. Please wait for approval from local NOCC representative.')
        tour_data = Tour.objects.filter(id=uuid_value).values()[0]
        subject = '[NOCC-Tour-Scheduler] - New Tour " ' + tour_data['tour_name'] + " \" was requested, please wait for approval email"
        from_email = 'nocc-tour-scheduler@akamai.com'
        to = [tour_data['requestor_email'], 'rmirek@akamai.com']
        if tour_data['nocc_personnel_required'] == "Yes":
            to.append('nocc-tix@akamai.com')
        html_content = '<h2>Hi '+ tour_data['requestor_name'] + ',</h2><br><h3>Tour details:</h3>'
        for key, data in tour_data.items():
            html_content += "<b>" + str(key) + "</b> : "
            html_content += "<i>" + str(data) + "</i><br>"
        html_content += "<br> To check status of the request see <br> <a href=\"http://194.233.175.38:8000/\">http://194.233.175.38:8000</a>"
        msg = EmailMessage(subject, html_content, from_email, to)
        msg.content_subtype = "html"
        msg.send()
        return redirect("/")
    else:
        context={
            'locations': Location.objects.all(),
            'form': TourForm(),
        }
        return render (request, "new-tour.html", context)


def get_avail_times(request):
    r=request.GET
    if request.method == 'GET' and r['location'] != '' and r['date'] != '':
        f_location=request.GET['location']
        f_date= request.GET['date']
        print (f_location)
        #try:
        #location = Location.objects.get(location_id=f_location)
        avail_start_time, avail_end_time = Availability.objects.filter(avail_date=f_date, location=f_location).values()[0]['avail_time'].split('-')
        print (avail_start_time, avail_end_time)
        avail_start_time = datetime.strptime(avail_start_time, "%H:%M").time()
        avail_end_time = datetime.strptime(avail_end_time, "%H:%M").time()
        entry = avail_start_time
        start_times = []
        end_times =[]
        while entry < avail_end_time:
            start_times.append(entry.strftime("%H:%M"))
            entry = (datetime.combine(date.today(), entry) + timedelta(minutes=15)).time()
            #entry = entry + timedelta(minutes=15)
            end_times.append(entry.strftime("%H:%M"))
        print (start_times)
        print (end_times)
        #time_slots = Availability.objects.filter(avail_date=f_date, location_id=f_location).values()[0]['time_slots'].split(',')
        #start_times=['8:00','8:15','8:30','8:45','9:00','9:15','9:30','9:45','10:00']
        #end_times=['8:15','8:30','8:45','9:00','9:15','9:30','9:45','10:00']
        #except:
            #start_times=""
            #end_times=""
    else:
        start_times=""
        end_times=""

    return JsonResponse({
        "start_times": start_times,
        "end_times": end_times,
     })

def settings(request):

    if request.method == 'POST':
        r=request.POST
        location=r['location']
        location_instance=Location.objects.get(location=location)
        if 'nocc_representatives_list' in r:
            nocc_representatives_list = r['nocc_representatives_list'].replace(' ','')
            Location.objects.filter(location=location).update(nocc_representatives_list=nocc_representatives_list)
            return redirect('/settings/' )
        else:
            from_date = datetime.strptime(r['from_date'], "%Y-%m-%d").date()
            to_date = datetime.strptime(r['to_date'], "%Y-%m-%d").date()
            avail_time = r['avail_time']
            delta = to_date - from_date
            for i in range(delta.days + 1):
                day = from_date + timedelta(days=i)
                Availability.objects.update_or_create(location=location_instance, avail_date=day,
                defaults={
                        'location': location_instance,
                        'avail_time': avail_time,
                        'avail_date': day
                        })
            messages.success(request, 'Time slots updated successfully')



    context = {
        'availability_data_cambridge': Availability.objects.filter(location__location='Cambridge', avail_date__gte=date.today()).order_by('avail_date'),
        'nocc_representatives_list_cambridge' : Location.objects.get(location='Cambridge').nocc_representatives_list,
     }

    return render(request, "settings.html", context )