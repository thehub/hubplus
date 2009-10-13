from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from apps.plus_permissions.models import GenericReference
from django.contrib.auth.models import User
from django.db.models import Q

class Tag(models.Model):
    """This is the actual tag. It should be created when the first TagItem is added. It should be deleted when no more TagItems refer to it. 
    """
    keyword = models.TextField(max_length=50)
    # tag_types are qualifiers e.g. the tag "python" relating to the user "Tom" might have a "tag_type" of "interest"
    tag_type = models.TextField(max_length=30, default=None)
    # "tagged_for" is the agent within which the Tag exists. This is distinguished from "tagged_by" which is the user that actually did the tagging. e.g. Tom might tag something on behalf of the "tech team" group, in which case Tom is the "tagged_by" user and "tech team" is the tagged_for agent.
    tagged_for = models.ForeignKey(GenericReference, related_name="tags_in_this_context")
    items = models.ManyToManyField(GenericReference, through="TagItem")

class TagItem(models.Model):
    """This represents a m2m relation between Tag and GenericReference. Each time a tag is added one of these is added and the "Tag" is created if it doesn't already exist. The relation needs to be managed by the ORM so that it can have an extra attribute referring the the user that did that tagging.
    """
    class Meta:
        unique_together=('tag', 'ref')
    tag = models.ForeignKey(Tag)
    ref = models.ForeignKey(GenericReference)
    tagged_by = models.ForeignKey(User, related_name="tags_created")
    def obj(self):
        return self.ref.obj


def tag_autocomplete(tag_value, limit, tagged_for=None, tagged=None, tag_type=None):
    """XXX should use a similar algorithm to top_tags here to determine 'weight'/level, but it order by weight (not alphabetically)
    """
    query_dict = {'partial_tag_value':tag_value}
    if tag_type:
        query_dict['tag_type'] = tag_type
    tags = get_tags(**query_dict)
    keywords = tags.values('keyword').distinct()
    return keywords[0:limit]

def get_resources_for_tag_intersection(keywords):
    items = GenericReference.objects
    if keywords:
        for keyword in keywords:
            items = items.filter(tag__keyword=keyword)
    return items

def get_tags_for_object(tagged, user):
    tags = get_tags(tagged=tagged)
    keywords = tags.values('keyword').distinct() #also need to do a group_by keyword / count tags for a keyword to determine prominence of the tag
    return keywords[0:10]


from django.db.models import Count

def keyword_sort(A, B):
    if A['keyword']<B['keyword']:
        return -1
    return 1

def top_tags(n=50, levels=18):
    tags = get_tags()

    n = min(n, tags.count())
    tag_counts = tags.values('keyword').annotate(count=Count('items')).order_by('count')[:n]
    level_boundaries = []
    for level in range(1, levels+1):
        level_boundaries.append((n/levels)*level)

    current_count = 1 
    current_level = 1
    index = 0
    tag_cloud_list = []
    for annot in tag_counts:
        tag_cloud_list.append(annot)
        if annot['count'] > current_count and index>level_boundaries[current_level-1]:
            current_level += 1
        current_count = annot['count']
        annot['level'] = current_level
        index += 1

    tag_cloud_list.sort(keyword_sort)
    
    return tag_cloud_list


def get_intersecting_tags(items, n=10):
    #get the tags on these items, these should not be distinct but one tag per intersection
    # may need to get all the "TagItems here"
    try:
        total = items.count()
    except TypeError:
        total = len(items)
    keywords_count = Tag.objects.filter(items__in=items).values('keyword').annotate(num_keyword=Count('keyword')).exclude(num_keyword=total)
    top_intersections = keywords_count.order_by('-num_keyword')[:n]
    return top_intersections

def get_tags(tagged=None, tag_type=None, tag_value=None, tagged_for=None, tagged_by=None, partial_tag_value=None):
    """XXX Should only get viewable tags here, further should only get viewable items within those tags, and only viewable items within a tag which count towards its weight
    """
    tag_filter = {}

    if tag_type != None:
        tag_filter['tag_type'] = tag_type
    if tag_value != None:
        tag_filter['keyword'] = tag_value
    elif partial_tag_value != None:
        Qobj = Q(keyword__startswith=partial_tag_value) | Q(keyword__contains=' '+partial_tag_value)
    if tagged_for != None:
        if not isinstance(tagged_for, GenericReference):
            tagged_for = tagged_for.get_ref()
        tag_filter['tagged_for'] = tagged_for
    require_distinct = False

    if tagged != None:
        require_distinct = True
        tag_filter['items__in'] = [tagged.get_ref().id]
        
    if tagged_by != None:
        require_distinct = True
        tag_filter['items__tagged_by'] = tagged_by.id
    if 'Qobj' in locals():
        tags = Tag.objects.filter(Qobj, **tag_filter)
    else:
        tags = Tag.objects.filter(**tag_filter)
    if require_distinct:
        tags.distinct()
    return tags


def tag_add(tagged, tag_type, tag_value, tagged_by, tagged_for=None):
    if not tagged_for:
        tagged_for = tagged_by.get_ref()

    #does the tag already exist?
    try:
        tag = Tag.objects.get(tag_type=tag_type,
                              keyword=tag_value.lower(),
                              tagged_for=tagged_for)
    except Tag.DoesNotExist:
        #create it!
        tag = Tag(tag_type=tag_type,
                  keyword=tag_value.lower(),
                  tagged_for=tagged_for)
        tag.save()
        
    try:
        tag_item = tag.items.get(id=tagged.get_ref().id)
        return (tag, False)
    
    except GenericReference.DoesNotExist:
        tag_item = TagItem(ref=tagged.get_ref(),
                           tag=tag,
                           tagged_by=tagged_by)
        tag_item.save()
        return (tag, True) 


def tag_delete(tagged, tag_type, tag_value, tagged_by, tagged_for=None):
    if not tagged_for:
        tagged_for = tagged_by.get_ref()
    try:
        existing_tag = Tag.objects.get(tag_type=tag_type,
                                       keyword=tag_value.lower(),
                                       tagged_for=tagged_for)
    except Tag.DoesNotExist:
        return (None, False)

    existing_tag_item = existing_tag.items.remove(tagged.get_ref())

    if not existing_tag.items.count():
        existing_tag.delete()
    
    
    return (None, True)
