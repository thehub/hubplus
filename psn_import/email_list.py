from django.contrib.auth.models import User

for u in User.objects.all() :
    print ("%s, %s, %s, %s" % (u.username, u.first_name, u.last_name, u.email_address)).encode('utf-8')
