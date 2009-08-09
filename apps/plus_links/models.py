from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from apps.hubspace_compatibility.models import Location, ObjectReference
from apps.hubspace_compatibility.models import make_object_reference, get_referenced_object


class Service(models.Model) :
    url = models.URLField(max_length=200)
    name = models.CharField(max_length=50)

class Link(models.Model) :
    service = models.ForeignKey(Service,null=True)
    url = models.URLField(max_length=200)
    text = models.CharField(max_length=100)
    owner_content_type = models.ForeignKey(ContentType,related_name='link_owning_resource')
    owner_object_id = models.PositiveIntegerField()
    owner = generic.GenericForeignKey('owner_content_type', 'owner_object_id')

    
def get_links_for(owner) :
    return (x for x in Link.objects.filter(owner_object_id=owner.id) if x.owner == owner)


class ListItem(models.Model):
    """Ported from Hubspace. Ordering for list of things. Including links for pages.
    """
    list_name = models.CharField(max_length=100) #to differentiate multiple lists in the location
    next = models.ForeignKey("ListItem", default=None)
    location = models.ForeignKey(Location, null=True)

    item = models.ForeignKey(ObjectReference,related_name='list_item_item')
    owner = models.ForeignKey(ObjectReference,related_name='list_item_owner') # if this list belongs to, say, a Group or a Profile


class ListOfLinks :
    """ Just an in memory owner of a list. Not a model entity at the moment"""

    def __init__(self,xs,owner,location=None,next=None,list_name='default_list') :
        self.link_refs = [
            ListItem(item=make_object_reference(x),owner=make_object_reference(owner),location=location,next=next,list_name=list_name)
            for x in xs]

    def __getitem__(self,idx) :

        return self.link_refs[idx].item.object

    def __setitem__(self,idx,val) :
        raise Exception("""ListOfLinks class is not a real list. Can't assign to one element""")

    def __len__(self) : 
        return len(self.link_refs)

    def iterator(self) :
        return (x.object for x in self.link_refs)

            
        

    
