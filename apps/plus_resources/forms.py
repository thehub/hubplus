
from django import forms
from django.contrib.auth.models import User


licenses = (('',''),
            ('',''))



class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    resource  = forms.FileField(required=False)

    description = forms.CharField(required=False)
    license = forms.CharField(required=False)

    author = forms.CharField(required=False)
    uploader_name = forms.CharField()

    def clean_uploader_name(self) :
        username = self.cleaned_data['uploader_name']
        if User.objects.filter(username=username).count() < 1 :
            raise forms.ValidationError('Uploader must be a real user')
        self.cleaned_data['uploader'] = User.objects.get(username=username)
        return username



