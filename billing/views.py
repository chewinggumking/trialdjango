from datetime import datetime, date
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse

from .forms import ReceiptForm, FlatBillForm
from .models import BillDetails, FlatBill, Receipt
from .utilities import create_flat_bills
from members.models import Flat


def bill_costing(request):
    """Shows initial charges configured for flat types 1, 2, and 3."""
    initial_amounts = BillDetails.objects.all().order_by('flat_type')
    context = {'initial_amounts': initial_amounts}
    return render(request, 'billing/initial_bill.html', context)


def bill_sorter(request):
    """
    Generates bills for each flat for the current month/year based on
    flat_type and initial rates, avoiding duplicates.
    """
    now = datetime.now()
    error_flats = []
    created_count = 0

    flats = Flat.objects.all()
    for flat in flats:
        flat_type = flat.flat_number[2] if len(flat.flat_number) >= 3 else '1'
        bill_type = BillDetails.objects.filter(flat_type=flat_type).first() or BillDetails.objects.first()
        
        if not bill_type:
            continue

        existing = FlatBill.objects.filter(
            flat_name=flat,
            bill_date__year=now.year,
            bill_date__month=now.month
        ).exists()

        if existing:
            error_flats.append(str(flat))
        else:
            create_flat_bills(flat, bill_type)
            created_count += 1

    if error_flats:
        msg = f"Bills for {now.strftime('%B %Y')} already exist for: {', '.join(error_flats)}"
        messages.info(request, msg)
    if created_count > 0:
        messages.success(request, f"Successfully generated {created_count} new bills for {now.strftime('%B %Y')}.")

    return redirect('bill_list')


def bill_listing(request):
    """
    List all flat bills with real-time HTMX filtering by status, flat/resident search,
    and month/year.
    """
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    month = request.GET.get('month', '').strip()
    year = request.GET.get('year', '').strip()

    bills = FlatBill.objects.select_related('flat_name', 'flat_name__guest', 'receipt').all().order_by('-bill_date', '-id')

    if q:
        bills = bills.filter(
            Q(flat_name__flat_number__icontains=q) |
            Q(flat_name__wing__icontains=q) |
            Q(flat_name__guest__first_name__icontains=q) |
            Q(flat_name__guest__last_name__icontains=q)
        )

    if status == 'paid':
        bills = bills.filter(is_paid=True)
    elif status == 'outstanding':
        bills = bills.filter(is_paid=False)

    if month:
        bills = bills.filter(bill_date__month=int(month))
    if year:
        bills = bills.filter(bill_date__year=int(year))

    # Calculate summary metrics from queryset
    total_bills = list(bills)
    total_amount = sum(b.total() for b in total_bills)
    paid_amount = sum(b.total() for b in total_bills if b.is_paid)
    outstanding_amount = total_amount - paid_amount

    context = {
        'bills': bills,
        'q': q,
        'selected_status': status,
        'selected_month': month,
        'selected_year': year,
        'total_count': len(total_bills),
        'total_amount': total_amount,
        'paid_amount': paid_amount,
        'outstanding_amount': outstanding_amount,
    }

    if request.htmx:
        return render(request, 'billing/partials/bill_rows.html', context)
    return render(request, 'billing/bill_list.html', context)


def bill_view(request, id):
    """Displays detailed breakdown of a specific flat bill and receipt."""
    bill = get_object_or_404(FlatBill.objects.select_related('flat_name', 'flat_name__guest', 'receipt'), id=id)
    receipt = getattr(bill, 'receipt', None)

    receipt_form = ReceiptForm(
        request.POST or None,
        instance=receipt if receipt else None,
        initial={'received_amount': bill.total(), 'paid_on': date.today()} if not receipt else None
    )

    if request.method == 'POST' and receipt_form.is_valid():
        instance = receipt_form.save(commit=False)
        instance.related_bill = bill
        instance.save()
        bill.is_paid = True
        bill.save()
        messages.success(request, f"Receipt #{instance.id} created successfully!")
        return redirect('bill_view', id=bill.id)

    context = {
        'bill': bill,
        'receipt': receipt,
        'receipt_form': receipt_form,
    }
    return render(request, 'billing/bill_view.html', context)


def bill_paid(request, id, status="paid"):
    """
    Marks a bill as paid. If called from HTMX, returns an updated row or status badge.
    """
    bill = get_object_or_404(FlatBill, id=id)
    if request.method in ["POST", "GET"]:
        bill.is_paid = (status.lower() == "paid")
        bill.save()

        # If marking as paid and no receipt exists, auto-create a simple receipt record
        if bill.is_paid and not hasattr(bill, 'receipt'):
            Receipt.objects.create(
                related_bill=bill,
                paid_on=date.today(),
                payment_mode="Online/Bank Transfer",
                drawn_on="Direct",
                transaction_no=f"TXN-{bill.id}-{int(datetime.now().timestamp())}",
                received_amount=bill.total()
            )

        if request.htmx:
            # Check if this was called from the list table or the detail view
            target = request.htmx.target or ""
            if "badge" in target or "status" in target:
                return render(request, 'billing/partials/bill_status_badge.html', {'bill': bill})
            return render(request, 'billing/partials/bill_single_row.html', {'bill': bill})

        return HttpResponseRedirect(reverse('bill_view', kwargs={'id': id}))
    return HttpResponse(status=405)


def create_receipt(request, bill_id):
    """
    Creates or updates receipt for a bill. Supports inline HTMX modal/drawer and standard view.
    """
    bill = get_object_or_404(FlatBill, id=bill_id)
    receipt_instance = getattr(bill, 'receipt', None)
    edit = receipt_instance is not None

    if request.method == "POST":
        receipt_form = ReceiptForm(request.POST, instance=receipt_instance)
        if receipt_form.is_valid():
            receipt = receipt_form.save(commit=False)
            receipt.related_bill = bill
            bill.is_paid = True
            bill.save()
            receipt.save()

            if request.htmx:
                return render(request, 'billing/partials/receipt_section.html', {
                    'bill': bill,
                    'receipt': receipt
                })
            messages.success(request, f"Receipt #{receipt.id} recorded successfully.")
            return HttpResponseRedirect(reverse('bill_view', kwargs={'id': bill.id}))
    else:
        receipt_form = ReceiptForm(
            instance=receipt_instance,
            initial={'received_amount': bill.total(), 'paid_on': date.today()} if not edit else None
        )

    context = {
        'form': receipt_form,
        'edit': edit,
        'bill': bill
    }

    if request.htmx:
        return render(request, 'billing/partials/receipt_form_partial.html', context)
    return render(request, 'billing/receipt_form.html', context)
