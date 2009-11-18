from django import forms
from apps.plus_lib.utils import HTMLField
from apps.plus_groups.forms import validate_name_url
from apps.plus_groups.models import name_from_title
from apps.plus_wiki.models import WikiPage


class EditWikiForm(forms.Form):
    title = forms.CharField(max_length=100)
    license = forms.CharField(max_length=100, required=False)
    content = HTMLField()
    what_changed = forms.CharField(required=False)
    author = forms.CharField(required=False) # copyright purposes

    # not from the original request.POST dict
    in_agent = forms.IntegerField
    

    def clean(self):
        obj = self.data['obj']
        if self._errors:
            return self.cleaned_data

        # should use validate_name_url from plus_groups form
        self.cleaned_data['name'] = name_from_title(self.cleaned_data['title'])
        if self.cleaned_data['name'] != obj.name:
            try:
                WikiPage.objects.get(name=self.cleaned_data['name'], in_agent=obj.in_agent)
                self._errors['title'] = 'A Page with the name/url %s already exists in %s' %(self.cleaned_data['name'], obj.in_agent.obj.display_name) 
            except WikiPage.DoesNotExist:
                pass
        return self.cleaned_data

