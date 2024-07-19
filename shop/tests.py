# from django.test import TestCase

# Create your tests here.

import datetime
ordernumber = str(1234).zfill(6)+str(datetime.datetime.now())[:24].replace(' ', '').replace('-', '').replace(':', '').replace('.', '')
print(datetime.datetime.now())
print(ordernumber)