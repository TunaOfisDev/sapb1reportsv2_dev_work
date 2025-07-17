# backend/sapbot_api/api/serializers.py

from rest_framework import serializers

from ..models import (
    DocumentSource,
    KnowledgeChunk,
    ChatConversation,
    ChatMessage,
)


class DocumentSourceSerializer(serializers.ModelSerializer):
    """Döküman serializer"""

    class Meta:
        model = DocumentSource
        fields = [
            "id",
            "title",
            "document_type",
            "language",
            "processing_status",
            "uploaded_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class KnowledgeChunkSerializer(serializers.ModelSerializer):
    """Chunk serializer"""

    class Meta:
        model = KnowledgeChunk
        fields = [
            "id",
            "source",
            "content",
            "sap_module",
            "technical_level",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ChatConversationSerializer(serializers.ModelSerializer):
    """Konusma serializer"""

    class Meta:
        model = ChatConversation
        fields = [
            "id",
            "user",
            "session_id",
            "user_type",
            "last_activity",
        ]
        read_only_fields = ["id", "last_activity"]


class ChatMessageSerializer(serializers.ModelSerializer):
    """Mesaj serializer"""

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "conversation",
            "message_type",
            "content",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
 
