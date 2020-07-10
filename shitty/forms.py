from shitty.models import *
from django import forms


class ProFileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields ="__all__"


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = "__all__"


class BioServices(forms.ModelForm):
    class Meta:
        fields = "__all__"
