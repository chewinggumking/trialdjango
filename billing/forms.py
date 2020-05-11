from django.forms import ModelForm

from .models import  FlatBill, Receipt

class ReceiptForm (ModelForm):
    class Meta:
        model = Receipt
        # fields = '__all__'
        exclude = ['related_bill']
        # fields = ['paid_on','payment_mode', 'drawn_on', 'transaction_no', 'received_amount']


class FlatBillForm(ModelForm):
    class Meta:
        model = FlatBill
        fields = ['is_paid']