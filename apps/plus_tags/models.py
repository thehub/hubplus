from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


class GenericTag(models.Model) :
    keyword = models.TextField(max_length=50)
    tag_type = models.TextField(max_length=30, default=None)

    agent_content_type = models.ForeignKey(ContentType, related_name='generic_tag_agent')
    agent_object_id = models.PositiveIntegerField()
    agent = generic.GenericForeignKey('agent_content_type', 'agent_object_id')

    subject_content_type = models.ForeignKey(ContentType, related_name='generic_tag_subject')
    subject_object_id = models.PositiveIntegerField()
    subject = generic.GenericForeignKey('subject_content_type', 'subject_object_id')


def tag_autocomplete(tag_type, tag_value, limit):
    tags = get_tags(tag_type=tag_type, partial_tag_value=tag_value)
    return [tag.keyword for tag in tags[0:10]]


def get_tags(tagged=None, tag_type=None, tag_value=None, tagger=None, partial_tag_value=None):
    given = {}
    if tagged != None:
       tagged_type = ContentType.objects.get_for_model(tagged)
       given.update(dict(subject_object_id = tagged.id,
                         subject_content_type__pk = tagged_type.id))
    if tagger != None:
       tagger_type = ContentType.objects.get_for_model(tagger)
       given.update(dict(agent_object_id = tagger.id,
                         agent_content_type__pk = tagger_type.id))
    if tag_type != None:
       given['tag_type'] = tag_type
    if tag_value != None:
       given['keyword'] = tag_value
    elif partial_tag_value != None:
       given['keyword__startswith'] = partial_tag_value
    tags = GenericTag.objects.filter(**given)
    tags.order_by('keyword')
    return tags

def tag_add(tagged, tag_type, tag_value, tagger):
    existing_tag = get_tags(tagged, tag_type, tag_value, tagger)

    if existing_tag:
       return (existing_tag[0], False)

    new_tag = GenericTag(keyword = tag_value,
                         tag_type = tag_type,
                         agent = tagger,
                         subject = tagged)
    new_tag.save()
    return (new_tag, True)

def tag_delete(tagged, tag_type, tag_value, tagger):
    existing_tag = get_tags(tagged, tag_type, tag_value, tagger)
    if not existing_tag:
       return (None, False)
    existing_tag.delete()
    return (None, True)


