
from django import forms
from django.contrib.auth.models import User
from apps.plus_groups.forms import validate_name_url
from apps.plus_groups.models import name_from_title
from apps.plus_resources.models import Resource


licenses = (('',''),
            ('',''))


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=60)
    resource  = forms.FileField(required=False)
    description = forms.CharField(required=True)
    license = forms.CharField(required=False)
    author = forms.CharField(required=False) # copyright purposes

    def clean(self):
        obj = self.data['obj']        

        if not self.cleaned_data['resource'] and not obj.resource:
            self._errors['resource'] = "You must upload a file"

        self.cleaned_data['name'] = name_from_title(self.cleaned_data['title'])
        # should use validate_name_url from plus_groups form
        if self.cleaned_data['name'] != obj.name:
            try:
                Resource.objects.get(name=self.cleaned_data['name'], in_agent=obj.in_agent)
                self._errors['title'] = 'An Upload with the name/url %s already exists in %s' %(self.cleaned_data['name'], obj.in_agent.obj.display_name) 
            except Resource.DoesNotExist:
                pass
        return self.cleaned_data
    
