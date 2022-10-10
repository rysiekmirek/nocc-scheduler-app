from .models import Tour
from django.forms import ModelForm,DateTimeInput


class TourForm(ModelForm):
    class Meta:
        model = Tour
        fields = '__all__'
        widgets = {
            'date': DateTimeInput(attrs={'type': 'date'}),
            'start_time': DateTimeInput(attrs={'type': 'time'}),
            'end_time': DateTimeInput(attrs={'type': 'time'}),
        }