from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Tour(models.Model):
    tour_name = models.CharField(max_length=300)
    requestor_name = models.CharField(max_length=300)
    requestor_email = models.EmailField()
    alternate_contact = models.CharField(max_length=300)
    attendees_akamai = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(50)])
    attendees_guests = models.IntegerField(
        default=0, validators=[MinValueValidator(1), MaxValueValidator(50)])
    CURRENT_CUSTOMER_CHOICES = [
        ('No', 'No'),
        ('Yes', 'Yes'),
    ]
    current_customer = models.CharField(
        max_length=10,
        choices=CURRENT_CUSTOMER_CHOICES,
        default='No',
    )
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
    NOCC_REQUIRED_CHOICES = [
        ('No', 'No'),
        ('Yes', 'Yes'),
    ]

    nocc_required = models.CharField(
        max_length=10,
        choices=NOCC_REQUIRED_CHOICES,
        default='no',
    )

    LOCATION_CHOICES = [
        ('Cambridge', 'Cambridge'),
        ('Krakow', 'Kraków'),
        ('Bangalore', 'Bangalore')
    ]
    location = models.CharField(
        max_length=100, choices=LOCATION_CHOICES, default='Cambridge')
    date = models.DateField()
    start_time = models.TimeField(help_text="use local time for location")
    end_time = models.TimeField(help_text="use local time for location")
        
    PERSON_ASSIGNED_CHOICES = [
        ('None', 'None'),
        ('Adam', 'Adam'),
        ('Brian', 'Brian'),
        ('Charlie', 'Charlie'),
    ]
    nocc_person_assigned = models.CharField(
        max_length=30,
        choices=PERSON_ASSIGNED_CHOICES,
        default='None',
    )
    comment = models.TextField(max_length=2000, null=True, blank=True)
    feedback = models.TextField(
        max_length=2000, null=True, blank=True, default="No feedback yet")
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(unique=True, primary_key=True, editable=True)

    STATUS_CHOICES = [
        ('Requested', 'Requested'),
        ('Rejected', 'Rejected'),
        ('Approved', 'Approved'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Requested')

    def __str__(self):
        return self.tour_name
