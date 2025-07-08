# backend/systemnotebook/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from systemnotebook.api.views.system_note_view import SystemNoteViewSet, GitHubSyncView

app_name = 'systemnotebook_api'

router = DefaultRouter()
router.register(r'system-notes', SystemNoteViewSet, basename='systemnote')

urlpatterns = [
    path('', include(router.urls)),
    path('github-sync/', GitHubSyncView.as_view(), name='github_sync'),
]
