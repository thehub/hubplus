
from apps.plus_contacts.models import Application, Contact
from apps.plus_permissions.proxy_hmac import attach_hmac

#def make_signup_link(sponsor, site_root, id) :
#    url = attach_hmac("/signup/%s/" % id, sponsor)
#    url = 'http://%s%s' % (site_root,url)
#    return url



for a in Application.objects.all() :
  
    if a.status != 1 : continue
    print
    print '%s, %s, %s, %s, ' % (a.applicant.first_name, a.applicant.last_name, a.applicant.email_address, a.status)
    print a.applicant.make_link(a.accepted_by,a.id)

 
