from django.urls import path
from .views import (home_view,
                    add_view,
                    edit_view,
                    delete_view,
                    flat_view,
                    add_flat_view,
                    # flat_detail,
                    FlatDetailView
                    )


urlpatterns = [
    path('', home_view, name = "home"),
    path('flats', flat_view, name = "all_flats"),
    path('flats/<slug>', FlatDetailView.as_view(), name = "flat_detail"),
    path('flats/add/', add_flat_view, name = "add_flats"),
    path('add/', add_view, name = "add_member"),
    path('edit/<int:pk>', edit_view, name = "edit"),
    path('delete/<int:pk>', delete_view, name = "delete"),
]