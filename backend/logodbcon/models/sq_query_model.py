# backend/logodbcon/models/sq_query_model.py
from django.db import models
from .base import BaseModel
from authcentral.models import Department, Position 
from django.contrib.auth.models import Group


class SQLQuery(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    query = models.TextField()
    parameters = models.JSONField(default=list, blank=True, null=True)
    departments = models.ManyToManyField(Department, related_name='logodbcon_queries_departments', blank=True)
    positions = models.ManyToManyField(Position, related_name='logodbcon_positions', blank=True) 

    # SQL sorguları için klavuz metni
    guidance_text = models.TextField(
        default="""
        Parametrik SQL Sorgusu Oluşturma Klavuzu:
        - Sorgunuzda parametre kullanmak için, parametre yerine '?' işaretini kullanın.
        - 'startdate' ve 'enddate' gibi tarih parametreleri için, istek URL'sinde 'YYYY-MM-DD' formatında tarihleri belirtin.
        - Diğer parametreler ('cardcode', 'itemcode' vb.) için de benzer şekilde, istek URL'sinde parametre değerlerini belirtin.
        - SQL sorgunuzda şema bilgisini "{schema}" placeholder'ı ile belirtin:
        Ornek parametre: [{"name": "", "type": "", "description": ""}]
        Örnek Sorgu:
        WITH RiskCalculation AS (
            SELECT
                "CardCode",
                "CardName",
                ...
                WHERE "RefDate" BETWEEN ? AND ?), 0) AS "Balance",
                ...
        )
        SELECT
            "CardCode",
            "CardName",
            "Balance",
            ...
        FROM
            RiskCalculation
        WHERE
            ("Balance" + "TotalOrders" + "TotalDelivery") != 0;
        - Bu sorguyu çağırırken, URL'niz şu şekilde olmalıdır: /api/query/TEST?startdate=2023-01-01&enddate=2023-12-31
        """,
        blank=True
    )

    def __str__(self):
        return self.name

    @staticmethod
    def get_query_by_name(query_name):
        try:
            sql_query = SQLQuery.objects.get(name=query_name)
            # Departmanları da döndürmek için güncelleme
            return sql_query.query, sql_query.parameters, sql_query.guidance_text, sql_query.departments.all()
        except SQLQuery.DoesNotExist:
            return None, None, None, None
