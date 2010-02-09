
from apps.account.models import PasswordReset

for p in PasswordReset.objects.all() :
    if PasswordReset.objects.filter(temp_key=p.temp_key,reset=False).count() > 1 :
        print p
        p.reset = True
        p.save()

