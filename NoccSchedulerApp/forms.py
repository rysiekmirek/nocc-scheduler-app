from .models import Tour
from django.forms import ModelForm


class TourForm(ModelForm):
    class Meta:
        model = Tour
        fields = '__all__'