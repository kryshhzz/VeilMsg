from django import forms
from .models import *

class SettingsForm(forms.ModelForm):
    class Meta :
        model = profile
        fields = ['is_open']
        labels = {
            "is_open" : "open for dms"
        }
        