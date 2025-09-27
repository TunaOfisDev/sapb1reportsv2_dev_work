# backend/docarchive/serializers.py
from rest_framework import serializers
from .models.models import Document, Department, DocumentFile

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

# Department modeli için serializer
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


# Department modeli için serializer
class DocumentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFile
        fields = '__all__'