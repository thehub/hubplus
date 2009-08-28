from django import forms

from django.contrib.auth.models import User
from plus_contacts.models import Contact, Application
from plus_permissions.default_agents import get_site, get_admin_user
from django.utils.translation import ugettext, ugettext_lazy as _


class InviteForm(forms.Form):
    
    username = forms.CharField(label=_("Their name"), max_length=30, widget=forms.TextInput())
    email_address = forms.EmailField(label=_("Email (required)"), required=True, widget=forms.TextInput())

    #message = forms.CharField(label=_("Invite Message"), widget=forms.TextInput())
    group = forms.CharField(label=_("A specific group you'd like to invite them to (Optional)"), required=False)


