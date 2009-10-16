
from apps.plus_groups.models import TgGroup

for g in TgGroup.objects.all() :
    print (g.group_name, g.place.name, g.group_type)
