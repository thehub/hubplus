from apps.plus_groups.models import TgGroup

group_ids = (38, 12, 69, 74, 114, 30, 71, 144)

for i in group_ids :
    g = TgGroup.objects.get(id=i)
    g.delete()
