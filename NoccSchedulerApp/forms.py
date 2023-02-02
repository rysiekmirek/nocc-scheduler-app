from .models import Tour, Location, Availability, NoccRepresentatives
from django.forms import ModelForm, DateTimeInput, TextInput, Textarea, RadioSelect, CharField, ChoiceField, TimeField, DateTimeField, DateInput
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta, datetime
import pytz

class TourForm(ModelForm):

    class Meta:
        model = Tour
        #fields = '__all__'
        exclude = ('id','status','nocc_person_assigned','feedback', 'tour_name', 'feedback_status')
        widgets = {
            'date': DateInput(format=('%Y-%m-%d'),attrs={'type': 'date', 'min': (date.today())}),
            'comment': Textarea(attrs={'rows':1, 'cols':50}),
            'attendees_guests': TextInput(attrs={'min':0,'max': '50','type': 'number'}),
            'attendees_akamai': TextInput(attrs={'min':0,'max': '50','type': 'number'}),
        }

    def __init__(self, *args, **kwargs):
        super(TourForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control form-control-sm',
                'placeholder': field.label,
                })
                
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        location = cleaned_data.get('location')
        today = date.today()
        now_with_date = datetime.now()
        if start_time >= end_time:
            self.add_error('end_time', ValidationError(_('End time has to be after start time')))
        if date < today:
            self.add_error('date', ValidationError(_('Tour cannot be scheduled in the past')))
        if date == today:
            if location == 'Krakow':
                timezone = pytz.timezone('Europe/Warsaw')
            elif location == 'Bangalore':
                timezone = pytz.timezone('Asia/Calcutta')
            else:
                timezone = pytz.timezone('America/New_York')

            local_now = now_with_date.astimezone(timezone).time()

            if start_time <= local_now:
                self.add_error('start_time', ValidationError(_('Tour cannot start in the past')))

        for existing_tour in Tour.objects.filter(location=location).exclude(status="Rejected").exclude(status="Canceled"):
            if date == existing_tour.date:
                if existing_tour.start_time <= start_time < existing_tour.end_time:
                    raise ValidationError(
                        {'start_time': _("Start time colides with an exising tour")})
                if existing_tour.start_time < end_time <= existing_tour.end_time:
                    raise ValidationError(
                        {'end_time': _("End time colides with an exising tour")})
                if start_time <= existing_tour.start_time and end_time >= existing_tour.end_time:
                    raise ValidationError({
                        'start_time': ValidationError(_('Tour cant overlap existing tour')),
                        'end_time': ValidationError(_('Tour cant overlap existing tour'))})
    


class TourFormFeedback(ModelForm):
    class Meta:
        model = Tour
        fields = ['satisfaction', 'key_take_aways', 'overall_feedback', 'internal_or_external_audience', 'feedback_name', 'sessions_welcoming', 
        'sessions_speaker', 'sessions_walls_displays', 'sessions_daily_work', 'sessions_scheduling_arrangement', 'feedback_status']
        #exclude = ('id','status','nocc_person_assigned','feedback', 'tour_name', 'start_time', 'end_time', 'requestor_name' )
        widgets = {
            'key_take_aways': TextInput,
            'overall_feedback' : TextInput,
            'internal_or_external_audience': TextInput,
            'feedback_name' : TextInput,
        }

    def __init__(self, *args, **kwargs):
        super(TourFormFeedback, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control form-control-sm',
                'placeholder': field.label,
                })


class TourFormFeedbackDetails(ModelForm):
    class Meta:
        model = Tour
        fields = ['satisfaction', 'key_take_aways', 'overall_feedback', 'internal_or_external_audience', 'feedback_name', 'sessions_welcoming', 
        'sessions_speaker', 'sessions_walls_displays', 'sessions_daily_work', 'sessions_scheduling_arrangement']
        #exclude = ('id','status','nocc_person_assigned','feedback', 'tour_name', 'start_time', 'end_time', 'requestor_name' )
        widgets = {
            'key_take_aways': TextInput,
            'overall_feedback' : TextInput,
            'internal_or_external_audience': TextInput,
            'feedback_name' : TextInput,
        }

    def __init__(self, *args, **kwargs):
        super(TourFormFeedbackDetails, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control form-control-sm',
                'placeholder': field.label,
                })
            field.disabled = True


class TourFormDetails(ModelForm):
    class Meta:
        model = Tour
        #fields = '__all__'
        exclude = ('feedback','status', 'satisfaction', 'key_take_aways', 'overall_feedback', 'internal_or_external_audience', 'feedback_name', 'sessions_welcoming', 
        'sessions_speaker', 'sessions_walls_displays', 'sessions_daily_work', 'sessions_scheduling_arrangement','feedback_status')
        widgets = {
            'start_time': TextInput(attrs={'readonly': 'readonly'}),
            'end_time': TextInput(attrs={'readonly': 'readonly'}),
            'location': TextInput(attrs={'readonly': 'readonly'}),
            'comment': Textarea(attrs={'rows':1, 'cols':50}),
            'id': TextInput(attrs={'readonly': 'readonly'}),
            'status': RadioSelect(),
        }
    def __init__(self, *args, **kwargs):
        super(TourFormDetails, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():   
            field.widget.attrs.update({
                'class': 'form-control form-control-sm',
                'placeholder': field.label,
                })
            if name not in ['tour_name', 'customer_or_group_name', 'nocc_person_assigned']:
                field.disabled = True




class AvailabilityForm(ModelForm):
    class Meta:
        model = Availability
        fields = '__all__'
        widgets = {
            'avail_date': DateTimeInput(attrs={'type': 'date', 'min': (date.today() + timedelta(days=1)) }),
            'avail_time': Textarea(attrs={'rows':1, 'cols':50}),
        }
    
    def __init__(self, *args, **kwargs):
        super(AvailabilityForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control form-control-sm',
                'placeholder': field.label,
                })