# backend\dynamicreport\tests.py  py manage.py test dynamicreport.tests
from django.test import TestCase
from ..utilities.data_services import DataServices
from ..utilities.connection_pool_manager import ConnectionPoolManager

class HanaDBTestCase(TestCase):

    def test_simple_hana_query(self):
        ConnectionPoolManager.initialize_hana_pool()
        connection = ConnectionPoolManager.get_hana_connection()

        try:
            sql_query = """SELECT "DocEntry", "CardCode", "CardName" FROM "TUNATEST"."ORDR" WHERE "DocDate" >= '01.01.2023'"""
            result = DataServices.execute_and_fetch(sql_query)
            print("Sorgu Sonucu:", result)
        except Exception as e:
            print(f"Hata: {str(e)}")
        finally:
            ConnectionPoolManager.release_hana_connection(connection)






'''  
    SELECT 
    O."DocEntry", 
    O."CardCode",   
    O."CardName" 

    FROM "TUNATEST"."ORDR" O
    
    WHERE O."DocDate" >= '01.01.2023'
    
'''