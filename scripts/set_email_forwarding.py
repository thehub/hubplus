
from django.contrib.auth.models import User

for u in User.objects.all() :
    print u
    u.cc_messages_to_email = True
    u.save()

