# backend/taskorchestrator/utils/dispatcher.py

from taskorchestrator.models.scheduled_task import ScheduledTask
from django.utils.module_loading import import_string
from taskorchestrator.utils.logger_config import logger  # 🔥 Merkezi logger kullanımı


def run_task(task_id: int) -> None:
    """
    ScheduledTask ID'si verilen görevi çalıştırır.
    İlgili TaskDefinition.function_path import edilir ve parametrik şekilde çağrılır.
    Sadece hata durumları loglanır.
    """
    try:
        task = ScheduledTask.objects.get(id=task_id)

        if not task.enabled:
            return  # Pasif görevse sessiz çık

        func_path = task.task.function_path
        func = import_string(func_path)

        func(**task.parameters)

    except ScheduledTask.DoesNotExist:
        logger.error(f"❌ ScheduledTask bulunamadı (id={task_id})")

    except Exception as e:
        logger.exception(f"🔥 Görev çalıştırılırken hata oluştu (id={task_id}): {str(e)}")
