import unittest

from application import *
from apps.plus_contacts.models import *

class TestApplication(unittest.TestCase) :

    def test_application(self) :
        contact = PlusContact(first_name='kate', last_name='smith', email

