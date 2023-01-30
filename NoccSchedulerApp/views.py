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
        if form.is_valid():
            if form.has_changed():
                if r['nocc_person_assigned'] != tour_data.nocc_person_assigned and r['nocc_person_assigned'] != None :
                    subject = f'[NOCC-Visit-Scheduler] - tour requested by You got assigned to {r["nocc_person_assigned"]}'
                    from_email = 'nvs@akamai.com'
                    to = [tour_data.requestor_email, 'rmirek@akamai.com']
                    html_content = f'<h2>Hi {tour_data.requestor_name}, </h2><br> this is just inromation that you tour got assigned to {r["nocc_person_assigned"]} from NOCC in {tour_data.location} '
                    msg = EmailMessage(subject, html_content, from_email, to)
                    msg.content_subtype = "html"
                    msg.send()
                    messages.success(request, 'Tour details updated and email sent to requestor with information about NOCC person assigned to the tour')
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

    print (initial_tour_data)
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
    if tour_data.feedback_status != 'Provided':
        subject = f'[NOCC-Visit-Scheduler] - Please tell us more about Your visit at Akamai NOCC on {tour_data.date}'
        from_email = 'nvs@akamai.com'
        to = [tour_data.requestor_email, 'rmirek@akamai.com']
        html_content = f'<h2>Hi {tour_data.requestor_name}, </h2><br> Please visit <br> <a href="http://nvs.akamai.com/feedback/{pk}">Link</a> and share Your feedback with us'
        msg = EmailMessage(subject, html_content, from_email, to)
        msg.content_subtype = "html"
        msg.send()
        Tour.objects.filter(id=pk).update(feedback_status='Request sent')
        messages.success(request, 'Invitation for after-tour survey sent to requestor')
    else:
        messages.warning(request, f'Feedback status is {tour_data.feedback_status}, invitation for after-tour survey not sent to requestor')

        return redirect("/tour-details/"+pk)

@login_required(login_url='/login/')
def status_change(request, pk):
    tour_data = Tour.objects.filter(id=pk).values()[0]
    if request.method == 'POST':
        status=request.POST['f_status']
        if tour_data['nocc_person_assigned'] == None and tour_data['nocc_personnel_required'] == "Yes" and status == "Approved":
            messages.error(request, 'You can\'t approve this tour without NOCC person being assigned to it, please do that first')
            return redirect("/tour-details/"+pk)
        else:
            if tour_data['status'] != status:
                Tour.objects.filter(id=pk).update(status=status)
                if status == "Approved":
                    send_email_ics(pk)
                    messages.success(request, 'Requestor will be informed via email that tour was approved')
                elif status == "Requested":
                    messages.warning(request, 'Tour status set to requested')
                else:
                    if status == "Rejected":
                        messages.warning(request, 'Requestor will be informed via email that tour was rejected')
                        subject = '[NOCC-Visit-Scheduler] - Your tour " ' + \
                            tour_data['tour_name'] + " \" was rejected"
                    else:
                        messages.warning(request, 'Requestor will be informed via email that tour was canceled')
                        subject = '[NOCC-Visit-Scheduler] - Your tour " ' + \
                            tour_data['tour_name'] + " \" was canceled"

                    from_email = 'nvs@akamai.com'
                    to = [tour_data['requestor_email'], 'rmirek@akamai.com']
                    html_content = "<h2>Hi " + \
                        tour_data['requestor_name'] + \
                        ", </h2><br> To check status of the request see <br> <a href=\"http://nvs.akamai.com\">Link</a>"
                    msg = EmailMessage(subject, html_content, from_email, to)
                    msg.content_subtype = "html"
                    msg.send()

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
        try:
            r=request.POST
            tour_data= r.dict()
            print(tour_data)
            print(form.errors)
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
            print (dbentry, dbentry.start_time , dbentry.end_time )
            dbentry.save()
            tour_data = Tour.objects.filter(id=uuid_value).values()[0]
            subject = '[NOCC-Visit-Scheduler] - New Tour " ' + tour_data['tour_name'] + " \" was requested, please wait for approval email"
            from_email = 'nvs@akamai.com'
            to = [tour_data['requestor_email'], 'rmirek@akamai.com']
            # if tour_data['nocc_personnel_required'] == "Yes":
            #     to.append('nocc-tix@akamai.com')
            html_content = '<h2>Hi '+ tour_data['requestor_name'] + ',</h2><br><h3>Tour details:</h3>'
            for key, data in tour_data.items():
                html_content += "<b>" + str(key) + "</b> : "
                html_content += "<i>" + str(data) + "</i><br>"
                if key == "status":
                    break
            # html_content += "<br> To check status of the request see <br> <a href=\"http://nvs.akamai.com\">http://nvs.akamai.com</a>"
            msg = EmailMessage(subject, html_content, from_email, to)
            msg.content_subtype = "html"
            msg.send()
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
    print(tour_data.requestor_name)

    cal = Calendar()
    cal.add('attendee', 'MAILTO:' + tour_data.requestor_email)
    cal.add('attendee', 'MAILTO:'+ tour_data.poc_email)
    cal.add('attendee', 'MAILTO:'+ 'rmirek@akamai.com')

    # Let's set time zones

    if str(tour_data.location) == 'Krakow':
        timezone = pytz.timezone('Europe/Warsaw')
    elif str(tour_data.location) == 'Bangalore':
        timezone = pytz.timezone('Asia/Calcutta')
    else:
        timezone = pytz.timezone('America/New_York')

    print(timezone)

    combined_date_time_start = datetime.combine(tour_data.date,tour_data.start_time)
    combined_date_time_end = datetime.combine(tour_data.date,tour_data.end_time)

    print(combined_date_time_end.tzinfo)

    aware_combined_date_time_start = timezone.localize(combined_date_time_start)
    aware_combined_date_time_end = timezone.localize(combined_date_time_end)

    print(aware_combined_date_time_start, aware_combined_date_time_start.tzinfo)


    event = Event()
    event.add('name', 'Akamai NOCC tour in '+ str(tour_data.location))
    event.add('summary', 'Akamai NOCC tour in '+ str(tour_data.location))
    event.add('description', 'Visit NOCC office to see how we work')
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


    subject = '[NOCC-Visit-Scheduler] Your NOCC visit has been approved'
    message = 'Some message here'
    from_email = 'nvs@akamai.com'
    to_email = tour_data.requestor_email

    html_content = f'<p>Hi {tour_data.requestor_name}, <br>' +\
                f'we would like to invite You to visit us in {tour_data.location}\'s NOCC office <br>' +\
                f'Date: {tour_data.date} <br>' +\
                f'Time: {tour_data.start_time} - {tour_data.end_time} <br>' +\
                f'Time zone: {aware_combined_date_time_start.tzinfo} </p>'


    # Create the email message
    msg = EmailMultiAlternatives(subject, message, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.attach_file(f'media/ics_files/{filename}', 'text/calendar')


    # Send the email
    msg.send()
    try:
        os.remove(f'media/ics_files/{filename}')
    except:
        print ('File not removed')

