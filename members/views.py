from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView

from .models import Guest, Flat
from .forms import GuestForm, FlatForm


# Create your views here.
def home_view(request):
    guests = Guest.objects.all().order_by("flat_number")
    # guests = Guest.objects.all().order_by("first_name")
    context = {
        'guests' : guests
    }
    return render(request, "home_view.html", context)

def add_view(request):
    form = GuestForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('home')    
    context = {
        'form' : form
    }
    return render(request, "addguest.html", context)

def edit_view(request, pk):
    guest_obj = Guest.objects.get(id = pk)
    form = GuestForm(request.POST or None, instance = guest_obj)
    if form.is_valid():
        form.save()
        return redirect('home')   
    context = {
        'form' : form
    }
    return render(request, "editguest.html", context)

def delete_view(request, pk):
    obj_to_delete = Guest.objects.get(id =pk)
    obj_to_delete.delete()
    return redirect('home')
    

def flat_view(request):
    flat_list = Flat.objects.all().order_by('wing').order_by('flat_number')
    context = {'flat_list': flat_list}
    return render(request, 'flat_view.html', context)

def add_flat_view(request):
    form = FlatForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('all_flats')
    context = {'form' : form}
    return render (request, 'add_flat.html', context)
 

# def flat_detail(request, slug):
#      flat = None
#      return render (request, "flat_detail.html", {"flat":flat})


class FlatDetailView(DetailView):
    model = Flat
    template = "/templates/flat_detail1.html"
        

