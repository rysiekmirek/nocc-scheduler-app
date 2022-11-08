from .models import Tour, Location
from django.forms import ModelForm, DateTimeInput, TextInput, Textarea, RadioSelect, CharField, ChoiceField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date


class TourForm(ModelForm):

    TIME_SLOTS = (
        ('7:00 - 8:00', '7:00 - 8:00'),
        ('9:00 - 10:00', '9:00 - 10:00'),
        ('11:00 - 12:00', '11:00 - 12:00'),
        ('13:00 - 14:00', '13:00 - 14:00'),
        )
    
    time_slot_selection = ChoiceField(label='Time slot selection', choices=TIME_SLOTS)

    class Meta:
        model = Tour
        #fields = '__all__'
        exclude = ('id','status','nocc_person_assigned','feedback', 'tour_name', 'start_time', 'end_time' )
        widgets = {
            'date': DateTimeInput(attrs={'type': 'date'}),
            'start_time': DateTimeInput(attrs={'type': 'time', 'min':'7:00','max': '19:00', "step": "900", 'type': 'hidden'}),
            'end_time': DateTimeInput(attrs={'type': 'time', 'type': 'hidden'}),
            'comment': Textarea(attrs={'rows':1, 'cols':50}),
            'attendees_guests': TextInput(attrs={'min':0,'max': '50','type': 'number'}),
            'attendees_akamai': TextInput(attrs={'min':0,'max': '50','type': 'number'})
        }
    def __init__(self, *args, **kwargs):
        super(TourForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control form-control-sm',
                'placeholder': field.label,
                })
"""
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        location = cleaned_data.get('location')
        today = date.today()
        #if start_time >= end_time:
        #    self.add_error('end_time', ValidationError(_('End time has to be after start time')))
        if date <= today:
            self.add_error('date', ValidationError(_('Tour cannot be scheduled for the same day or in the past')))
        for existing_tour in Tour.objects.filter(location=location):
            if date == existing_tour.date and existing_tour.status != "Rejected":
                if existing_tour.start_time <= start_time <= existing_tour.end_time:
                    raise ValidationError(
                        {'start_time': _("Start time colides with an exising tour")})
                if existing_tour.start_time <= end_time <= existing_tour.end_time:
                    raise ValidationError(
                        {'end_time': _("End time colides with an exising tour")})
                if start_time <= existing_tour.start_time and end_time >= existing_tour.end_time:
                    raise ValidationError({
                        'start_time': ValidationError(_('Tour can\'t overlap existing tour')),
                        'end_time': ValidationError(_('Tour can\'t overlap existing tour'))})

"""

class TourFormEdit(ModelForm):
    class Meta:
        model = Tour
        #fields = '__all__'
        exclude = ('feedback','status')
        widgets = {
          'comment': Textarea(attrs={'rows':1, 'cols':50}),
          #'feedback': Textarea(attrs={'rows':1, 'cols':50, 'readonly': 'readonly'}),
          'id': TextInput(attrs={'readonly': 'readonly'}),
          'status': RadioSelect(),
        }
    def __init__(self, *args, **kwargs):
        super(TourFormEdit, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():   
            field.widget.attrs.update({
                'class': 'form-control form-control-sm',
                'placeholder': field.label,
                })
