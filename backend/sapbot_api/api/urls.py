# backend/sapbot_api/api/urls.py

from django.urls import path

from .views import (
    DocumentSourceListCreateView,
    DocumentSourceDetailView,
    ChatConversationListCreateView,
    ChatMessageListCreateView,
    ChatMessageDetailView,
)

app_name = "sapbot_api"

urlpatterns = [
    path("documents/", DocumentSourceListCreateView.as_view(), name="document-list"),
    path("documents/<uuid:pk>/", DocumentSourceDetailView.as_view(), name="document-detail"),
    path("conversations/", ChatConversationListCreateView.as_view(), name="conversation-list"),
    path(
        "conversations/<uuid:conversation_id>/messages/",
        ChatMessageListCreateView.as_view(),
        name="conversation-messages",
    ),
    path("messages/<uuid:pk>/", ChatMessageDetailView.as_view(), name="message-detail"),
]
 
