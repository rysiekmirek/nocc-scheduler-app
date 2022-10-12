from django.db import models
import uuid


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
        ('public relations / press / analysts', 'Public Relations / Press / Analysts'),
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
    date = models.DateField()
    location = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                            primary_key=True, editable=False)
    def __str__(self):
        return self.tour_name
                            