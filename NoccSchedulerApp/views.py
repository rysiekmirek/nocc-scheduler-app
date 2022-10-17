from django.shortcuts import render, redirect, HttpResponse
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from .models import Tour
from .forms import TourForm
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
        tour_data = Tour.objects.filter(id=uuid_value).values()

        subject = '[NOCC-Tour-Scheduler] - New Tour - ' + tour_data[0]['tour_name']
        from_email = 'nocc-tour-scheduler@srv30945.seohost.com.pl'
        to = ['rysiekmirek@gmail.com']
        html_content = '<p>This is an <strong>important</strong> message.</p>'
        msg = EmailMessage(subject, html_content, from_email, to)
        msg.content_subtype = "html"
        msg.send()
        
        
    form = TourForm()
    context={
        'tours': Tour.objects.all().order_by('date'),
        'form': form
    }
    return render (request, "schedule-tour.html", context)
