from django.contrib import admin

from .models import Tour, Location, Availability

admin.site.register(Tour)
admin.site.register(Location)
admin.site.register(Availability)

radio_fields = {'satisfaction': admin.HORIZONTAL}