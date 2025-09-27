# backend/systemnotebook/api/views/system_note_view.py

from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from systemnotebook.models.system_note_model import SystemNote
from systemnotebook.api.serializers.system_note_serializer import SystemNoteSerializer
from systemnotebook.filters.system_note_filter import SystemNoteFilter

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from systemnotebook.tasks.github_tasks import import_github_commits_task


class SystemNoteViewSet(viewsets.ModelViewSet):
    """
    Sistem notları için tam CRUD desteği sağlar.
    - Listeleme ve görüntüleme: Tüm authenticated kullanıcılar
    - Ekleme, güncelleme, silme: Sadece admin kullanıcılar
    """
    queryset = SystemNote.objects.select_related('created_by')
    serializer_class = SystemNoteSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = SystemNoteFilter
    search_fields = ['title', 'content', 'created_by__username']
    ordering_fields = ['created_at', 'source']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class GitHubSyncView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        import_github_commits_task.delay()
        return Response({"message": "GitHub commit senkronizasyonu başlatıldı."}, status=status.HTTP_202_ACCEPTED)
