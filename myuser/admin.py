from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import SiteUser

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget= forms.PasswordInput)
    password2 = forms.CharField(label="Password Confirmation", widget= forms.PasswordInput)

    class Meta:
        model = SiteUser
        fields = ["email", "first_name", "last_name"]

    def clean_password(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Both passwords must match.")
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = SiteUser
        fields = ["email", "password", "first_name", "last_name", "mobile", "staff", "admin", "active"]
    
    def clean_password(self):
        return self.initial["password"]
    

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    ass_form = UserCreationForm

    list_display = ["email",  "first_name", "last_name", "mobile"]
    list_filter = ["admin"]
    fieldsets = (
        (None, {"fields" : ("email", "password")}),
        ("Full Name", {"fields" : ("first_name", "last_name")}),
        ("Permissions", {"fields" : ["admin", "staff", "active"]})
    )

    add_fieldsets = (
        (None, {
            'classes': ("wide",),
            'fields': ("email", "first_name", "last_name", "mobile", "password1", "password2")}
        ),
    )
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["last_name"]
    filter_horizontal = ()


# Register your models here.
# "email", "first_name", "last_name", "mobile", "password1", "password2"
admin.site.register(SiteUser, UserAdmin)

admin.site.unregister(Group)