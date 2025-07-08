# backend/taskorchestrator/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from taskorchestrator.api.views.scheduled_task_view import ScheduledTaskViewSet
from taskorchestrator.api.views.task_definition_view import TaskDefinitionViewSet
from taskorchestrator.api.views.task_launcher_view import TaskLauncherView

app_name = "taskorchestrator"

router = DefaultRouter()
router.register(r'scheduled-task', ScheduledTaskViewSet, basename='scheduled-task')
router.register(r'task-definition', TaskDefinitionViewSet, basename='task-definition')

urlpatterns = [
    path('', include(router.urls)),
    path('launch-task/', TaskLauncherView.as_view(), name='launch-task'),
]
