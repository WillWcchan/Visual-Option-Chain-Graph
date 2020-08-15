from datetime import datetime as dt, timedelta, date

from django.test import TestCase
from .models import Option, OptionPrice

# Create your tests here.
class OptionModelTests(TestCase):

    def testA(self):
        self.assertIs(1 > 0, True)