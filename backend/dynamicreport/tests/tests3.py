# backend\dynamicreport\tests.py  py manage.py test dynamicreport.tests3
from django.test import TestCase
from ..utilities.hana_data_types import format_decimal
''' 
test_decimal = 12345.67
formatted_decimal = format_decimal(test_decimal)
print(f"Orjinal Değer: {test_decimal}, Biçimlendirilmiş Değer: {formatted_decimal}")
'''

class TestHanaDataTypes(TestCase):
    def test_format_decimal(self):
        test_decimal = 12345.67
        formatted_decimal = format_decimal(test_decimal)
        self.assertEqual(formatted_decimal, '12.345,67')
