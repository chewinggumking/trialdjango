from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from .models import Guest, Flat, RentalStatus, Vehicle
from .forms import GuestForm, FlatForm, VehicleForm


def home_view(request):
    q = request.GET.get('q', '').strip()
    guests = Guest.objects.select_related('flat_number').all().order_by("flat_number__wing", "flat_number__flat_number")
    
    if q:
        guests = guests.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(mobile__icontains=q) |
            Q(flat_number__flat_number__icontains=q) |
            Q(flat_number__wing__icontains=q)
        )
    
    context = {
        'guests': guests,
        'q': q,
    }
    
    if request.htmx:
        return render(request, "members/partials/guest_rows.html", context)
    return render(request, "home_view.html", context)


def add_view(request):
    form = GuestForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('home')
    context = {
        'form': form
    }
    return render(request, "addguest.html", context)


def edit_view(request, pk):
    guest_obj = get_object_or_404(Guest, id=pk)
    form = GuestForm(request.POST or None, instance=guest_obj)
    if form.is_valid():
        form.save()
        return redirect('home')
    context = {
        'form': form,
        'guest': guest_obj
    }
    return render(request, "editguest.html", context)


def delete_view(request, pk):
    obj_to_delete = get_object_or_404(Guest, id=pk)
    if request.method in ["DELETE", "POST"]:
        obj_to_delete.delete()
        if request.htmx:
            return HttpResponse("")
        return redirect('home')
    # If GET request, show confirmation or delete
    obj_to_delete.delete()
    return redirect('home')


def flat_view(request):
    q = request.GET.get('q', '').strip()
    wing = request.GET.get('wing', '').strip()
    status = request.GET.get('status', '').strip()

    flat_list = Flat.objects.select_related('guest', 'rentalstatus').prefetch_related('vehicle_set').all().order_by('wing', 'flat_number')

    if q:
        flat_list = flat_list.filter(
            Q(flat_number__icontains=q) |
            Q(wing__icontains=q) |
            Q(guest__first_name__icontains=q) |
            Q(guest__last_name__icontains=q)
        )
    if wing:
        flat_list = flat_list.filter(wing=wing)
    if status == 'rented':
        flat_list = flat_list.filter(rentalstatus__is_rented=True)
    elif status == 'owner':
        flat_list = flat_list.filter(Q(rentalstatus__is_rented=False) | Q(rentalstatus__isnull=True))

    wings = Flat.objects.values_list('wing', flat=True).distinct().order_by('wing')

    context = {
        'flat_list': flat_list,
        'wings': wings,
        'selected_wing': wing,
        'selected_status': status,
        'q': q,
    }

    if request.htmx:
        return render(request, 'members/partials/flat_cards.html', context)
    return render(request, 'flat_view.html', context)


def add_flat_view(request):
    form = FlatForm(request.POST or None)
    if form.is_valid():
        flat = form.save()
        RentalStatus.objects.get_or_create(flat_number=flat)
        return redirect('all_flats')
    context = {'form': form}
    return render(request, 'add_flat.html', context)


def flat_detail_view(request, slug):
    flat = get_object_or_404(Flat, slug=slug)
    rental_status, _ = RentalStatus.objects.get_or_create(flat_number=flat)
    vehicles = flat.vehicle_set.all()
    bills = flat.flatbill_set.all().order_by('-bill_date', '-id')
    vehicle_form = VehicleForm()

    context = {
        'flat': flat,
        'rental_status': rental_status,
        'vehicles': vehicles,
        'bills': bills,
        'vehicle_form': vehicle_form,
    }
    return render(request, 'members/flat_detail.html', context)


class FlatDetailView(View):
    def get(self, request, slug, *args, **kwargs):
        return flat_detail_view(request, slug)


def toggle_rental_status(request, slug):
    if request.method == "POST":
        flat = get_object_or_404(Flat, slug=slug)
        rental_status, _ = RentalStatus.objects.get_or_create(flat_number=flat)
        rental_status.is_rented = not rental_status.is_rented
        rental_status.save()
        return render(request, 'members/partials/rental_status_card.html', {
            'flat': flat,
            'rental_status': rental_status
        })
    return HttpResponse(status=405)


def add_vehicle(request, slug):
    flat = get_object_or_404(Flat, slug=slug)
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.flat = flat
            vehicle.save()
        vehicles = flat.vehicle_set.all()
        return render(request, 'members/partials/vehicle_list.html', {
            'flat': flat,
            'vehicles': vehicles,
            'vehicle_form': VehicleForm()
        })
    return HttpResponse(status=405)


def delete_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, id=pk)
    flat = vehicle.flat
    if request.method in ["DELETE", "POST"]:
        vehicle.delete()
        if request.htmx:
            return HttpResponse("")
        return redirect(flat.get_absolute_url())
    return HttpResponse(status=405)
