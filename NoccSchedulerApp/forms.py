from .models import Tour
from django.forms import ModelForm, DateTimeInput, TextInput, Textarea
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class TourForm(ModelForm):
    class Meta:
        model = Tour
        #fields = '__all__'
        exclude = ('id','status','nocc_person_assigned','feedback')
        widgets = {
            'date': DateTimeInput(attrs={'type': 'date'}),
            'start_time': DateTimeInput(attrs={'type': 'time'}),
            'end_time': DateTimeInput(attrs={'type': 'time'}),
            'comment': Textarea(attrs={'rows':1, 'cols':50}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_time >= end_time:
            self.add_error('end_time', ValidationError(
                _('End time has to be after start time')))
        for existing_tour in Tour.objects.all():
            if cleaned_data.get('date') == existing_tour.date:
                if existing_tour.start_time <= start_time <= existing_tour.end_time:
                    raise ValidationError(
                        {'start_time': _("Start time colides with an exising tour")})
                if existing_tour.start_time <= end_time <= existing_tour.end_time:
                    raise ValidationError(
                        {'end_time': _("Start time colides with an exising tour")})
                if start_time <= existing_tour.start_time and end_time >= existing_tour.end_time:
                    raise ValidationError({'start_time': ValidationError(
                        _('Tour ca\'t encompas existing tour')), 'end_time': ValidationError(
                        _('Tour ca\'t encompas existing tour'))})



class TourFormEdit(ModelForm):
    class Meta:
        model = Tour
        fields = '__all__'
        #exclude = ('id',)
        widgets = {
          'comment': Textarea(attrs={'rows':1, 'cols':50}),
          'feedback': Textarea(attrs={'rows':1, 'cols':50, 'readonly': 'readonly'}),
          'id': TextInput(attrs={'readonly': 'readonly'}),
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
                    raise ValidationError(
                        {'start_time': _("Start time colides with an exising tour", code='invalid')})
                if existing_tour.start_time <= end_time <= existing_tour.end_time:
                    raise ValidationError(
                        {'end_time': _("Start time colides with an exising tour", code='invalid')})
                if start_time <= existing_tour.start_time and end_time >= existing_tour.end_time:
                    raise ValidationError({'start_time': ValidationError(
                        _('Tour ca\'t encompas existing tour'), code='invalid'), 'end_time': ValidationError(
                        _('Tour ca\'t encompas existing tour'), code='invalid')})

