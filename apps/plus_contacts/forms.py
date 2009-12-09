from django import forms

from django.contrib.auth.models import User
from plus_contacts.models import Contact, Application
from plus_permissions.default_agents import get_site, get_admin_user
from django.utils.translation import ugettext, ugettext_lazy as _
from apps.plus_groups.models import TgGroup
import re

alnum_re = re.compile(r'^[\w\s]+$')

class InviteForm(forms.Form):
    first_name = forms.RegexField(regex=alnum_re, label=_("First Name"), max_length=30, widget=forms.TextInput(), error_messages={'invalid': 'Name must only contain alphabetic character'})
    last_name = forms.RegexField(regex=alnum_re, label=_("Last Name"), max_length=30, widget=forms.TextInput(), error_messages={'invalid': 'Name must only contain alphabetic character'})
    email_address = forms.EmailField(label=_("Email (required)"), required=True, widget=forms.TextInput())
    message = forms.CharField(label=_("Invite Message"), required=True, widget=forms.TextInput())
    group = forms.CharField(label=_("A specific group you'd like to invite them to (Optional)"), required=False)

    
    def clean_email_address(self):
        email_address = self.cleaned_data['email_address']
        if User.objects.filter(email_address=email_address) :
            raise forms.ValidationError(_("We already have a user with that email address."))
        return self.cleaned_data['email_address']


    def clean_group(self):
        # turn group id into actual object
        group = self.cleaned_data['group']
        if not group:
            return None

        if TgGroup.objects.filter(group_name=group):
            return TgGroup.objects.get(group_name=group)
        raise forms.ValidationError(_("There is no group with a group_name %s" % group))
