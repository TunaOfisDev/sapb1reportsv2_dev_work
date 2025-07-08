# backend/eduvideo/serializers.py
from rest_framework import serializers
from .models.models import EduVideo

class EduVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EduVideo
        fields = ['id', 'title', 'description', 'thumbnail_url' ,'video_url', 'published_at', 'created_at', 'updated_at']
