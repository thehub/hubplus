from django import forms
from profiles.models import Profile, HostInfo
from apps.plus_lib.utils import HTMLField
from django.conf import settings
from apps.plus_groups.models import TgGroup


class ProfileInfoForm(forms.Form):
    #organization,role,location, hub
    organisation = forms.CharField(max_length=100)
    role = forms.CharField(max_length=100)
    location = forms.CharField(max_length=100)
    hub = forms.CharField(max_length=100)
  
class ProfileAboutForm(forms.Form):
    pass

class ProfileHostInfoForm(forms.Form) :
    pass


class ProfileForm(forms.ModelForm):
    about = HTMLField()
    email_address = forms.EmailField(max_length=100)
    name = forms.CharField(max_length=100)
    #display_name = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    organisation = forms.CharField(max_length=100)
    role = forms.CharField(max_length=100)
    mobile = forms.CharField(max_length=100, required=False)
    home = forms.CharField(max_length=100, required=False)
    work = forms.CharField(max_length=100, required=False)
    fax = forms.CharField(max_length=100,required=False)
    post_or_zip = forms.CharField(max_length=20, required=False)

    email2 = forms.EmailField(max_length=100, required=False)
    address = forms.CharField(max_length=100)
    skype_id = forms.CharField(max_length=100, required=False)
    sip_id = forms.CharField(max_length=100, required=False)
    website = forms.URLField(required=False)
    homeplace = forms.CharField(max_length=100)
    homehub = forms.ModelChoiceField(queryset=TgGroup.objects.filter(level='member'),required=False)
    place = forms.CharField(max_length=100)

    def clean_homehub(self) :
        hs = TgGroup.objects.filter(self.cleaned_data['homehub'])
        if not hs :
            raise forms.ValidationError(_('Not a valid %(hub_name)s')%settings.HUB_NAME)
        return hs[0]

class HostInfoForm(forms.ModelForm) :
    class Meta:
        model = HostInfo
