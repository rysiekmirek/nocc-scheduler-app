from .models import Tour
from django.forms import ModelForm, DateTimeInput, TextInput, Textarea, RadioSelect
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML


class TourForm(ModelForm):
    class Meta:
        model = Tour
        #fields = '__all__'
        exclude = ('id','status','nocc_person_assigned','feedback', 'tour_name')
        widgets = {
            'date': DateTimeInput(attrs={'type': 'date'}),
            'start_time': DateTimeInput(attrs={'type': 'time'}),
            'end_time': DateTimeInput(attrs={'type': 'time'}),
            'comment': Textarea(attrs={'rows':1, 'cols':50}),
            'attendees_guests': TextInput(attrs={'min':0,'max': '50','type': 'number'}),
            'attendees_akamai': TextInput(attrs={'min':0,'max': '50','type': 'number'})
        }
    def __init__(self, *args, **kwargs):
        super(TourForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            Fieldset(
                'Basic information',
                'requestor_name',
                'requestor_email',
            ),
            Fieldset(
                'Point of Contact',
                HTML('<span> The Point of Contact is the person who is responsible for this group from within Akamai and will escort them to the NOCC </span>'),
                'poc_name',
                'poc_email',
                'cc_this_request_to',
                HTML('<span>Division</span>'),
                'division',
            ),
             Fieldset(
                'Visit Details',
                HTML('<span>Location</span>'),
                'location',
                HTML('<span>Date</span>'),
                'date',
                HTML('<span>Start time</span>'),
                'start_time',
                HTML('<span>End time</span>'),
                'end_time',
                HTML('<span>NOCC personnel required?</span>'),
                'nocc_personnel_required',
            ),
            Fieldset(
                'Visitors Details',
                HTML('<span>Category</span>'),
                'category',
                HTML('<span>Atendees - Akamai</span>'),
                'attendees_akamai',
                HTML('<span>Atendees - Guest</span>'),
                'attendees_guests',
                HTML('<span>Current customer?</span>'),
                'current_customer',
                'customer_name',
            ),
            Fieldset(
                '',
                'comment',
            ),
            Submit('submit', 'Submit', css_class='button white'),
        )

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
        if start_time >= end_time:
            self.add_error('end_time', ValidationError(_('End time has to be after start time')))
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
