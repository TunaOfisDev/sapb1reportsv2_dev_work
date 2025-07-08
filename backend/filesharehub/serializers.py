# backend/filesharehub/serializers.py
from rest_framework import serializers
from .models.models import Directory, FileRecord

class DirectorySerializer(serializers.ModelSerializer):
    """
    Dizin bilgilerini döndüren serializer.
    """
    class Meta:
        model = Directory
        fields = ['id', 'path', 'last_scanned']
        read_only_fields = ['last_scanned']


class FileRecordSerializer(serializers.ModelSerializer):
    """
    Dosya bilgilerini döndüren serializer.
    """
    directory_path = serializers.CharField(source='directory.path', read_only=True)
    size_mb = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = FileRecord
        fields = ['id', 'filename', 'file_path', 'directory', 'directory_path', 'size', 'size_mb', 'last_modified', 'thumbnail_url']
        read_only_fields = ['size', 'last_modified']

    def get_size_mb(self, obj):
        """Dosya boyutunu MB cinsinden döndürür."""
        return round(obj.size / (1024 * 1024), 2)

    def get_thumbnail_url(self, obj):
        """
        Thumbnail URL'sini döner.
        Eğer bir resim dosyası değilse uygun ikonu döner.
        """
        if obj.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
            # Eğer bir resim dosyasıysa, thumbnail URL'sini döndür
            return f"/api/v2/filesharehub/thumbnail/{obj.file_path}"
        # Eğer bir resim dosyası değilse, ikon döndür
        file_extension = obj.filename.split('.')[-1].lower()
        return f"/static/icons/{file_extension}_icon.png" if file_extension in ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'ppt', 'pptx', 'zip'] else "/static/icons/default_icon.png"


class FileListSerializer(serializers.Serializer):
    """
    Dosya listelerini ve dizinleri döndüren serializer.
    """
    directories = DirectorySerializer(many=True)
    files = FileRecordSerializer(many=True)
