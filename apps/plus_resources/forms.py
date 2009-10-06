
from django import forms
from django.contrib.auth.models import User


licenses = (('',''),
            ('',''))


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    resource  = forms.FileField()

    description = forms.CharField(required=False)
    license = forms.CharField(required=False)

    author = forms.CharField(required=False)
    in_agent = forms.CharField(required=False)

    name = forms.CharField(required=True)
    


