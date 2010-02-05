from apps.plus_groups.models import TgGroup

for g in TgGroup.objects.all() :
    g.group_type = g.group_type.lower()
    print g.display_name.encode('utf-8'),g.group_type
    g.save()
