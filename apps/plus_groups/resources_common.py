# common between uploads (plus_resources) / wikipages etc.
from django.db import models

from datetime import datetime
from apps.plus_tags.models import tag_item_delete, TagItem
from apps.plus_groups.models import TgGroup
from apps.plus_permissions.models import GenericReference
from django.contrib.auth.models import User

from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from apps.plus_lib.utils import hub_name

class NameConflictException(Exception) :
    pass

from apps.plus_explore.models import Explorable

class ResourceCommonModel(Explorable) :
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)

    stub = models.BooleanField(default=True)
    in_agent = models.ForeignKey(GenericReference,related_name="%(class)s_related")
    created_by = models.ForeignKey(User, related_name="created_%(class)s", null=True) 
    #stubs shouldn't be created by anyone or owned by anyone (imo) - t.s.

    class Meta:
        abstract = True
        unique_together = (("name", "in_agent"),)

    def set_name(self, name):
        self.check_name(name, self.in_agent, obj=self)
        self.name = name

    def display_name(self):
        return self.title


    def move_to_new_group(self, group) :
        try :
            self.check_name(self.name, group.get_ref(), self)
        except ValueError, e:
            raise NameConflictException(_("Group %(group_name)s already has a %(type)s called %(name)")%{'type':self.__class__.__name__,'group_name':group.group_name,'name':name})
        # change in_agent   
        self.in_agent = group.get_ref()
        # change security_context
        self.acquires_from(group)
        self.save()

    @classmethod
    def check_name(cls, name, in_agent, obj=None):
        try:
            res = cls.objects.get(name=name, in_agent=in_agent)
            if obj and obj.id==res.id:
                pass
            else:
                raise ValueError("Can't change name to %s, a %s of that name already exists in this group" % (name,cls.__name__))
        except cls.DoesNotExist:
            pass


    def delete(self) :
        for tag_item in TagItem.objects.filter(ref=self.get_ref()):
            tag_item_delete(tag_item)
        ref = self.get_ref()
        ref.delete()
        models.Model.delete(self)


    def save(self):
        models.Model.save(self) # can't use super because this designed to be called by subclass, which leads to recursionOB
        ref = self.get_ref()
        ref.modified = datetime.now()
        ref.display_name = self.get_display_name()
        ref.save()


    def display_type(self) :
        if self.__class__.__name__ == 'Resource' :
            return 'Uploaded File'
        if self.__class__.__name__ == 'WikiPage' :
            return 'Page'
        return self.__class__.__name__


    def list_siblings(self) :
        return self.in_agent.obj.get_resources_in_class(self.__class__)

    def get_attachments(self) :
        return self.get_ref().attachments.all()

    def add_attachment(self, attachment):
        self.get_ref().attachments.add(attachment.get_ref())
    
    def is_downloadable(self) :
        # override if downloadable
        return False

    # for Explorable interface
    def get_description(self) :
        return self.get_display_name()
   
    def get_author_name(self) :
        return self.created_by.get_display_name()


    def get_url_root(self) :
        group_label = 'group'
        if self.in_agent.obj.is_hub_type():
            group_label = hub_name().lower()
        return group_label + "s:"

    def get_url(self) :
        from django.core.urlresolvers import reverse
        url = reverse(self.get_url_root()+'view_'+self.__class__.__name__,args=(self.in_agent.obj.id,self.name))
        return 'http://%s%s' % (settings.DOMAIN_NAME, url)
    

# Forms
from django import forms

class MoveResourceForm(forms.Form) :
    new_parent_group = forms.CharField()

    def clean_new_parent_group(self) :
        # allows the resource to be moved to a new parent
        # assuming that the group_id is submitted.
        # why id? because group_name is just as abstract for the user.
        # and group display name is not necessarily unique
        
        parent_id = self.data['new_parent_group']
        if parent_id :
            # note that self.user needs to have been set on this form
            groups = TgGroup.objects.plus_filter(self.user, id=parent_id)
            if groups :
                self.cleaned_data['new_parent_group'] = groups[0]
            else :
                raise forms.ValidationError(_("There is no group with the id you submitted."))
        return self.cleaned_data['new_parent_group']


