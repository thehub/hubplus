from django import forms
from apps.plus_lib.utils import HTMLField

class EditWikiForm(forms.Form):
    title = forms.CharField(max_length=100)
    license = forms.CharField(max_length=100, required=False)
    content = HTMLField()
    changes = forms.CharField(required=False)
