# backend/logodbcon/tests.py
import json
import unittest
import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

# Django ayarlarını yükleme
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sapreports.settings')
django.setup()

# Modelleri import etme
from logodbcon.models.sq_query_model import SQLQuery

class SQLQueryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sql_query_name = "customerbalance"

        # Kullanıcı oluşturma ve token alma
        User = get_user_model()
        self.user = User.objects.create_user(email='user@tunaofis.com', password='Tuna2023')
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        
        # Authorization header ekleme
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {self.token}'
        
        # Aynı isimdeki SQLQuery nesnesi varsa sil
        SQLQuery.objects.filter(name=self.sql_query_name).delete()

        # SQLQuery nesnesi oluşturma
        self.sql_query = SQLQuery.objects.create(
            name=self.sql_query_name,
            query="""
            SELECT 
                CLCARD.CODE AS CustomerCode,
                CLCARD.DEFINITION_ AS CustomerName,
                SUM(CASE WHEN CLFLINE.MODULENR = 3 AND CLFLINE.TRCODE IN (1, 2, 3, 12, 14) THEN CLFLINE.AMOUNT ELSE 0 END) AS Debit,
                SUM(CASE WHEN CLFLINE.MODULENR = 3 AND CLFLINE.TRCODE IN (4, 5, 6, 11, 13) THEN CLFLINE.AMOUNT ELSE 0 END) AS Credit
            FROM 
                LG_001_CLCARD CLCARD
            LEFT JOIN 
                LG_001_CLFLINE CLFLINE ON CLCARD.LOGICALREF = CLFLINE.CLIENTREF
            GROUP BY 
                CLCARD.CODE, CLCARD.DEFINITION_
            ORDER BY 
                CLCARD.CODE;
            """,
            parameters=[]
        )

    def test_customerbalance_query(self):
        # Müşteri bakiye sorgusunu çalıştırma
        response = self.client.get(reverse('sqlquery-detail', args=[self.sql_query_name]))
        self.assertEqual(response.status_code, 200)
        
        # JSON yanıtını çözme
        result = response.json()
        
        # Test çıktısını terminalde görüntüleme
        print(json.dumps(result, indent=4))

if __name__ == "__main__":
    unittest.main()


