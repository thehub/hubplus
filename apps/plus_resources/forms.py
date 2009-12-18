
from django import forms
from django.contrib.auth.models import User
from apps.plus_groups.forms import validate_name_url
from apps.plus_lib.utils import title_to_name
from apps.plus_resources.models import Resource


licenses = (('',''),
            ('',''))


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=60)
    resource  = forms.FileField(required=False)
    description = forms.CharField(required=True)
    license = forms.CharField(required=False)
    author = forms.CharField(required=False) # copyright purposes

    new_parent_group = forms.CharField(required=False) 

    def __init__(self, *args, **kwargs) :
        if kwargs.has_key('user') :
            self.user = kwargs['user']
            del kwargs['user']
        super(UploadFileForm, self).__init__(*args,**kwargs)


    def clean_new_parent_group(self) :
        # allows the resource to be moved to a new parent
        # assuming that the group_id is submitted.
        # why id? because group_name is just as abstract for the user.
        # and group display name is not necessarily unique
        parent_id = self.data['new_parent_group']
        if parent_id :
            groups = TgGroup.objects.plus_filter(user=self.user, id=parent_id)
            if groups :
                self.cleaned_data['new_parent_group'] = groups[0]
            else :
                raise forms.ValidationError(_("There is no group with the id you submitted."))
        return self.cleaned_data['new_parent_group']
        
    def clean(self):
        obj = self.data['obj']        

        if not self.cleaned_data['resource'] and not obj.resource:
            self._errors['resource'] = "You must upload a file"

        self.cleaned_data['name'] = title_to_name(self.data['title'])
        # should use validate_name_url from plus_groups form

        if self.cleaned_data['name'] != obj.name:
            rs = Resource.objects.filter(name=self.cleaned_data['name'], in_agent=obj.in_agent)
            if rs :
                if rs[0].id != obj.id :
                    self._errors['title'] = 'An Upload with the name/url %s already exists in %s' %(self.cleaned_data['name'], obj.in_agent.obj.display_name) 
        return self.cleaned_data
    
