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
    keyword = models.TextField(max_length=50, null=True) # duplicated here for quick querying purposes
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
            items = items.filter(tag__keyword=keyword).distinct()
    return items

def get_tags_for_object(tagged, user):
    tags = get_tags(tagged=tagged)
    keywords = tags.values('keyword').distinct() #also need to do a group_by keyword / count tags for a keyword to determine prominence of the tag
    return keywords[0:10]


from django.db.models import Count


def scale_tag_weights(tag_counts, levels=8):
    n = tag_counts.count()
    start_index = 0
    weighted_tags = []
    for level in range(1, levels+1):
        end_index = n/levels*level
        #deal with any remainder by putting them on the top level - otherwise we could use floats and rounding here
        if level == levels:
            end_index = n
        previous_max_count = tag_counts[max(start_index-1, 0)]['count']
        for annot in tag_counts[start_index:end_index]:
            if annot['count'] == previous_max_count:
                annot['level'] = max(level - 1, 1)  
            else:
                annot['level'] = level
            weighted_tags.append(annot)
        start_index = end_index
    
    return weighted_tags

def keyword_sort(A, B):
    if A['keyword']<B['keyword']:
        return -1
    return 1

def tag_counts(n=50, tag_set=None):
    counts = tag_set.values('keyword').annotate(count=Count('items')).order_by('count')
    count = counts.count()
    min_count = max(count-n, 0)
    return counts[min_count:count]


from django.db.models.query import QuerySet

def counts_sort(a, b):
    if a['count'] > b['count']:
        return -1
    return 1

def get_intersecting_tags(items, n=10, levels=8):
    #get the tags on these items, these should not be distinct but one tag per intersection
    # may need to get all the "TagItems here"
    try:
        total = items.count()
    except TypeError:
        total = len(items)

    # the problem with below is that when you have a single item that is tagged more than once with the same keyword - inflating the count
    # i.e. with different tag_type, or tagged_for different users

    # keywords_count = Tag.objects.filter(items__in=items).values('keyword').annotate(count=Count('keyword')).exclude(count=total)

    # solution a) immediate -- add keyword to each tag_item and count tag_items by distinct (ref, keyword) combinations
    #          b) 'a)' will not work when we need to count only items in a user's tagspace or of a particular type. 
    #             This could be rectified by filtering tag_items by certain tag types 
    #             OR creating a join/view of tag_items with tag_types which can then be queried.  The former is preferable if practical within the ORM constraints 

    #if not isinstance(items, QuerySet):
    #    items = GenericReference.objects.filter(id__in=items)

    keywords_count = TagItem.objects.filter(ref__in=items).values('keyword', 'ref').distinct()  #keywords_count.annotate(count=Count('keyword')).exclude(count=total)
    counts = {}
    # not how I wanted to do it. -- maybe very inefficient with large datasets
    for entry in keywords_count:
        counts.setdefault(entry['keyword'], {'keyword':entry['keyword'], 'count':0})
        counts[entry['keyword']]['count'] += 1
        if counts[entry['keyword']]['count'] == total:
            del counts[entry['keyword']]
            

    #top_intersections = keywords_count.order_by('-count')[:n]
    counts = counts.values()
    counts.sort(counts_sort)
    top_intersections = counts[:n]

    if top_intersections:
        max_level = top_intersections[0]['count']

        for tag in top_intersections:
            level = int(round((tag['count']/float(max_level)*levels)))
            tag['level'] = level and level or 1 

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

    keyword = tag_value.lower()
    #does the tag already exist?
    try:
        tag = Tag.objects.get(tag_type=tag_type,
                              keyword=keyword,
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
                           keyword=keyword,
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
