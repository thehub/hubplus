from apps.plus_groups.models import TgGroup
from apps.profiles.models import Profile
from apps.plus_wiki.models import WikiPage
from apps.plus_resources.models import Resource
from datetime import datetime

def patch():
    for obj in TgGroup.objects.all():
        ref = obj.get_ref()
        ref.display_name = obj.get_display_name()
        ref.modified = datetime.now()
        ref.save()

    for obj in Profile.objects.all():
        ref = obj.get_ref()
        ref.display_name = obj.get_display_name()    
        ref.modified = datetime.now()
        ref.save()

    for obj in Resource.objects.all():
        ref = obj.get_ref()
        ref.display_name = obj.get_display_name()    
        ref.modified = datetime.now()
        ref.save()

    for obj in WikiPage.objects.all():
        ref = obj.get_ref()
        ref.display_name = obj.get_display_name()
        ref.modified = datetime.now()
        ref.save()



patch()
