from datetime import datetime

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy

from .forms import ReceiptForm, FlatBillForm
from .models import BillDetails, FlatBill, Receipt
from .utilities import create_flat_bills

from members.models import Flat


def bill_costing(request):
    #''' This Function sends out a list of all flat types in a building and 
    # and then sends it to a view. The types of flats at the moment
    # are type 1,2 and 3'''
    initial_amounts = BillDetails.objects.all().order_by('flat_type')
    context = {'initial_amounts': initial_amounts}
    return render(request, 'billing/initial_bill.html', context)




def bill_sorter(request):
    #''''This function generates all the bills for each flat depending
    # on the flat type from the initial values provided to the model.
    # It uses a helper function from the utilities module
    # called create_flat_bills and takes 2 arguments.
    # flat object and a filtered BillDetails object filtered on the 3 digit
    # of the flat number. '''
    date_string = datetime.now()
    error_flats = ""
    for flat in Flat.objects.all():
        bill_type = BillDetails.objects.get(flat_type = flat.flat_number[2])
        #'''Now we will check if bill from present month for that flat is already the flat in question
        # check_bill is filtered by flat, year and month and then using exists() from django we check 
        # if the bill exists. If it does we send a message'''
        check_bill = FlatBill.objects.filter(flat_name = flat).filter(bill_date__year =date_string.year)
        if check_bill.filter(bill_date__month =date_string.month).exists():
            error_flats+= (flat.__str__() + ", ")
        else:
            create_flat_bills(flat, bill_type)
    #'''Below we check to see if our previous error checking has resulted in a string of flats.
    # If it hasn't then we don't send an error message by setting the variable to none.
    # we only send an error message variable if there is a string with error flats'''
    if not error_flats =="":
        error_message = "There already exist bills for the period of {} {} for flats ".format (date_string.strftime("%B"), date_string.year)
        error_message+= error_flats
    else:
        error_message = None
    messages.add_message(request, messages.INFO, error_message)            
    return redirect('bill_list')



def bill_listing(request):
    #''' This function just gives out a list of all the bills created so far.
    # It will soon be filtered by month and then year'''
    bills = FlatBill.objects.all()
    context = {'bills': bills}
    
    return render(request, 'billing/bill_list.html', context)

def bill_view(request, id):
        #'''This function just gives details of the bill asked for taking
    # one parameter. The bill pk or id. '''
    bill = get_object_or_404(FlatBill, id = id)
    #'''We also included the form for the receipt model and added some logic in the view template that 
    # lets you include either the receipt form if receipt does not exist or the receipt if it exists '''
    receipt_form = ReceiptForm(request.POST or None, initial={'received_amount':bill.total()})
    if receipt_form.is_valid():
        instance = receipt_form.save(commit=False)
        instance.related_bill = bill
        instance.save()
    context = {'bill':bill, 'receipt_form':receipt_form}
    return render (request, 'billing/bill_view.html', context)

def bill_paid(request, id, status):
    bill = FlatBill.objects.get(id=id)
    bill.is_paid = True
    bill.save()
    print (status)
    return HttpResponseRedirect(reverse('bill_view', kwargs = {'id':id}))


def create_receipt(request, bill_id):
    bill = FlatBill.objects.get(id=bill_id)
    edit = False
    if Receipt.objects.filter(related_bill=bill).exists():
        edit = True
        receipt_instance = bill.receipt
        print (receipt_instance)
        receipt_form = ReceiptForm(request.POST or None, instance=receipt_instance)
        if receipt_form.is_valid():
            receipt_form.save()
            return HttpResponseRedirect(reverse('bill_view', kwargs = {'id':bill.id}))
    else:
        receipt_form = ReceiptForm(request.POST or None,
                              initial = {'received_amount':bill.total() }
                              )
        if receipt_form.is_valid():
            instance = receipt_form.save(commit = False)
            instance.related_bill = bill
            bill.is_paid = True
            bill.save()
            instance.save()
            return HttpResponseRedirect(reverse('bill_view', kwargs = {'id':bill.id}))
    return render (request, 'billing/receipt_form.html', {'form': receipt_form, 'edit':edit})


