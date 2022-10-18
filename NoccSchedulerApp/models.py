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
    LOCATION_CHOICES = [('cambridge','Cambridge'), ('krakow','Kraków'), ('bangalore','Bangalore')]
    location = models.CharField(max_length=100,choices=LOCATION_CHOICES,default='Cambridge')
    date = models.DateField()
    start_time = models.TimeField(help_text="use local time for location")
    end_time = models.TimeField(help_text="use local time for location")
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(unique=True, primary_key=True, editable=True)

    def __str__(self):
        return self.tour_name
