from .models import Tour
from django.forms import ModelForm, DateTimeInput, TextInput, Textarea


class TourForm(ModelForm):
    class Meta:
        model = Tour
        #fields = '__all__'
        exclude = ('id','approved','nocc_person_assigned','feedback')
        widgets = {
            'date': DateTimeInput(attrs={'type': 'date'}),
            'start_time': DateTimeInput(attrs={'type': 'time'}),
            'end_time': DateTimeInput(attrs={'type': 'time'}),
            'comment': Textarea(attrs={'rows':1, 'cols':50}),
        }

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