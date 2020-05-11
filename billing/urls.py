from django.urls import path

from .views import (bill_costing,
                    bill_sorter,
                    bill_listing,
                    bill_view,
                    bill_paid,
                    create_receipt
                    )

urlpatterns = [
    path('', bill_costing, name = "bill-costing"),
    path('create_bills/', bill_sorter, name = "create_bills"),
    path('create_receipt/<int:bill_id>/', create_receipt, name = "create_receipt"),
    path('bill_list/', bill_listing, name = "bill_list"),
    path('bill_view/<int:id>/', bill_view, name = "bill_view"),
    path('bill_paid/<int:id>/<str:status>', bill_paid, name = "bill_paid"),
]