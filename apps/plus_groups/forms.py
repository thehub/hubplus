from datetime import datetime, timedelta

from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _, ugettext

from django.contrib.sites.models import Site

from apps.plus_lib.utils import make_name
from apps.plus_groups.models import GROUP_TYPES, TgGroup


PERMISSION_OPTIONS = (
    (u'public', u'Public'),
    (u'open', u'Open'),
    (u'invite', u'Invite'),
    (u'private', u'Private'),

)



class TgGroupForm(forms.Form):
    
    name = forms.CharField()
    group_type = forms.ChoiceField(choices=GROUP_TYPES)
    about = forms.CharField()
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
            about = self.cleaned_data['about'],
            )
        group.save()
        return group
    

