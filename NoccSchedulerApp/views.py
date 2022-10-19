from django.shortcuts import render, redirect, HttpResponse
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.contrib import messages
from .models import Tour
from .forms import TourForm, TourFormEdit
import requests
import uuid



def schedule_tour(request):
    if request.method == 'POST':
        form = TourForm(request.POST)
        if form.is_valid():
            dbentry = form.save(commit=False)
            uuid_value = uuid.uuid4()
            dbentry.id = uuid_value
            dbentry.save()
        tour_data = Tour.objects.filter(id=uuid_value).values()[0]

        subject = '[NOCC-Tour-Scheduler] - New Tour " ' + tour_data['tour_name'] + " \" was scheduled"
        from_email = 'nocc-tour-scheduler@srv30945.seohost.com.pl'
        to = ['rysiekmirek@gmail.com']
        html_content = '<h2>Hi '+ tour_data['requestor_name'] + ',</h2><br><h3>Tour details:</h3>'
        for key, data in tour_data.items():
            html_content += "<b>" + str(key) + "</b> : "
            html_content += "<i>" + str(data) + "</i><br>"
        html_content += "\n\n Please visit \n <a href=\"http://194.233.175.38:8000/schedule-tour/tour-details/"+str(tour_data['id'])+"\">Click</a>"
        msg = EmailMessage(subject, html_content, from_email, to)
        msg.content_subtype = "html"
        msg.send()
        
        
    form = TourForm()
    context={
        'tours': Tour.objects.all().order_by('date'),
        'form': form
    }
    return render (request, "schedule-tour.html", context)

def tour_details(request, pk):
    tour_data = Tour.objects.filter(id=pk).values()[0]
    
    if request.method == 'POST':
        instance = Tour.objects.get(id=pk)
        form = TourFormEdit(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Użytkownik został utworzony')
            return redirect('/schedule-tour/tour-details/'+pk)

    context = {
        'tour_data': tour_data,
        'form': TourFormEdit(initial=tour_data)
    }
    return render (request, "tour-details.html", context)