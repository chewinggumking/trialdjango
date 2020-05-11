from django.contrib import admin

from .models import BillDetails, FlatBill, Receipt

admin.site.register([BillDetails, FlatBill, Receipt])

# Register your models here.
