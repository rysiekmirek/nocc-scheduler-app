from django.db import models
from datetime import datetime
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _



class Location(models.Model):
    LOCATION_CHOICES = [
        ('Cambridge', 'Cambridge'),
        ('Krakow', 'Krakow'),
        ('Bangalore', 'Bangalore')
    ]
    location = models.CharField(max_length=100, choices=LOCATION_CHOICES, default='Cambridge')
    nocc_representatives_list = models.CharField(max_length=2000)

    def __str__(self):
        return self.location

class Availability(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    avail_date = models.DateField()
    time_slots = models.TextField(max_length=5000)
    def __str__(self):
        return str(self.location) + "x" + str(self.avail_date)

class Tour(models.Model):
    tour_name = models.CharField(max_length=300)
    requestor_name = models.CharField(max_length=300)
    requestor_email = models.EmailField()
    poc_name = models.CharField(max_length=300)
    poc_email = models.EmailField()
    cc_this_request_to = models.EmailField(help_text="Ability to CC more people in order to receive feedback form + invitation to event once it has been approved.")
    DIVISION_CHOICES = [
        ('P & RE', 'P & RE'),
        ('Customer & Industry', 'Customer & Industry'),
        ('marketing', 'Marketing'),
        ('Global Events', 'Global Events'),
        ('Marketing Strategy', 'Marketing Strategy'),
        ('Legal', 'Legal'),
        ('CTO', 'CTO'),
        ('CEO', 'CEO'),
        ('Global Sales', 'Global Sales'),
        ('Customer Success', 'Customer Success'),
        ('Global Services', 'Global Services'),
        ('Products & Enablement', 'Products & Enablement'),
        ('Compute', 'Compute'),
        ('Edge Delivery', 'Edge Delivery'),
        ('Edge Business Operations', 'Edge Business Operations'),
        ('Edge Experience', 'Edge Experience'),
        ('Other', 'Other'),
    ]
    division = models.CharField(
        max_length=50,
        choices=DIVISION_CHOICES,
        default='P & RE',
    )

    LOCATION_CHOICES = [
        ('Cambridge', 'Cambridge'),
        ('Krakow', 'Krakow'),
        ('Bangalore', 'Bangalore')
    ]
    #location = models.CharField(max_length=100, choices=LOCATION_CHOICES, default='Cambridge')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    NOCC_REQUIRED_CHOICES = [
        ('No', 'No'),
        ('Yes', 'Yes'),
    ]
    nocc_personnel_required = models.CharField(
        max_length=10,
        choices=NOCC_REQUIRED_CHOICES,
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
    )
    opportunity_ID = models.CharField(max_length=300, null=True, blank=True)

    attendees_akamai = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(50)])
    attendees_guests = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(50)])

    customer_or_group_name = models.CharField(max_length=200)

    TYPE_OF_CUSTOMERS=[
        ('Financial Services', 'Financial Services'),
        ('Media', 'Media'),
        ('High Tech', 'High Tech'),
        ('Retail + Commerce', 'Retail + Commerce'),
        ('Gaming/OTT', 'Gaming/OTT'),
        ('Healthcare/Life Science', 'Healthcare/Life Science'),
        ('Manufacturing', 'Manufacturing'),
        ('Other', 'Other'),
    ]

    type_of_customers = models.CharField(max_length=200, choices=TYPE_OF_CUSTOMERS)
    
    PERSON_ASSIGNED_CHOICES = [
        ('None', 'None'),
        ('Adam', 'Adam'),
        ('Brian', 'Brian'),
        ('Charlie', 'Charlie'),
    ]
    nocc_person_assigned = models.CharField(
        max_length=50,
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
