from .models import Tour
from django.forms import ModelForm, DateTimeInput
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class TourForm(ModelForm):
    class Meta:
        model = Tour
        #fields = '__all__'
        exclude = ('id',)
        widgets = {
            'date': DateTimeInput(attrs={'type': 'date'}),
            'start_time': DateTimeInput(attrs={'type': 'time'}),
            'end_time': DateTimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_time >= end_time:
            self.add_error('end_time', ValidationError(
                _('End time has to be after start time'), code='invalid'))
        for existing_tour in Tour.objects.all():
            if cleaned_data.get('date') == existing_tour.date:
                if existing_tour.start_time <= start_time <= existing_tour.end_time:
                    self.add_error(
                        'start_time', ValidationError(_("Start time colides with an exising tour"), code='invalid'))
                if existing_tour.start_time <= end_time <= existing_tour.end_time:
                    self.add_error(
                        'end_time', ValidationError(_("Start time colides with an exising tour"), code='invalid'))
                if start_time <= existing_tour.start_time and end_time >= existing_tour.end_time:
                    raise ValidationError({'start_time': ValidationError(
                        _('Tour can\'t encompas existing tour'), code='invalid'), 'end_time': ValidationError(
                        _('Tour can\'t encompas existing tour'), code='invalid')})
