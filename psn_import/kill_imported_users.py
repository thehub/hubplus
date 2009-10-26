
from django.contrib.auth.models import User

for u in User.objects.all() :
    if u.username != 'phil' and u.username != 'admin' :
        print u
        u.delete()
