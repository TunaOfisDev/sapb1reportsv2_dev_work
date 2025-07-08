# backend/filesharehub_v2/api/serializers.py
from rest_framework import serializers
from filesharehub_v2.models.filerecord import FileRecord

class FileRecordSerializer(serializers.ModelSerializer):
    full_path = serializers.ReadOnlyField()
    id = serializers.SerializerMethodField()

    class Meta:
        model = FileRecord
        fields = [
            "id",  # frontend için file_id'yi "id" gibi göster
            "file_id",  # backend işlemleri için de erişilebilir olsun
            "name", "path", "full_path", "is_dir", "size",
            "modified", "ext", "is_image", "thumbnail_path",
        ]

    def get_id(self, obj):
        return obj.file_id
