from django.forms import ModelForm
from .models import Guest, Flat

class GuestForm (ModelForm):
    class Meta:
        model = Guest
        fields = '__all__'
        # fields = ['first_name', 'last_name', 'mobile']

class FlatForm(ModelForm):
    class Meta:
        model = Flat
        fields =  '__all__'