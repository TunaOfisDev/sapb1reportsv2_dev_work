# backend/taskorchestrator/api/views/task_launcher_view.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from taskorchestrator.models.scheduled_task import ScheduledTask
from taskorchestrator.tasks import run_scheduled_task
from taskorchestrator.utils.logger_config import logger  # 🔥 Merkezi loglama


class TaskLauncherView(APIView):
    """
    Tekil bir ScheduledTask'i manuel olarak tetikleyen endpoint.
    POST ile task_id gönderilmelidir.
    """

    def post(self, request, *args, **kwargs):
        task_id = request.data.get("task_id")

        if not task_id:
            return Response(
                {"detail": "task_id alanı zorunludur."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            task = ScheduledTask.objects.get(id=task_id)

            if not task.enabled:
                return Response(
                    {"detail": "Görev pasif durumda, çalıştırılamaz."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            run_scheduled_task.delay(task.id)

            return Response(
                {"detail": f"{task.name} görevi kuyruğa eklendi."},
                status=status.HTTP_200_OK
            )

        except ScheduledTask.DoesNotExist:
            logger.error(f"❌ Task ID bulunamadı: {task_id}")
            return Response(
                {"detail": "Belirtilen ID ile görev bulunamadı."},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.exception(f"🔥 Task tetikleme hatası: {str(e)}")
            return Response(
                {"detail": "Görev tetiklenirken sistemsel hata oluştu."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
