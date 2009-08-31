from django import forms

from django.contrib.auth.models import User
from plus_contacts.models import Contact, Application
from plus_permissions.default_agents import get_site, get_admin_user
from django.utils.translation import ugettext, ugettext_lazy as _



class InviteForm(forms.Form):
    
    username = forms.CharField(label=_("Their name"), max_length=30, widget=forms.TextInput())
    email_address = forms.EmailField(label=_("Email (required)"), required=True, widget=forms.TextInput())

    message = forms.CharField(label=_("Invite Message"), required=False,widget=forms.TextInput())
    group = forms.CharField(label=_("A specific group you'd like to invite them to (Optional)"), required=False)

    
    def clean_email_address(self):
        email_address = self.cleaned_data['email_address']
        if User.objects.filter(email_address=email_address) :
            raise forms.ValidationError(_("We already have a user with that email address."))
        return self.cleaned_data['email_address']


    def clean_group(self):
        # turn group id into actual object
        group = self.cleaned_data['group']
        if TgGroup.objects.filter(group_name=group):
            return TgGroup.objects.get(group_name=group)
        raise forms.ValidationError(_("There is no group with a group_name %s" % group))
        

