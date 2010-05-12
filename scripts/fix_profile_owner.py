
from apps.profiles.models import Profile

for p in Profile.objects.all() :
    agents = [x.obj for x in p.get_tag_for_interface('Profile.Viewer').agents.all()]
    print p,p.user.username, p.get_ref().creator,agents
