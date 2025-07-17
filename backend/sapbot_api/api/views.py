# backend/sapbot_api/api/views.py
"""API view'lari"""

from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from ..models import DocumentSource,  ChatConversation, ChatMessage
from .serializers import (
    DocumentSourceSerializer,
 
    ChatConversationSerializer,
    ChatMessageSerializer,
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .pagination import StandardResultsSetPagination
from .filters import DocumentSourceFilter, ChatMessageFilter
from ..throttling  import ChatRateThrottle


class DocumentSourceListCreateView(generics.ListCreateAPIView):
    queryset = DocumentSource.objects.all().order_by("-created_at")
    serializer_class = DocumentSourceSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filterset_class = DocumentSourceFilter


class DocumentSourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DocumentSource.objects.all()
    serializer_class = DocumentSourceSerializer
    permission_classes = [IsAdminOrReadOnly]


class ChatConversationListCreateView(generics.ListCreateAPIView):
    queryset = ChatConversation.objects.all().order_by("-created_at")
    serializer_class = ChatConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user_type"]


class ChatMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filterset_class = ChatMessageFilter
    throttle_classes = [ChatRateThrottle]

    def get_queryset(self):
        conversation_id = self.kwargs.get("conversation_id")
        qs = ChatMessage.objects.all().order_by("created_at")
        if conversation_id:
            qs = qs.filter(conversation_id=conversation_id)
        return qs

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get("conversation_id")
        conversation = get_object_or_404(ChatConversation, id=conversation_id)
        serializer.save(conversation=conversation)


class ChatMessageDetailView(generics.RetrieveAPIView):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
 
