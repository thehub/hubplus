from django import forms
from profiles.models import Profile, HostInfo
from apps.plus_lib.utils import HTMLField


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
    mobile = forms.CharField(max_length=100)
    home = forms.CharField(max_length=100)
    work = forms.CharField(max_length=100)
    fax = forms.CharField(max_length=100)

    email2 = forms.EmailField(max_length=100)
    address = forms.CharField(max_length=100)
    skype_id = forms.CharField(max_length=100)
    sip_id = forms.CharField(max_length=100)
    website = forms.URLField(required=False)
    homeplace = forms.CharField(max_length=100)
    place = forms.CharField(max_length=100)

class HostInfoForm(forms.ModelForm) :
    class Meta:
        model = HostInfo
