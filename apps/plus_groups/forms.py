from datetime import datetime, timedelta

from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _, ugettext

from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from apps.plus_lib.utils import make_name
from apps.plus_groups.models import GROUP_TYPES, TgGroup


PERMISSION_OPTIONS = (
    (u'public', u'Public'),
    (u'open', u'Open'),
    (u'invite', u'Invite'),
    (u'private', u'Private'),
)
CREATE_INTERFACES = (
    (u"CreateWikiPage"),
    (u"CreateUpload"), 
    (u"CreateNews"),
    (u"CreateEvent")
)

class AddContentForm(forms.Form):
    title = forms.CharField(max_length=100)
    group = forms.IntegerField()
    create_iface = forms.ChoiceField(choices=CREATE_INTERFACES)
    

class TgGroupForm(forms.Form):
    
    name = forms.CharField()
    group_type = forms.ChoiceField(choices=GROUP_TYPES)
    description = forms.CharField()
    address = forms.CharField(required=False)
    location = forms.CharField(required=False)
    permissions_set = forms.ChoiceField(choices=PERMISSION_OPTIONS)
    
    def clean_name(self):
        name = self.cleaned_data['name']
        group_name=make_name(name)
        if TgGroup.objects.filter(group_name=group_name):
            raise forms.ValidationError(_("We already have a group with this name."))

        self.cleaned_data['display_name'] = name
        self.cleaned_data['group_name'] = group_name
        return group_name
    
    def save(self, user, site):

        group = site.create_TgGroup(
            group_name=self.cleaned_data['group_name'],
            display_name=self.cleaned_data['display_name'],
            group_type = self.cleaned_data['group_type'],
            level = 'member',
            user = user,
            description = self.cleaned_data['description'],
            permission_prototype = self.cleaned_data['permissions_set'],
            )
        group.save()
        return group
    


class TgGroupMemberInviteForm(forms.Form) :
    plain_text = forms.CharField()
    special_message = forms.CharField()
    
    def clean_plain_text(self) :
        tt = self.cleaned_data['plain_text']
        try :
            user = User.objects.get(username=tt)
        except :
            print "%s is not a username" % tt
            try :
                user = User.objects.get(email_address=tt)
            except :
                print "%s is not an email_address" % tt
                raise forms.ValidationError('Not recognised as either email or existing username')
        self.cleaned_data['user'] = user
