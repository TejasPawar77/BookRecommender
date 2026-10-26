from django import forms

class RegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True
    )