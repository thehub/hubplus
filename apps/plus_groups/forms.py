from datetime import datetime, timedelta
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _, ugettext

from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from apps.plus_lib.utils import make_name
from apps.plus_groups.models import GROUP_TYPES, TgGroup, name_from_title
from apps.plus_lib.utils import HTMLField


PERMISSION_OPTIONS = (
    (u'public', u'Public'),
    (u'open', u'Open'),
    (u'invite', u'Invite'),
    (u'private', u'Private'),
)
CREATE_INTERFACES = (
    (u"CreateWikiPage", u"CreateWikiPage"),
    (u"CreateResource", u"CreateResource"), 
    (u"CreateNews", u"CreateNews"),
    (u"CreateEvent", u"CreateEvent")
)

class AddContentForm(forms.Form):

    title = forms.CharField(max_length=100)
    group = forms.IntegerField()
    create_iface = forms.ChoiceField(choices=CREATE_INTERFACES)
        #ensure name is unique for group and type
    def clean(self):
        if self._errors:
            return self.cleaned_data
    
            #raise forms.ValidationError()

        self.cleaned_data['name'] = name_from_title(self.cleaned_data['title'])
        self.cleaned_data['type_string'] = self.cleaned_data['create_iface'].split('Create')[1]
        cls = ContentType.objects.get(model=self.cleaned_data['type_string'].lower()).model_class()
        group = TgGroup.objects.get(id=self.cleaned_data['group'])
        try:
            obj = cls.objects.get(name=self.cleaned_data['name'], in_agent=group.get_ref(), stub=True)
            self._errors['title'] = _("There is already a %s in %s called %s. Please choose a different title.") %(self.cleaned_data['type_string'], group.display_name.capitalize(), self.cleaned_data['title'])
        except cls.DoesNotExist:
            pass

        return self.cleaned_data
    

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

class TgGroupMessageMemberForm(forms.Form) :
    message_header = forms.CharField()
    message_body = forms.CharField()
  
