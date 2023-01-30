from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.utils import timezone
from tours.models import Tour


class Command(BaseCommand):
    help = 'Checks the database and sends feedback emails'

    def handle(self, *args, **options):
        # Query the database for all dates in the past
        tours = Tour.objects.filter(date__lt=timezone.now().date(), feedback_status='Request not sent')

        for tour in tours:
            subject = '[NOCC-Visit-Scheduler] - Please tell us more about Your visit at Akamai NOCC '
            from_email = 'nvs@akamai.com'
            to = [tour.requestor_email, 'rmirek@akamai.com']
            html_content = f'<h2>Hi {tour.requestor_name}, </h2><br> Please visit <br> <a href="http://nvs.akamai.com/feedback/{tour.id}">Link</a> and share Your feedback with us'
            msg = EmailMessage(subject, html_content, from_email, to)
            msg.content_subtype = "html"
            msg.send()

Command.command = "check_and_send_feedback_request"