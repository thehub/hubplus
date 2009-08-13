import unittest

from application import *
from apps.plus_contacts.models import *
from apps.plus_groups.models import *


class TestApplication(unittest.TestCase) :

    def test_application(self) :
        contact = PlusContact(first_name='kate', last_name='smith', email_address='kate@z.x.com')
        contact.save()
        group, admin = create_site_group('singing', 'Singers')
        application = Application(applicant=contact, request='I want to join in')
        application.save()
        application.group = group
        application.save()
        self.assertEquals(application.applicant, contact)
        self.assertEquals(application.request, 'I want to join in')
        self.assertEquals(application.group, group)
        self.assertEquals(application.status, PENDING)


