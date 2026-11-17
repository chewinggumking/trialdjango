from django.urls import path
from .views import (
    home_view,
    add_view,
    edit_view,
    delete_view,
    flat_view,
    add_flat_view,
    FlatDetailView,
    toggle_rental_status,
    add_vehicle,
    delete_vehicle,
)

urlpatterns = [
    path('', home_view, name="home"),
    path('flats', flat_view, name="all_flats_noslash"),
    path('flats/', flat_view, name="all_flats"),
    path('flats/add/', add_flat_view, name="add_flats"),
    path('flats/<slug:slug>/', FlatDetailView.as_view(), name="flat_detail"),
    path('flats/<slug:slug>', FlatDetailView.as_view(), name="flat_detail_noslash"),
    path('flats/<slug:slug>/toggle-rental/', toggle_rental_status, name="toggle_rental"),
    path('flats/<slug:slug>/add-vehicle/', add_vehicle, name="add_vehicle"),
    path('vehicles/<int:pk>/delete/', delete_vehicle, name="delete_vehicle"),
    path('add/', add_view, name="add_member"),
    path('edit/<int:pk>/', edit_view, name="edit_slash"),
    path('edit/<int:pk>', edit_view, name="edit"),
    path('delete/<int:pk>/', delete_view, name="delete_slash"),
    path('delete/<int:pk>', delete_view, name="delete"),
]