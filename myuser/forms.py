from django import forms


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