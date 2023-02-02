from django.shortcuts import render, redirect, HttpResponse
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.contrib import messages
from .models import Tour, Location, Availability, NoccRepresentatives
from .forms import TourForm, TourFormDetails, TourFormFeedback, TourFormFeedbackDetails
import requests
import uuid
import calendar
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from datetime import date, datetime, timedelta, time, timezone
from django.db.models import Q
from django.http import JsonResponse
from icalendar import Calendar, Event, vCalAddress, vText
import pytz
import os
from pathlib import Path


def main(request):

    context = {
        'tours': Tour.objects.filter(date__gte=date.today()).exclude(status="Rejected").exclude(status="Canceled").order_by('date', 'start_time'),
    }
    return render(request, "main.html", context)

@login_required(login_url='/login/')
def tour_details(request, pk):
    r = request.POST
    tour_data = Tour.objects.get(id=pk)
    initial_tour_data = Tour.objects.filter(id=pk).values()[0]

    if request.method == 'POST':
        form = TourFormDetails(request.POST, instance=tour_data)
        if form.has_changed():
            if r['nocc_person_assigned'] != tour_data.nocc_person_assigned:
                tour_data.nocc_person_assigned = r['nocc_person_assigned']
                tour_data.save()
                send_email(template='tour_assignment_nocc', tour_data=tour_data)
                send_email(template='tour_assignment_visitor', tour_data=tour_data)
                messages.success(request, 'Tour details updated, emails sent to both requestor and NOCC representative with information that NOCC person is assigned to the tour')
            else:
                messages.success(request, 'Tour details updated')
            form.save()
            return redirect('/tour-details/'+pk)

    location = Location.objects.get(id=tour_data.location_id)

    context = {
        'nocc_representatives_list': NoccRepresentatives.objects.filter(location=int(tour_data.location_id)),
        'selected_nocc_representative': tour_data.nocc_person_assigned,
        'selected_location': location.location,
        'tour_data': tour_data,
        'form_edit': TourFormDetails(initial=initial_tour_data),
        'form_feedback': TourFormFeedbackDetails(initial=initial_tour_data),
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
        'tours': Tour.objects.filter(date__gte=datetime(year, month, 1)).exclude(date__gte=datetime(year, month, calendar.monthrange(year, month)[1])).exclude(status="Rejected").exclude(status="Canceled").order_by('date', 'start_time'),
        'month': month,
        'year': year,
        'today': datetime.today().date(),
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
        r=request.POST
        username = r['f_username']
        password = r['f_password']

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
    tour_data = Tour.objects.get(id=pk)
    send_email(template='feedback_form', tour_data=tour_data)
    Tour.objects.filter(id=pk).update(feedback_status='Request sent')
    messages.success(request, 'Invitation for after-tour survey sent to requestor')

    return redirect("/tour-details/"+pk)

@login_required(login_url='/login/')
def status_change(request, pk):
    tour_data = Tour.objects.filter(id=pk).values()[0]
    tour_data2 = Tour.objects.get(id=pk)
    if request.method == 'POST':
        status=request.POST['f_status']
        if tour_data['nocc_person_assigned'] == None and tour_data['nocc_personnel_required'] == "Yes" and status == "Approved":
            messages.error(request, 'You can\'t approve this tour without NOCC person being assigned to it, please do that first')
            return redirect("/tour-details/"+pk)
        else:
            if tour_data['status'] != status:
                Tour.objects.filter(id=pk).update(status=status)
                if status == "Approved":
                    send_email(template='approval', tour_data=tour_data2)
                    messages.success(request, 'Requestor will be informed via email that tour was approved')
                elif status == "Requested":
                    messages.warning(request, 'Tour status set to requested')
                else:
                    if status == "Rejected":
                        send_email(template='rejection', tour_data=tour_data2)
                        messages.warning(request, 'Requestor will be informed via email that tour was rejected')
                    else:
                        send_email(template='cancellation', tour_data=tour_data2)
                        messages.warning(request, 'Requestor will be informed via email that tour was canceled')

    return redirect("/tour-details/"+pk)


def feedback(request, pk):
    tour_data = Tour.objects.filter(id=pk).values()[0]

    if request.method == 'POST':
        instance = Tour.objects.get(id=pk)
        form = TourFormFeedback(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Feedback submitted successfully')
            return redirect('/thank-you')

    context={
            'form': TourFormFeedback(),
            'tour_data': tour_data,
        }

    return render(request, "feedback.html", context )

def thank_you(request):

    return render(request, "thank-you.html" )

def new_tour(request):
    if request.method == 'POST':
        form = TourForm(request.POST)
        print(form)
        print(form.errors)
        try:
            r=request.POST
            start_time= r['start_time']
            end_time = r['end_time']
            date = r['date']
            dbentry = form.save(commit=False)
            dbentry.tour_name = str(r['customer_or_group_name']) + "-" + str(r['date'])
            uuid_value = uuid.uuid4()
            dbentry.id = uuid_value
            dbentry.date = datetime.strptime(date, '%Y-%m-%d').date()
            dbentry.start_time = datetime.strptime(start_time, "%H:%M").time()
            dbentry.end_time = datetime.strptime(end_time, "%H:%M").time()
            dbentry.save()
            tour_data=Tour.objects.get(id=uuid_value)
            send_email(template='new_request', tour_data=tour_data)
            messages.success(request, 'Your tour has been submited and confirmation email sent to You. Please wait for approval from local representative.')
            return redirect("/thank-you")
        except:
            context={
            'locations': Location.objects.all(),
            'form': form,
            }
            return render (request, "new-tour.html", context)

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
        try:
            avail_start_time, avail_end_time = Availability.objects.filter(avail_date=f_date, location=f_location).values()[0]['avail_time'].split('-')
            avail_start_time = datetime.strptime(avail_start_time, "%H:%M").time()
            avail_end_time = datetime.strptime(avail_end_time, "%H:%M").time()
            entry = avail_start_time
            start_times = []
            end_times =[]
            while entry < avail_end_time:
                start_times.append(entry.strftime("%H:%M"))
                entry = (datetime.combine(date.today(), entry) + timedelta(minutes=15)).time()
                end_times.append(entry.strftime("%H:%M"))

            other_tours_that_day = Tour.objects.filter(date=f_date,location=f_location).exclude(status="Rejected").exclude(status="Canceled").values()
            for tour in other_tours_that_day:
                existing_tours_times = []
                tour_start_time = tour['start_time']
                tour_end_time = tour['end_time']
                i= tour_start_time
                while i <= tour_end_time:
                    existing_tours_times.append(i.strftime("%H:%M"))
                    i = (datetime.combine(date.today(), i) + timedelta(minutes=15)).time()
                start_times = list(set(start_times) - set(existing_tours_times[:-1]))
                end_times = list(set(end_times) - set(existing_tours_times[1:]))
                print (existing_tours_times)

            end_times = sorted(end_times)
            start_times = sorted(start_times)
            print (start_times)
            print (end_times)

        except:
            start_times=""
            end_times=""
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
        print(r)
        if 'name' in r and 'email' in r:
            NoccRepresentatives.objects.create(location=location_instance, name= r['name'], email = r['email'])
            messages.success(request, f'{location_instance}\'s NOCC representatives list updated successfully')
        elif 'person_id' in r:
            person = NoccRepresentatives.objects.get(location__location=location_instance, id=int(r['person_id']))
            person.delete()
            messages.warning(request, f' Person removed from NOCC representatives list')

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
            messages.success(request, f'{location_instance}\'s time slots updated successfully')


    context = {
        'availability_data_cambridge': Availability.objects.filter(location__location='Cambridge', avail_date__gte=date.today()).order_by('avail_date'),
        'nocc_representatives_list_cambridge' : NoccRepresentatives.objects.filter(location__location='Cambridge'),
        'availability_data_krakow': Availability.objects.filter(location__location='Krakow', avail_date__gte=date.today()).order_by('avail_date'),
        'nocc_representatives_list_krakow' : NoccRepresentatives.objects.filter(location__location='Krakow'),
        'availability_data_bangalore': Availability.objects.filter(location__location='Bangalore', avail_date__gte=date.today()).order_by('avail_date'),
        'nocc_representatives_list_bangalore' : NoccRepresentatives.objects.filter(location__location='Bangalore'),
     }
    return render(request, "settings.html", context )


def send_email_ics(pk):

    tour_data = Tour.objects.get(id=pk)

    cal = Calendar()
    cal.add('attendee', 'MAILTO:' + tour_data.requestor_email)
    cal.add('attendee', 'MAILTO:'+ tour_data.poc_email)

    # Let's set time zones

    if str(tour_data.location) == 'Krakow':
        timezone = pytz.timezone('Europe/Warsaw')
    elif str(tour_data.location) == 'Bangalore':
        timezone = pytz.timezone('Asia/Calcutta')
    else:
        timezone = pytz.timezone('America/New_York')

    combined_date_time_start = datetime.combine(tour_data.date,tour_data.start_time)
    combined_date_time_end = datetime.combine(tour_data.date,tour_data.end_time)

    aware_combined_date_time_start = timezone.localize(combined_date_time_start)
    aware_combined_date_time_end = timezone.localize(combined_date_time_end)

    event = Event()
    event.add('name', 'Akamai NOCC visit in '+ str(tour_data.location))
    event.add('summary', 'Akamai NOCC visit in '+ str(tour_data.location))
    event.add('description', 'Visit Akamai NOCC office')
    event.add('dtstart', aware_combined_date_time_start)
    event.add('dtend', aware_combined_date_time_end)
    event.add('dtstamp', datetime.now())

    event['location'] = vText(tour_data.location)

    # Adding events to calendar
    cal.add_component(event)

    directory = str(Path(__file__).parent.parent) + "/media/ics_files/"
    print("ics file will be generated at ", directory)
    filename=f'invitation{tour_data.date}-{tour_data.start_time}.ics'
    f = open(os.path.join(directory, filename), 'wb')
    f.write(cal.to_ical())
    f.close()


    subject = f'NOCC visit approved - {tour_data.tour_name}'
    message = 'Some message here'
    from_email = 'nvs@akamai.com'
    to_email = [tour_data.requestor_email, tour_data.poc_email, tour_data.cc_this_request_to, 'rmirek@akamai.com']

    html_content = f'<p>Hi {tour_data.requestor_name}, <br>' +\
                f'Your NOCC visit has been approved with the following details {tour_data.location}\'s NOCC office <br>' +\
                f'Date: {tour_data.date} <br>' +\
                f'Time: {tour_data.start_time} - {tour_data.end_time} <br>' +\
                f'Time zone: {aware_combined_date_time_start.tzinfo} </p>' +\
                f'Please find calendar invitation attached.'
    #add footer to the email
    html_content += f'<br> Regards, <br> <br> <hr> <br> <b>Akamai Technologies NOCC </b> <br> <b>e-mail:</b> nocc-shift@akamai.com <br> <a href="http://www.akamai.com"> www.akamai.com </a>' \
                    f'<br> <b> Phone: </b> 1-877-6-AKAMAI (1-877-625-2624) | International +1-617-444-3007'


    # Create the email message
    msg = EmailMultiAlternatives(subject, message, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.attach_file(f'media/ics_files/{filename}', 'text/calendar')


    # Send the email
    msg.send()
    try:
        os.remove(f'media/ics_files/{filename}')
    except:
        print ('File not removed')

def send_email(template, tour_data, subject='', html_content='', to=[]):
    
    if template == 'new_request':
        subject = f'New Akamai NOCC visit Requested with title - {tour_data.tour_name}'
        html_content = f'Hi {tour_data.requestor_name}, <br> we received your request for a NOCC visit. Your visit is not confirmed yet.' \
                        f'<br> Next, we will review the details of the visit and get back to you.'
        html_content += f'<br><h3>Tour details:</h3>'
        for key, data in tour_data.__dict__.items():
            if key =='_state':
                key=''
                data=''
            else:
                html_content += "<b>" + str(key) + "</b> : "
                html_content += "<i>" + str(data) + "</i><br>"
                if key == "status":
                    break
        to= [tour_data.requestor_email, tour_data.cc_this_request_to, tour_data.poc_email, 'rmirek@akamai.com']

    elif template == 'approval':
        send_email_ics(tour_data.id)
        return redirect ('/tour-details/'+str(tour_data.id))

    elif template == 'rejection':
        subject = f'NOCC visit rejected - {tour_data.tour_name}'
        html_content = f'Hi {tour_data.requestor_name}, <br> we are sorry to inform that Your request for a NOCC visit has been rejected.' \
                        f'<br> For more information please contact {tour_data.poc_name}, {tour_data.poc_email}'
        to= [tour_data.requestor_email, tour_data.cc_this_request_to, tour_data.poc_email, 'rmirek@akamai.com']

    elif template == 'cancellation':
        subject = f'NOCC visit canceled - {tour_data.tour_name}'
        html_content = f'Hi {tour_data.requestor_name}, <br> we are sorry to inform that Your visit "{tour_data.tour_name}"  has been canceled.' \
                        f'<br> For more information please contact {tour_data.poc_name}, {tour_data.poc_email}'
        to= [tour_data.requestor_email, tour_data.cc_this_request_to, tour_data.poc_email, 'rmirek@akamai.com']

    elif template == 'tour_assignment_nocc':
        nocc_rep = NoccRepresentatives.objects.get(name=tour_data.nocc_person_assigned)
        subject = f'You\'ve been assigned a NOCC visit - {tour_data.tour_name}'
        html_content = f'Hi {tour_data.nocc_person_assigned}, <br> You have been assigned to the tour "{tour_data.tour_name}".' \
                        f'<br>  If you are not able to attend please notify the local NOCC team as soon as possible.'
        html_content += f'<br><h3>Tour details:</h3>'
        for key, data in tour_data.__dict__.items():
            if key =='_state':
                key=''
                data=''
            else:
                html_content += "<b>" + str(key) + "</b> : "
                html_content += "<i>" + str(data) + "</i><br>"
                if key == "status":
                    break
        to= [nocc_rep.email, 'rmirek@akamai.com']
    
    elif template == 'tour_assignment_visitor':
        subject = f'NOCC visit has been assigned - {tour_data.tour_name}'
        html_content = f'Hi {tour_data.requestor_name}, <br> Your NOCC visit "{tour_data.tour_name}" has been assigned to {tour_data.nocc_person_assigned}.'
        to= [tour_data.requestor_email, tour_data.cc_this_request_to, tour_data.poc_email, 'rmirek@akamai.com']
    
    elif template == 'feedback_form':
        subject = f'30 seconds survey - Did you enjoy your NOCC visit? - {tour_data.tour_name}'
        html_content = f'Hi, <br> The survey below takes ~30 seconds to complete.' + \
                        f'<br> Did you enjoy your time at the NOCC? We\'d like to hear from your.' + \
                        f'<br> Survey: <a href="http://nvs.akamai.com/feedback/{tour_data.id}">Feedback form </a>'
                        
        to= [tour_data.requestor_email, tour_data.cc_this_request_to, tour_data.poc_email, 'rmirek@akamai.com']

    elif template == 'custom':
        subject = subject
        html_content = html_content
        to = to
    else:
        subject = f'Send function failed to match template'
        html_content = ''
        to= ['rmirek@akamai.com']

    #add footer to the email
    html_content += f'<br> Regards, <br> <br> <hr> <br> <b>Akamai Technologies NOCC </b> <br> <b>e-mail:</b> nocc-shift@akamai.com <br> <a href="http://www.akamai.com"> www.akamai.com </a>' \
                    f'<br> <b> Phone: </b> 1-877-6-AKAMAI (1-877-625-2624) | International +1-617-444-3007'
    from_email='nvs@akamai.com'
    msg = EmailMessage(subject, html_content, from_email, to)
    msg.content_subtype = "html"
    msg.send()
