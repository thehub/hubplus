
from apps.plus_tags.models import Tag

for t in Tag.objects.all() :
    if t.tag_type in [u'',u'None',u'folder_name'] :
        t.tag_type = 'tag'
        t.save()



