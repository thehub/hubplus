from django import forms
from profiles.models import Profile, HostInfo

class ProfileInfoForm(forms.Form) :
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
    class Meta:
        model = Profile
        exclude = ('user', 'blogrss', 'timezone', 'language',
            'twitter_user', 'twitter_password')

class HostInfoForm(forms.ModelForm) :
    class Meta:
        model = HostInfo
