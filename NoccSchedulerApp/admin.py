from django.contrib import admin

from .models import Tour, Location, Availability, NoccRepresentatives

admin.site.register(Tour)
admin.site.register(Location)
admin.site.register(Availability)
admin.site.register(NoccRepresentatives)