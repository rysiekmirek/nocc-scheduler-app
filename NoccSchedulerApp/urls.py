"""NoccSchedulerApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tour-details/<str:pk>/', views.tour_details, name = 'tour_details' ),
    path('new-tour/', views.new_tour, name = 'new_tour' ),
    path('calendar/', views.view_calendar, name = 'calendar' ),
    path('archives/', views.archives, name = 'archives' ),
    path('login/', views.login_user, name = 'login' ),
    path('logout/', views.logout_user, name='logout'),
    path('status-change/<str:pk>/', views.status_change, name='status_change'),
    path('ask-for-feedback/<str:pk>/', views.ask_for_feedback, name='ask_for_feedback'),
    path('feedback/<str:pk>/', views.feedback, name='feedback'),
    path('settings/', views.settings, name='settings'),
    path('avail-times/', views.get_avail_times, name='get_avail_times'),
    #path('ical/<str:tour_id>/', views.send_email_ics, name='send_email_ics'),
    path('', views.main, name = 'main' ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
