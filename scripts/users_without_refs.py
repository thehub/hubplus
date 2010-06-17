from django.contrib.auth.models import User

for u in User.objects.all() :
    try :
        u.get_ref()
    except Exception, e:
        print u.username, e

