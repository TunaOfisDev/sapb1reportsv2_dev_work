# backend/report_orchestrator/admin/__init__.py

from .api_report_admin import APIReportModelAdmin
from .api_execution_log_admin import APIExecutionLogAdmin

__all__ = [
    "APIReportModelAdmin",
    "APIExecutionLogAdmin",
]
