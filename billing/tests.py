from datetime import date
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse

from .models import BillDetails, FlatBill, Receipt
from members.models import Flat, RentalStatus


class BillingModelTests(TestCase):
    def setUp(self):
        self.flat = Flat.objects.create(flat_number="201", wing="B")
        self.bill_details = BillDetails.objects.create(
            flat_type="1",
            municipal_tax=Decimal("500.00"),
            maintenance=Decimal("1500.00"),
            water_charges=Decimal("300.00"),
            parking_charges=Decimal("200.00"),
            sinking_fund=Decimal("250.00"),
            building_repair=Decimal("200.00"),
            elec_ins_chgs=Decimal("150.00")
        )

    def test_maintenance_total(self):
        # 1500 + 300 + 200 + 250 + 200 + 150 = 2600.00
        self.assertEqual(self.bill_details.maintenance_total(), Decimal("2600.00"))

    def test_flat_bill_total(self):
        bill = FlatBill.objects.create(
            flat_name=self.flat,
            municipal_tax=Decimal("500.00"),
            maintenance=Decimal("1500.00"),
            water_charges=Decimal("300.00"),
            parking_charges=Decimal("200.00"),
            sinking_fund=Decimal("250.00"),
            building_repair=Decimal("200.00"),
            elec_ins_chgs=Decimal("150.00"),
            noc_charges=Decimal("0.00"),
            add_item_amt_1=Decimal("0.00"),
            add_item_amt_2=Decimal("0.00")
        )
        self.assertEqual(bill.total(), Decimal("3100.00"))


class BillingViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.flat = Flat.objects.create(flat_number="101", wing="A")
        RentalStatus.objects.create(flat_number=self.flat, is_rented=False)
        self.bill = FlatBill.objects.create(
            flat_name=self.flat,
            municipal_tax=Decimal("500.00"),
            maintenance=Decimal("1500.00"),
            water_charges=Decimal("300.00"),
            parking_charges=Decimal("200.00"),
            sinking_fund=Decimal("250.00"),
            building_repair=Decimal("200.00"),
            elec_ins_chgs=Decimal("150.00"),
            noc_charges=Decimal("0.00"),
            add_item_amt_1=Decimal("0.00"),
            add_item_amt_2=Decimal("0.00")
        )
        self.bill_details = BillDetails.objects.create(
            flat_type="1",
            municipal_tax=Decimal("500.00"),
            maintenance=Decimal("1500.00"),
            water_charges=Decimal("300.00"),
            parking_charges=Decimal("200.00"),
            sinking_fund=Decimal("250.00"),
            building_repair=Decimal("200.00"),
            elec_ins_chgs=Decimal("150.00")
        )

    def test_bill_costing_view(self):
        response = self.client.get(reverse('bill-costing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Flat Type 1")

    def test_bill_listing_view_standard(self):
        response = self.client.get(reverse('bill_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Flat 101 A")
        self.assertContains(response, "Maintenance Bills")

    def test_bill_listing_view_htmx_filter(self):
        response = self.client.get(
            reverse('bill_list') + "?status=outstanding",
            headers={"HX-Request": "true"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "billing/partials/bill_rows.html")
        self.assertContains(response, "Outstanding")

    def test_bill_view(self):
        response = self.client.get(reverse('bill_view', kwargs={'id': self.bill.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Municipal Tax")
        self.assertContains(response, "Flat 101")

    def test_bill_paid_htmx(self):
        self.assertFalse(self.bill.is_paid)
        response = self.client.post(
            reverse('bill_paid', kwargs={'id': self.bill.id, 'status': 'paid'}),
            headers={"HX-Request": "true", "HX-Target": "bill-row-" + str(self.bill.id)}
        )
        self.assertEqual(response.status_code, 200)
        self.bill.refresh_from_db()
        self.assertTrue(self.bill.is_paid)
        self.assertFalse(Receipt.objects.filter(related_bill=self.bill).exists())
        self.assertContains(response, "Paid")

        # Toggle back to unpaid
        response = self.client.post(
            reverse('bill_paid', kwargs={'id': self.bill.id, 'status': 'unpaid'}),
            headers={"HX-Request": "true", "HX-Target": "bill-row-" + str(self.bill.id)}
        )
        self.assertEqual(response.status_code, 200)
        self.bill.refresh_from_db()
        self.assertFalse(self.bill.is_paid)
        self.assertContains(response, "Outstanding")

    def test_bill_paid_badge_htmx(self):
        response = self.client.post(
            reverse('bill_paid', kwargs={'id': self.bill.id, 'status': 'paid'}),
            headers={"HX-Request": "true", "HX-Target": "bill-status-badge"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "billing/partials/bill_status_badge.html")
        self.bill.refresh_from_db()
        self.assertTrue(self.bill.is_paid)
        self.assertContains(response, 'checked')

    def test_create_receipt_modal_htmx_list(self):
        get_resp = self.client.get(
            reverse('create_receipt', kwargs={'bill_id': self.bill.id}) + "?modal=1&source=list",
            headers={"HX-Request": "true"}
        )
        self.assertEqual(get_resp.status_code, 200)
        self.assertTemplateUsed(get_resp, "billing/partials/receipt_modal.html")

        receipt_data = {
            'paid_on': '2026-11-26',
            'payment_mode': 'UPI',
            'drawn_on': 'ICICI Bank',
            'transaction_no': 'UPI987654',
            'received_amount': '3100.00'
        }
        post_resp = self.client.post(
            reverse('create_receipt', kwargs={'bill_id': self.bill.id}) + "?modal=1&source=list",
            data=receipt_data,
            headers={"HX-Request": "true"}
        )
        self.assertEqual(post_resp.status_code, 200)
        self.assertTemplateUsed(post_resp, "billing/partials/receipt_modal_success.html")
        self.bill.refresh_from_db()
        self.assertTrue(self.bill.is_paid)
        self.assertEqual(self.bill.receipt.transaction_no, 'UPI987654')
        self.assertContains(post_resp, 'hx-swap-oob="outerHTML"')
        self.assertContains(post_resp, f'id="bill-row-{self.bill.id}"')

    def test_unpaid_modal_keep_and_delete_receipt(self):
        Receipt.objects.create(
            related_bill=self.bill,
            paid_on=date(2026, 11, 26),
            payment_mode='UPI',
            drawn_on='HDFC Bank',
            transaction_no='UPI001',
            received_amount=Decimal('3100.00'),
        )
        self.bill.is_paid = True
        self.bill.save()

        # GET modal prompt
        modal_resp = self.client.get(
            reverse('bill_paid', kwargs={'id': self.bill.id, 'status': 'unpaid'}) + "?modal=1&source=list",
            headers={"HX-Request": "true"}
        )
        self.assertEqual(modal_resp.status_code, 200)
        self.assertTemplateUsed(modal_resp, "billing/partials/unpaid_confirm_modal.html")
        self.assertContains(modal_resp, "Keep Receipt")
        self.assertContains(modal_resp, "Delete Receipt")

        # Keep receipt
        keep_resp = self.client.post(
            reverse('bill_paid', kwargs={'id': self.bill.id, 'status': 'unpaid'}) + "?modal=1&source=list&receipt_action=keep",
            headers={"HX-Request": "true"}
        )
        self.assertEqual(keep_resp.status_code, 200)
        self.assertTemplateUsed(keep_resp, "billing/partials/unpaid_modal_success.html")
        self.bill.refresh_from_db()
        self.assertFalse(self.bill.is_paid)
        self.assertTrue(Receipt.objects.filter(related_bill=self.bill).exists())

        # Re-mark paid and then delete receipt
        self.bill.is_paid = True
        self.bill.save()
        del_resp = self.client.post(
            reverse('bill_paid', kwargs={'id': self.bill.id, 'status': 'unpaid'}) + "?modal=1&source=detail&receipt_action=delete",
            headers={"HX-Request": "true"}
        )
        self.assertEqual(del_resp.status_code, 200)
        self.assertTemplateUsed(del_resp, "billing/partials/unpaid_modal_success.html")
        self.bill.refresh_from_db()
        self.assertFalse(self.bill.is_paid)
        self.assertFalse(Receipt.objects.filter(related_bill=self.bill).exists())
        self.assertContains(del_resp, "Record Payment & Issue Receipt")

    def test_create_receipt_htmx(self):
        receipt_data = {
            'paid_on': '2026-11-17',
            'payment_mode': 'Cheque',
            'drawn_on': 'HDFC Bank',
            'transaction_no': 'CHQ123456',
            'received_amount': '3100.00'
        }
        response = self.client.post(
            reverse('create_receipt', kwargs={'bill_id': self.bill.id}),
            data=receipt_data,
            headers={"HX-Request": "true"}
        )
        self.assertEqual(response.status_code, 200)
        self.bill.refresh_from_db()
        self.assertTrue(self.bill.is_paid)
        self.assertTrue(hasattr(self.bill, 'receipt'))
        self.assertEqual(self.bill.receipt.transaction_no, 'CHQ123456')
        self.assertContains(response, "Receipt #")
