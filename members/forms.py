from django import forms
from .models import Guest, Flat, Vehicle


class BootstrapFormMixin:
    """Helper mixin to automatically add Bootstrap classes to form controls."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs['class'] = 'form-select'
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = 'form-check-input'
            else:
                widget.attrs['class'] = 'form-control'


class GuestForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Guest
        fields = '__all__'


class FlatForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Flat
        fields = ['flat_number', 'wing']


class VehicleForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['vehicle', 'registration_number', 'make', 'model']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control text-uppercase',
                'placeholder': 'e.g. MH 02 AB 1234',
                'maxlength': '15',
            }),
            'make': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Make (e.g. Honda, Maruti)',
                'maxlength': '50',
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Model (e.g. City, Swift)',
                'maxlength': '50',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['registration_number'].required = True