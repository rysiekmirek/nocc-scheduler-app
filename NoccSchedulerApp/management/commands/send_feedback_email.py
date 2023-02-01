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
            send_email(
                subject = f'[NOCC-Visit-Scheduler] - Please tell us more about Your visit at Akamai NOCC on {tour.date} - it takes just 1 minute to complete', 
                to = [tour.requestor_email, 'rmirek@akamai.com'], 
                html_content = f'<h2>Hi {tour.requestor_name}, </h2><br> Please go to our <br> <a href="http://nvs.akamai.com/feedback/{tour.id}">feedback form </a>' \
                                f'and share Your experience with us')

            tour.feedback_status = 'Request sent'
            tour.save()
            print(tour)
