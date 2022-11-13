from django.shortcuts import render, redirect, HttpResponse
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.contrib import messages
from .models import Tour, Location, Availability
from .forms import TourForm, TourFormEdit
import requests
import uuid
import calendar
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
from django.db.models import Q


def main(request):

    form = TourForm()
    context = {
        'tours': Tour.objects.filter(date__gte=date.today()).exclude(status="Rejected").order_by('date', 'start_time'),
        # 'tours': Tour.objects.all().order_by('date'),
        'form': form
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

    context = {
        'tour_data': tour_data,
        'form': TourFormEdit(initial=tour_data)
    }
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
        'tours': Tour.objects.filter(date__gte=month_dates[1][1]).exclude(date__gte=month_dates[-1][-1]).exclude(status="Rejected").order_by('date', 'start_time'),
        'month': month,
        'year': year,
        'month_dates': month_dates,
    }
    return render(request, "calendar.html", context)


@login_required(login_url='/login/')
def archives(request):
    tours = Tour.objects.filter(Q(date__lt=date.today()) | Q(
        status="Rejected")).order_by('date', 'start_time')
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
    messages.success(
        request, 'Invitation for after-tour survey sent to requestor')

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
            elif status == "Rejected":
                messages.warning(request, 'Requestor will be informed via email that tour was rejected')
                subject = '[NOCC-Tour-Scheduler] - Your tour " ' + \
                    tour_data['tour_name'] + " \" was rejected"
                from_email = 'nocc-tour-scheduler@akamai.com'
                to = [tour_data['requestor_email'], 'rmirek@akamai.com']
                html_content = "<h2>Hi " + \
                    tour_data['requestor_name'] + \
                    ", </h2><br> To check status of the request see <br> <a href=\"http://194.233.175.38:8000/\">Link</a>"
                msg = EmailMessage(subject, html_content, from_email, to)
                msg.content_subtype = "html"
                msg.send()
            else:
                messages.warning(request, 'Tour status set to requested')

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
        r = request.POST
        start_time, end_time = r['time_slot_selection'].replace(' ','').split("-")
        dbentry = form.save(commit=False)
        dbentry.tour_name = str(r['customer_or_group_name']) + "--" + str(r['category']) + "--" + str(r['date'])
        uuid_value = uuid.uuid4()
        dbentry.id = uuid_value
        dbentry.start_time = datetime.strptime(start_time, "%H:%M").time()
        dbentry.end_time = datetime.strptime(end_time, "%H:%M").time()
        print (dbentry, dbentry.start_time , dbentry.end_time )
        dbentry.save()
        #date_of_tour = datetime.strptime(dbentry.date,"%Y-%M-%D").date
        print (dbentry.date)
        availability_update=Availability.objects.filter(avail_date=dbentry.date).filter(location=dbentry.location).values()[0]

        print(availability_update)

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

    
        context = {
            'form': form
        }
        return render(request, "new-tour.html", context)


    form = TourForm()
    location_id = Location.objects.filter(location="Krakow").values()[0]['id']
    context={
        'time_slots': Availability.objects.filter(avail_date="2022-11-13",location_id=location_id).values()[0]['time_slots'].split(','),
        'form': form,
    }
    return render (request, "new-tour.html", context)