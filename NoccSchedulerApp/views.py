from django.shortcuts import render, redirect, HttpResponse
from .models import Tour
from .forms import TourForm
import requests


def schedule_tour(request):
    if request.method == 'POST':
        form = TourForm(request.POST)
        form.save()
        form = TourForm()
    else:
        form = TourForm()
    return render (request, "schedule-tour.html", {'form': form} )
    