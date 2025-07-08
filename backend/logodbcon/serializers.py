# backend/logodbcon/serializers.py
from rest_framework import serializers
from .models.sq_query_model import SQLQuery

class SQLQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SQLQuery
        fields = ['name', 'query', 'parameters', 'positions', 'description', 'guidance_text']

    def validate(self, data):
        # name alanı için validasyon
        if not data.get('name'):
            raise serializers.ValidationError("Sorgu adı boş olamaz.")
        if len(data['name']) > 100:
            raise serializers.ValidationError("Sorgu adı 100 karakterden fazla olmamalıdır.")

        # query alanı için basit bir validasyon
        if not data.get('query'):
            raise serializers.ValidationError("SQL sorgusu boş olamaz.")
        if "DROP TABLE" in data['query'] or "DELETE FROM" in data['query']:
            raise serializers.ValidationError("Tehlikeli SQL ifadeleri içeremez.")

        # parameters alanı için validasyon
        if data.get('parameters'):
            if not isinstance(data['parameters'], list):
                raise serializers.ValidationError("Parametreler bir liste olmalıdır.")

        # description alanı için validasyon
        if data.get('description') and len(data['description']) > 1500:
            raise serializers.ValidationError("Açıklama 1500 karakteri aşmamalıdır.")

        return data

