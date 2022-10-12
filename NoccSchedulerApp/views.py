from django.shortcuts import render, redirect, HttpResponse
from django.core.mail import send_mail
from .models import Tour
from .forms import TourForm
import requests


def schedule_tour(request):
    if request.method == 'POST':
        form = TourForm(request.POST)
        form.save()
        send_mail(
        '[NOCC-Tour-Scheduler]',
        'New tour was scheduled.',
        'nocc-tour-scheduler@srv30945.seohost.com.pl',
        ['rysiekmirek@gmail.com'],
        fail_silently=False,
        )
    form = TourForm()
    context={
        'tours': Tour.objects.all().order_by('date'),
        'form': form
    }
    return render (request, "schedule-tour.html", context)
    


    

send_mail(
    'Subject here',
    'Here is the message.',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,
)