
from apps.plus_tags.models import Tag, TagItem

for t in TagItem.objects.all() :
    t.keyword = t.tag.keyword
    t.save()
