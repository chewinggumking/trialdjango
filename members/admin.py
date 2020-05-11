from django.contrib import admin

# Register your models here.
from .models import Guest, Flat, RentalStatus, Renter, Vehicle

class RentalStatusInline(admin.TabularInline):
    model = RentalStatus


class GuestInline(admin.TabularInline):
    model = Guest

class FlatAdmin(admin.ModelAdmin):
    inlines = [GuestInline, RentalStatusInline]

admin.site.register(Guest)
admin.site.register(Renter)
admin.site.register(Flat, FlatAdmin)
admin.site.register(Vehicle)

