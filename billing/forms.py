from django import forms
from .models import FlatBill, Receipt
from members.forms import BootstrapFormMixin


class ReceiptForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Receipt
        exclude = ['related_bill']
        widgets = {
            'paid_on': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class FlatBillForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = FlatBill
        fields = ['is_paid']