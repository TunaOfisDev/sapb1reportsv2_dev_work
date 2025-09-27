# backend/taskorchestrator/api/views/task_definition_view.py

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from taskorchestrator.models.task_definition import TaskDefinition
from taskorchestrator.serializers.task_definition_serializer import TaskDefinitionSerializer


class TaskDefinitionViewSet(ModelViewSet):
    """
    TaskDefinition CRUD API endpoint'i.
    Sadece admin erişebilir.
    """
    queryset = TaskDefinition.objects.all()
    serializer_class = TaskDefinitionSerializer
    permission_classes = [IsAdminUser]
