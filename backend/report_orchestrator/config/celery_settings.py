# File: backend/report_orchestrator/config/celery_settings.py

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Günlük İlk 20 Müşteri Bakiyesi Raporu
    "daily_top20_customer_balance_mail": {
        "task": "report_orchestrator.tasks.run_report",
        "schedule": crontab(minute=0, hour=9, day_of_week='1-6'),  # Pazartesi-Cumartesi 16:00
        "args": ("customer_balance_top20",)
    },

    # Günlük Sofitel Müşteri Bakiye Raporu
    "daily_sofitel_balance_mail": {
        "task": "report_orchestrator.tasks.run_report",
        "schedule": crontab(minute=5, hour=9, day_of_week='1-6'),  # Pazartesi-Cumartesi 15:00
        "args": ("sofitel_balance_report",)
    },

    # Günlük Sofitel Tedarikçi Bakiye Raporu
    "daily_sofitel_supplier_balance_mail": {
        "task": "report_orchestrator.tasks.run_report",
        "schedule": crontab(minute=10, hour=9, day_of_week='1-6'),  # Pazartesi-Cumartesi 15:00
        "args": ("sofitel_supplier_balance_report",)
    },
}
