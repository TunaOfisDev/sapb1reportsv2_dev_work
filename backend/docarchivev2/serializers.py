# backend/docarchivev2/serializers.py
from rest_framework import serializers
from .models.models import Department, Document, DocumentFile

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class DocumentFileSerializer(serializers.ModelSerializer):
    file = serializers.FileField(max_length=None, allow_empty_file=False, use_url=True)

    class Meta:
        model = DocumentFile
        fields = ['id', 'file']

class DocumentSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), allow_null=True)

    files = DocumentFileSerializer(many=True, required=False)

    class Meta:
        model = Document
        fields = ['id', 'name', 'created_at', 'owner_name', 'comments', 'department', 'files']
        depth = 1

    def create(self, validated_data):
        files_data = validated_data.pop('files', [])
        document = Document.objects.create(**validated_data)

        for file_data in files_data:
            file_instance = file_data.get('file', None)
            if file_instance:
                DocumentFile.objects.create(document=document, file=file_instance)

        return document

    def update(self, instance, validated_data):
        files_data = validated_data.pop('files', [])
        instance.name = validated_data.get('name', instance.name)
        instance.owner_name = validated_data.get('owner_name', instance.owner_name)
        instance.comments = validated_data.get('comments', instance.comments)
        instance.department = validated_data.get('department', instance.department)
        instance.save()

        for file_data in files_data:
            file_id = file_data.get('id', None)
            if file_id:
                file_instance = DocumentFile.objects.get(id=file_id, document=instance)
                file_instance.file = file_data.get('file', file_instance.file)
                file_instance.save()
            else:
                DocumentFile.objects.create(document=instance, **file_data)

        return instance
