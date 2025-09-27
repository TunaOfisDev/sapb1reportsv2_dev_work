# backend/hanadbcon/api/sq_query_model.py
from django.db import models
from .base import BaseModel
from authcentral.models import Department, Position 
from django.contrib.auth.models import Group


class SQLQuery(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    query = models.TextField()
    parameters = models.JSONField(default=list, blank=True, null=True)
    departments = models.ManyToManyField(Department, related_name='queries_departments', blank=True)
    positions = models.ManyToManyField(Position, blank=True) 

    # SQL sorguları için klavuz metni
    guidance_text = models.TextField(
        default="""
        Parametrik SQL Sorgusu Oluşturma Klavuzu:
        - Sorgunuzda parametre kullanmak için, parametre yerine '?' sembolünü kullanın.
        - Şema bilgisini sorgunuzda "{schema}" placeholder'ı ile belirtin.

        Örnek Parametre: [{"name": "variant_code", "type": "string", "description": "Varyant Kodu"}]
        
        Örnek Sorgu:
        SELECT
            I."ItemCode",
            COALESCE(I."ItemName", 'YOK') AS "ItemName",
            COALESCE(ITM1."Price", 0) AS "Price",
            COALESCE(ITM1."Currency", 'YOK') AS "Currency"
        FROM
            {schema}."OITM" I
        LEFT JOIN
            {schema}."ITM1" ITM1 ON I."ItemCode" = ITM1."ItemCode" AND ITM1."PriceList" = 1
        WHERE
            I."ItemCode" = ?;

        - Bu sorguda 'variant_code' parametresi kullanılmaktadır.
        - API çağrısında URL şu şekilde olmalıdır:
        /api/v2/hanadbcon/query/query_variant_status_hana_db/?variant_code=30.BW.A14090.M1.E1&schema=TUNADB24

        - Parametreler query string'de sağlanır ve SQL sorgusunda güvenli olarak bağlanır.
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
