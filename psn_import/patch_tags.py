from apps.plus_tags.models import TagItem

def patch_items():
    for item in TagItem.objects.all():
        item.keyword = item.tag.keyword
        item.save()
    print "tags_patched"

patch_items()
