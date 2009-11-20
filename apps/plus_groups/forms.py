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
from apps.plus_groups.models import TgGroup, name_from_title, Location
from apps.plus_lib.utils import HTMLField

from django.conf import settings
from apps.plus_permissions.default_agents import get_or_create_root_location

from django.core.urlresolvers import reverse




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

reverse_lookup_dict = {'WikiPage': ['Page', 'view_WikiPage'],
                       'Resource': ['Upload', 'view_Resource']}

class AddContentForm(forms.Form):

    title = forms.CharField(max_length=100)
    current_app = forms.CharField(max_length=100)
    group = forms.IntegerField()
    create_iface = forms.ChoiceField(choices=CREATE_INTERFACES)
        #ensure name is unique for group and type
    def clean(self):
        if self._errors:
            return self.cleaned_data
    

        self.cleaned_data['name'] = name_from_title(self.cleaned_data['title'])
        self.cleaned_data['type_string'] = self.cleaned_data['create_iface'].split('Create')[1]
        cls = ContentType.objects.get(model=self.cleaned_data['type_string'].lower()).model_class()
        group = TgGroup.objects.get(id=self.cleaned_data['group'])
        cleaned_data = validate_name_url(cls, group, self.cleaned_data)
        return self.cleaned_data
    

def validate_name_url(cls, group, cleaned_data):
    try:
        obj = cls.objects.get(name=cleaned_data['name'], in_agent=group.get_ref(), stub=False)
        type_label, lookup_string = reverse_lookup_dict[cls.__name__]
        existing_url = reverse(cleaned_data['current_app'] + ':' + lookup_string, args=[group.id, cleaned_data['name']])
        self._errors['title'] = _("There is already a <em>%s</em> in %s called <a href='%s'>%s</a>. Please choose a different title.") %(type_label, group.display_name.capitalize(), existing_url, cleaned_data['title'])
    except cls.DoesNotExist:
        return cleaned_data


class TgGroupForm(forms.Form):
    
    name = forms.CharField(max_length=60)
    group_type = forms.ChoiceField(choices=settings.GROUP_TYPES)
    description = HTMLField()

    address = forms.CharField(required=False)
    location = forms.CharField(required=False)
    permissions_set = forms.ChoiceField(choices=PERMISSION_OPTIONS)

    is_hub = forms.CharField()
    
    def clean_name(self):
        name = self.cleaned_data['name']
        group_name=make_name(name)
        if TgGroup.objects.filter(group_name=group_name):
            raise forms.ValidationError(_("We already have a group with this name."))

        self.cleaned_data['display_name'] = name
        self.cleaned_data['group_name'] = group_name
        return group_name

    def clean_is_hub(self) :
        if self.cleaned_data['is_hub'] == 'True' : 
            self.cleaned_data['is_hub'] = True
        else :
            self.cleaned_data['is_hub'] = False
        return self.cleaned_data['is_hub']


    
    def save(self, user, site):
        if not self.cleaned_data['is_hub'] :
            place = get_or_create_root_location()
        else :
            place,created = Location.objects.get_or_create(name=self.cleaned_data['location'])

        group = site.create_TgGroup(
            group_name=self.cleaned_data['group_name'],
            display_name=self.cleaned_data['display_name'],
            group_type = self.cleaned_data['group_type'],
            level = 'member',
            user = user,
            description = self.cleaned_data['description'],
            permission_prototype = self.cleaned_data['permissions_set'],
            place = place,
            )
        group.save()
        return group
    


class TgGroupMemberInviteForm(forms.Form) :
    plain_text = forms.CharField()
    special_message = forms.CharField(required=False)
    
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
                raise forms.ValidationError(_('Not recognised as either existing username or known email'))
        self.cleaned_data['user'] = user

class TgGroupMessageMemberForm(forms.Form) :
    message_header = forms.CharField()
    message_body = forms.CharField()
  
