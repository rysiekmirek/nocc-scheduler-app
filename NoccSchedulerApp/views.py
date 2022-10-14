from django.shortcuts import render, redirect, HttpResponse
from django.core.mail import send_mail, EmailMessage
from .models import Tour
from .forms import TourForm
import requests
import uuid



def schedule_tour(request):
    if request.method == 'POST':
        form = TourForm(request.POST)
        if form.is_valid():
            dbentry = form.save(commit=False)
            dbentry.id = uuid.uuid4()
            dbentry.save()
            
        email = EmailMessage(
        subject = '[NOCC-Tour-Scheduler] - New Tour',
        body = 'Hi, new tour was scheduled.' + str(form.data),
        from_email = 'nocc-tour-scheduler@srv30945.seohost.com.pl',
        to = ['rysiekmirek@gmail.com'],
        reply_to = ['ryszard.mirek@gmail.com'],
        )
        email.send()
        
    form = TourForm()
    context={
        'tours': Tour.objects.all().order_by('date'),
        'form': form
    }
    return render (request, "schedule-tour.html", context)
