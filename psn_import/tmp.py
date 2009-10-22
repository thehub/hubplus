from apps.plus_resources.models import Resource
from apps.plus_groups.models import TgGroup
from apps.plus_tags.models import Tag, get_tags

gs = TgGroup.objects.filter(group_name__startswith='stewarding')
for g in gs :
    print g

    for m in g.get_members() :
        print m

