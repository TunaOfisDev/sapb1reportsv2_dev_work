# backend/report_orchestrator/apps.py

from django.apps import AppConfig

class ReportOrchestratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'report_orchestrator'

    def ready(self):
        import report_orchestrator.tasks.run_report
        import report_orchestrator.tasks.run_all_reports

