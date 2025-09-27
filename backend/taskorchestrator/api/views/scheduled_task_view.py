# backend/taskorchestrator/api/views/scheduled_task_view.py

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from taskorchestrator.models.scheduled_task import ScheduledTask
from taskorchestrator.serializers.scheduled_task_serializer import ScheduledTaskSerializer


class ScheduledTaskViewSet(ModelViewSet):
    """
    ScheduledTask CRUD API endpoint'i.
    Sadece admin kullanıcılar erişebilir.
    """
    queryset = ScheduledTask.objects.select_related("task", "crontab").all()
    serializer_class = ScheduledTaskSerializer
    permission_classes = [IsAdminUser]
