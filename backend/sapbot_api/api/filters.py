# backend/sapbot_api/api/filters.py

import django_filters as filters

from ..models import DocumentSource, KnowledgeChunk, ChatMessage


class DocumentSourceFilter(filters.FilterSet):
    """Döküman filtreleri"""

    class Meta:
        model = DocumentSource
        fields = {
            "document_type": ["exact"],
            "language": ["exact"],
            "processing_status": ["exact"],
            "is_public": ["exact"],
        }


class KnowledgeChunkFilter(filters.FilterSet):
    """Chunk filtreleri"""

    class Meta:
        model = KnowledgeChunk
        fields = {
            "sap_module": ["exact"],
            "technical_level": ["exact"],
            "is_verified": ["exact"],
        }


class ChatMessageFilter(filters.FilterSet):
    """Chat mesaj filtreleri"""

    conversation = filters.UUIDFilter(field_name="conversation_id")

    class Meta:
        model = ChatMessage
        fields = {
            "message_type": ["exact"],
        }
