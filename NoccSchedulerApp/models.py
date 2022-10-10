from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models


class Tour(models.Model):
    tour_name = models.CharField(max_length=300)
    requestor_name = models.CharField(max_length=300)
    requestor_email = models.EmailField()
    alternate_contact = models.CharField(max_length=300)
    attendees_akamai = models.IntegerField(default=0)
    attendees_guests = models.IntegerField(default=0)
    current_customer = models.BooleanField()
    CATEGORY_CHOICES = [
        ('existing customer', 'Existing Customer'),
        ('new prospect', 'New Prospect'),
        ('public relations / press / analysts',
         'Public Relations / Press / Analysts'),
        ('investors', 'Investors'),
        ('akamai employees (internal tour)', 'Akamai Employees (Internal Tour)'),
        ('students / informal guests', 'Students / Informal Guests'),
    ]
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='existing customer',
    )
    nocc_required = models.BooleanField()
    location = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField(help_text="use local time for location")
    end_time = models.TimeField(help_text="use local time for location")
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(unique=True, primary_key=True, editable=True)

    def clean(self):
        # self.clean_fields()
        start_time = self.start_time
        end_time = self.end_time
        if start_time >= end_time:
            raise ValidationError({'end_time': ValidationError(
                _('End time has to be after start time'), code='invalid')})
        for existing_tour in Tour.objects.all():
            if self.date == existing_tour.date:
                if existing_tour.start_time <= start_time <= existing_tour.end_time:
                    raise ValidationError(
                        {'start_time': _("Start time colides with an exising tour", code='invalid')})
                if existing_tour.start_time <= end_time <= existing_tour.end_time:
                    raise ValidationError(
                        {'end_time': _("Start time colides with an exising tour", code='invalid')})
                if start_time <= existing_tour.start_time and end_time >= existing_tour.end_time:
                    raise ValidationError({'start_time': ValidationError(
                        _('Tour ca\'t encompas existing tour'), code='invalid'), 'end_time': ValidationError(
                        _('Tour ca\'t encompas existing tour'), code='invalid')})

    def __str__(self):
        return self.tour_name
