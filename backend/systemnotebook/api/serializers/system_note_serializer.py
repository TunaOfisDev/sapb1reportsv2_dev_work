# backend/systemnotebook/api/serializers/system_note_serializer.py

from rest_framework import serializers
from systemnotebook.models.system_note_model import SystemNote
from django.utils import timezone

class SystemNoteSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)

    class Meta:
        model = SystemNote
        fields = [
            'id',
            'title',
            'content',
            'source',
            'source_display',
            'created_by',
            'created_by_email',  # Doğru olan bu
            'created_at'
        ]
        read_only_fields = ('created_by', 'created_at')

    def create(self, validated_data):
        if 'created_at' not in validated_data or validated_data['created_at'] is None:
            validated_data['created_at'] = timezone.now()

        # Kullanıcıyı backend'de set et
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user

        return super().create(validated_data)