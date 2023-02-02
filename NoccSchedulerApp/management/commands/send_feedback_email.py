from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.utils import timezone
from NoccSchedulerApp.models import Tour
from NoccSchedulerApp.views import send_email


class Command(BaseCommand):
    help = 'Checks the database and sends feedback emails'

    def handle(self, *args, **options):
        # Query the database for all dates in the past
        tours = Tour.objects.filter(date__lt=timezone.now().date(), feedback_status='Request not sent', status="Approved")

        for tour in tours:
            send_email(template='feedback_form', tour_data=tour)
            tour.feedback_status = 'Request sent'
            tour.save()
            print(tour)

        send_email(template='cron_ran', tour_data=tours.first())