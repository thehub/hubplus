# common between uploads (plus_resources) / wikipages etc.

from datetime import datetime
from apps.plus_tags.models import tag_item_delete, TagItem
from apps.plus_groups.models import TgGroup

class NameConflictException(Exception) :
    pass

def resource_common(cls) :

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

    cls.move_to_new_group = move_to_new_group

    def check_name(cls, name, in_agent, obj=None):
        try:
            res = cls.objects.get(name=name, in_agent=in_agent)
            if obj and obj.id==res.id:
                pass
            else:
                raise ValueError("Can't change name to %s, a %s of that name already exists in this group" % (name,cls.__name__))
        except cls.DoesNotExist:
            pass

    cls.check_name = classmethod(check_name)

    def delete(self) :
        for tag_item in TagItem.objects.filter(ref=self.get_ref()):
            tag_item_delete(tag_item)
        ref = self.get_ref()
        ref.delete()
        super(self.__class__,self).delete()

    cls.delete = delete

    def save(self):
        super(self.__class__, self).save()
        ref = self.get_ref()
        ref.modified = datetime.now()
        ref.display_name = self.get_display_name()
        ref.save()

    cls.save = save

    def display_type(self) :
        if self.__class__.__name__ == 'Resource' :
            return 'Uploaded File'
        if self.__class__.__name__ == 'WikiPage' :
            return 'Page'
        return self.__class__.__name__
    cls.display_type = display_type


    def list_siblings(self) :
        return self.in_agent.obj.get_resources_in_class(self.__class__)
    cls.list_siblings = list_siblings


    return cls



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


