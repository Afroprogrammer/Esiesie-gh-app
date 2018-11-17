from shitty.models import *
from django import forms


class ProFileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields ="__all__"

# class ContactForm(forms.ModelForm):
#     class Meta:
#         model = Message
#         fields = "__all__"